import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from bs4 import BeautifulSoup
import json
from gspread_dataframe import get_as_dataframe
from utils.gsheet_utils import export_to_sheets


def parse_job_card_indeed(job_card_soup):
    """
    Parses a BeautifulSoup object representing a single job card from Indeed,
    aiming to replicate the output of the R function 'get_indeed'.
    Returns a single-row pandas DataFrame.

    Args:
        job_card_soup (BeautifulSoup Tag): The BeautifulSoup Tag object
        for a job card.

    Returns:
        pandas.DataFrame: A single-row DataFrame containing extracted
        job information.
    """
    job_data = {
        'source': "indeed",
        'job_id': None,
        'job_url': None,
        'job_title': None,
        'job_company': None,
        'job_location': None,
        'job_salary': None,
        'employment_type': None,
        'job_list_date': None  # Storing as datetime object, can be formatted
    }

    # Job Title (R: html_element("h2") %>% html_text2())
    try:
        title_element = job_card_soup.select_one(
            "h2.jobTitle a span[title], h2.jobTitle span, h2.jobTitle a"
            )
        if not title_element:
            title_element = job_card_soup.select_one("h2")
        if title_element:
            job_data['job_title'] = title_element.get_text(strip=True)
            if not job_data['job_title'] and title_element.get('title'):
                job_data['job_title'] = title_element.get('title').strip()
            if job_data['job_title'] == "":
                job_data['job_title'] = None
    except Exception as e:
        print(f"Error parsing job_title: {e}")
        pass

    # Job ID (R: html_element("a") %>% html_attr("data-jk"))
    try:
        link_with_jk = job_card_soup.select_one(
            "h2 a[data-jk], a.jcs-JobTitle[data-jk]")
        if link_with_jk:
            job_data['job_id'] = link_with_jk.get('data-jk')
        else:
            if job_card_soup.name == 'a' and job_card_soup.get('data-jk'):
                job_data['job_id'] = job_card_soup.get('data-jk')
            elif job_card_soup.get('data-jk'):
                job_data['job_id'] = job_card_soup.get('data-jk')
            else:
                first_a_with_jk = job_card_soup.select_one("a[data-jk]")
                if first_a_with_jk:
                    job_data['job_id'] = first_a_with_jk.get('data-jk')
    except Exception as e:
        print(f"Error parsing job_id: {e}")
        pass

    # Job URL (R: glue("https://id.indeed.com/viewjob?jk={job_id}"))
    if job_data['job_id']:
        job_data['job_url'] = f"https://id.indeed.com/viewjob?jk="\
            f"{job_data['job_id']}"
    else:
        try:
            title_link_element = job_card_soup.select_one(
                "h2.jobTitle > a[href], a.jcs-JobTitle[href]")
            if title_link_element:
                job_link = title_link_element.get('href')
                if job_link:
                    if job_link.startswith('/'):
                        job_data['job_url'] = "https://id.indeed.com" \
                            + job_link
                    else:
                        job_data['job_url'] = job_link
        except Exception as e:
            print("Error getting job_url", e)
            pass

    # Job Company
    try:
        company_element = job_card_soup.select_one(
            "div[class*='company'] span[class*='Name'], span.companyName,"
            " span[data-testid='company-name']"
        )
        if company_element:
            job_data['job_company'] = company_element.get_text(strip=True)
    except Exception as e:
        print(f"Error parsing job_company: {e}")
        pass

    # Job Location
    try:
        location_element = job_card_soup.select_one(
            "div[class*='company'] div[class*='Location'], "
            "div.companyLocation, div[data-testid='text-location']"
        )
        if location_element:
            location_text = location_element.get_text(strip=True)
            job_data['job_location'] = re.sub(r"\+.*", "", location_text)\
                .strip()
    except Exception as e:
        print(f"Error parsing job_location: {e}")
        pass

    # Job Salary
    try:
        salary_element = job_card_soup.select_one(
            "div[class*='salaryContainer'] div[class*='salary'], "
            "div.salary-snippet-container div.salaryText, "
            "div.metadata.salary-snippet-container, "
            "div[class*='salary']"
        )
        if salary_element:
            salary_text = salary_element.get_text(strip=True)
            salary_text = salary_text.split(" per", 1)[0]
            salary_text = salary_text.replace("Rp. ", "IDR")
            salary_text = salary_text.replace(".", ",")
            job_data['job_salary'] = salary_text.strip()
    except Exception as e:
        print(f"Error parsing job_salary: {e}")
        pass

    # Employment Type
    try:
        attribute_elements = job_card_soup.select_one("div.jobMetaDataGroup")\
            .select_one("ul").select_one("li")
        if attribute_elements:
            potential_employment_type = None
            for el in attribute_elements:
                elem_text = el.get_text(strip=True)
                # Heuristic: not salary, not location, short, and no digits
                is_salary = job_data['job_salary'] and job_data['job_salary'] \
                    in elem_text
                is_location = job_data['job_location'] and \
                    job_data['job_location'] in elem_text

                if elem_text and not is_salary and not is_location:
                    if not (re.search(r"[0-9]", elem_text) and
                            not ("IDR" in elem_text or "$" in elem_text
                                 or "Rp" in elem_text)):
                        if len(elem_text.split()) < 4:
                            potential_employment_type = elem_text

            if potential_employment_type:
                type_text = re.sub(r"\+.*", "", potential_employment_type)\
                    .strip()
                if not re.search(r"\d", type_text) or any(
                        kw in type_text for kw in [
                            "Full-time", "Part-time", "Contract", "Temporary",
                            "Internship"]):
                    job_data['employment_type'] = type_text
    except Exception as e:
        print(f"Error parsing employment_type: {e}")
        pass

    # Posted Ago / Job List Date
    try:
        date_element = job_card_soup.select_one(
            "table[class*='jobCardShelfContainer'] span[class*='date'], "
            "span.date"
        )
        if date_element:
            posted_ago_raw = date_element.get_text(strip=True)
            posted_ago_text = re.sub(
                r"^(?:Active|Posted|Diiklankan|Diposkan)\s*",
                "", posted_ago_raw, flags=re.IGNORECASE).strip()

            current_date = datetime.today().date()

            if "30+" in posted_ago_text or "30 hari lalu" in posted_ago_text\
                    .lower():
                first_day_current_month = current_date.replace(day=1)
                job_data['job_list_date'] = first_day_current_month - \
                    relativedelta(months=1)
            elif "just posted" in posted_ago_text.lower() or \
                 "baru saja" in posted_ago_text.lower() or \
                 "hari ini" in posted_ago_text.lower() or \
                 "today" in posted_ago_text.lower():
                job_data['job_list_date'] = current_date
            else:
                days_match = re.search(r"(\d+)\s*(?:hari|day|days)",
                                       posted_ago_text, flags=re.IGNORECASE)
                if days_match:
                    days_ago = int(days_match.group(1))
                    job_data['job_list_date'] = current_date \
                        - timedelta(days=days_ago)
    except Exception as e:
        print(f"Error parsing job_list_date: {e}")
        pass

    return pd.DataFrame([job_data])


def get_job_from_indeed_url(url, sb):
    print(f'Getting job from {url}')
    # sb.open(url)
    sb.driver.uc_open_with_reconnect(url,
                                     reconnect_time=3)
    sb.uc_gui_handle_cf()
    sb.uc_gui_click_cf()
    sb.sleep(3)
    # last_height = sb.execute_script("return document.body.scrollHeight")

    # Scrape the first page
    page_source = sb.get_page_source()
    # print("page source")
    # print(page_source)
    soup = BeautifulSoup(page_source, 'html.parser')

    # Common selectors for job cards on Indeed. Adjust if necessary.
    # The R code uses "ul[class *= 'Results'] > li > div[class *= 'card']"
    job_card_selector = "div.result"
    job_cards_initial = soup.select(job_card_selector)

    all_jobs_df = []
    print(f"Found {len(job_cards_initial)} job cards on the first page.")
    try:
        for card_soup in job_cards_initial:
            job_info_df = parse_job_card_indeed(card_soup)
            # Correctly check if the DataFrame is not None and not empty
            if job_info_df is not None and not job_info_df.empty:
                if job_info_df.iloc[0]['job_title'] is not None:
                    all_jobs_df.append(job_info_df)

        if len(all_jobs_df) > 0:
            all_jobs_df = pd.concat(all_jobs_df, ignore_index=True)

        print("All Jobs Df:")
        print(all_jobs_df)
        return all_jobs_df
    except Exception as e:
        print("Error", e)
        return None


def enrich_indeed(job_info_series: pd.Series, spreadsheet, sb):
    """
    Enriches a single job's information by visiting its Indeed page.

    Args:
        job_info_series (pd.Series): A pandas Series containing initial job
        information.
        Expected keys: 'job_url', 'job_title', 'job_company',
        'job_list_date', etc.
        sb: An initialized SeleniumBase driver instance.

    Returns:
        pandas.DataFrame: A single-row DataFrame with enriched job information.
    """
    # Initialize a dictionary from the input series to store all data
    # Ensure all expected final columns are present, defaulting to None
    # Define the order of columns for the final DataFrame
    FINAL_COLUMN_ORDER = [
        "source", "job_id", "job_url", "job_title", "job_company",
        "job_location", "job_salary", "job_list_date", "seniority_level",
        "employment_type", "industries", "job_description", "applicant",
        "get_time"
    ]

    result_data = {col: job_info_series.get(col) for col in FINAL_COLUMN_ORDER}
    result_data.update(job_info_series.to_dict())

    # Set default values for fields to be enriched if not already present
    result_data.setdefault('seniority_level', None)
    result_data.setdefault('industries', None)
    result_data.setdefault('job_description', None)
    result_data.setdefault('applicant', None)
    result_data['get_time'] = datetime.now()

    url = result_data.get('job_url')
    job_title_display = result_data.get('job_title', 'N/A')
    job_company_display = result_data.get('job_company', 'N/A')

    print(f"Getting Job Details for {job_title_display}"
          f"- {job_company_display} (URL: {url})")

    if not url:
        print("Error: Job URL is missing.")
        # Ensure all columns are present before returning
        for col in FINAL_COLUMN_ORDER:
            result_data.setdefault(col, None)
        return pd.DataFrame([result_data])[FINAL_COLUMN_ORDER]

    try:
        sb.open(url)
        sb.sleep(3)
    except Exception as e:
        print(f"Error navigating to {url}: {e}")
        # Ensure all columns are present before returning
        for col in FINAL_COLUMN_ORDER:
            result_data.setdefault(col, None)
        result_data['get_time'] = datetime.now()
        return pd.DataFrame([result_data])[FINAL_COLUMN_ORDER]

    page_source = sb.get_page_source()
    soup = BeautifulSoup(page_source, 'html.parser')

    # --- Job Description ---
    try:
        description_element = soup.select_one("div#jobDescriptionText")
        if description_element:
            desc_html = str(description_element)

            # R: str_remove_all("\n|\t")
            desc_text = re.sub(r'\n|\t', '', desc_html)
            # R: str_replace_all('[\"]', "'")
            desc_text = re.sub(r'\"', "'", desc_text)
            # R: str_squish()
            desc_text = " ".join(desc_text.split()).strip()

            # R: str_replace_all("<p><br></p>", "\n\n")
            desc_text = re.sub(r"<p><br\s*/?></p>", "\n\n", desc_text,
                               flags=re.IGNORECASE)
            # R: str_replace_all("</ul>", "\n\n")
            desc_text = re.sub(r"</ul>", "\n\n", desc_text,
                               flags=re.IGNORECASE)

            # R: str_replace_all("<(h[1-9]).*?>", "<strong>")
            desc_text = re.sub(r"<h[1-9][^>]*>", "<strong>", desc_text,
                               flags=re.IGNORECASE)
            # R: str_replace_all("</(h[1-9])>", "</strong>")
            desc_text = re.sub(r"</h[1-9]>", "</strong>", desc_text,
                               flags=re.IGNORECASE)

            tags_to_remove_pattern = (
                r"<div[^>]*>|<div>|</div>|<ul[^>]*>|<ul>|"
                r"</li>|</p>|</ol>|<br\s*/?>|<span[^>]*>|<span>|</span>"
            )
            desc_text = re.sub(tags_to_remove_pattern, "", desc_text,
                               flags=re.IGNORECASE)

            # R: str_replace_all("<p>|<ol>|<br>", "\n\n")
            desc_text = re.sub(r"<p>|<ol>", "\n\n", desc_text,
                               flags=re.IGNORECASE)

            # R: str_replace_all("<li>|<li.*?>", "\n • ")
            desc_text = re.sub(r"<li[^>]*>", "\n • ", desc_text,
                               flags=re.IGNORECASE)

            # R: str_replace_all("\\n\\s+\\n", "\n\n")
            desc_text = re.sub(r"\n\s+\n", "\n\n", desc_text)
            desc_text = re.sub(r"\n\n<strong>\n\n", "<strong>\n\n", desc_text,
                               flags=re.IGNORECASE)

            # R: str_remove_all("•  \n|• \n|• \n\n")
            desc_text = re.sub(r"•\s*\n(\s*\n)?", "• ", desc_text)

            # R: str_replace_all("  •", " •")
            desc_text = re.sub(r"\s+•", " •", desc_text)
            # R: str_replace_all("(\n{2})\n+", "\n\n")
            desc_text = re.sub(r"(\n\s*){2,}", "\n\n", desc_text)
            # R: str_replace_all("\n\n</strong>\n", "\n</strong>\n")
            desc_text = re.sub(r"\n\n</strong>\n", "\n</strong>\n", desc_text,
                               flags=re.IGNORECASE)

            result_data['job_description'] = desc_text.strip() \
                if desc_text else None
        else:
            result_data['job_description'] = None
    except Exception as e:
        print(f"Error parsing job description: {e}")
        result_data['job_description'] = None

    # --- Update job_list_date from script tag (JSON-LD) ---
    new_job_list_date_parsed = None
    try:
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            if script.string:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, list):
                        json_data = json_data[0] if json_data else {}

                    if json_data.get('@type') == 'JobPosting' and \
                            'datePosted' in json_data:
                        date_posted_value = json_data['datePosted']

                        if isinstance(date_posted_value, str):
                            new_job_list_date_parsed = datetime.strptime(
                                date_posted_value,
                                '%Y-%m-%dT%H:%M:%S.%fZ').date()
                        elif isinstance(date_posted_value, (int, float)):
                            new_job_list_date_parsed = datetime.fromtimestamp(
                                date_posted_value / 1000).date()
                        break
                except json.JSONDecodeError:
                    continue
                except (TypeError, ValueError) as date_err:
                    print(f"Error parsing datePosted value"
                          f"'{json_data.get('datePosted')}': {date_err}")
                    continue
    except Exception as e:
        print(f"Error extracting new_job_list_date from script: {e}")

    if new_job_list_date_parsed:
        result_data['job_list_date'] = new_job_list_date_parsed

    # --- Industries Logic ---
    current_company_name = result_data.get('job_company')
    current_industries = result_data.get('industries')

    indeed_industry_sheet = spreadsheet.worksheet('Industry Indeed')
    company_industry_df = get_as_dataframe(indeed_industry_sheet)

    if current_company_name and company_industry_df is not None:
        # Try to find industry in the loaded CSV
        matched_company = company_industry_df[
            company_industry_df['job_company'] == current_company_name]
        if not matched_company.empty and pd.notna(
                matched_company['industries'].iloc[0]):
            current_industries = matched_company['industries'].iloc[0]
            print(f"Found industry for {current_company_name}"
                  f"in CSV: {current_industries}")
        else:
            current_industries = None

    if pd.isna(current_industries) and current_company_name:
        print(f"Industry for {current_company_name} not in CSV or is NA."
              f" Attempting to scrape.")
        new_scraped_industries = "Not Available"
        try:
            # R: html_element("div[data-company-name *= 'true'] > a")
            company_link_element = soup.select_one(
                "div[data-company-name*='true']").select_one('a')
            # print(company_link_element)
            if company_link_element:
                company_page_url = company_link_element.get('href')
                if company_page_url:
                    if not company_page_url.startswith('http'):
                        # Attempt to construct absolute URL if relative
                        from urllib.parse import urljoin
                        company_page_url = urljoin(sb.get_current_url(),
                                                   company_page_url)

                    print(f"Navigating to company page: {company_page_url}")
                    sb.open(company_page_url)
                    sb.uc_gui_handle_cf()
                    sb.sleep(3)
                    company_page_source = sb.get_page_source()
                    company_soup = BeautifulSoup(company_page_source,
                                                 'html.parser')

                    industry_li = company_soup.\
                        select_one("li[data-testid*='industry']")
                    if industry_li:
                        industry_divs = industry_li.select("div")
                        if industry_divs:
                            new_scraped_industries = industry_divs[-1]\
                                .get_text(strip=True)
                            if not new_scraped_industries:
                                new_scraped_industries = "Not Available"

                    print(f"Scraped industry for {current_company_name}:"
                          f" {new_scraped_industries}")

                    new_entry_df = pd.DataFrame(
                        [{'job_company': current_company_name,
                            'industries': new_scraped_industries}])
                    try:
                        export_to_sheets(spreadsheet=spreadsheet,
                                         sheet_name='Industry Indeed',
                                         df=new_entry_df, mode='a')
                        print("Appended to sheet")
                    except Exception as e:
                        print(f"Error writing to sheet {e}")

                    # if new_scraped_industries != "Not Available":
                    #     new_entry_df = pd.DataFrame(
                    #         [{'job_company': current_company_name,
                    #           'industries': new_scraped_industries}])
                    #     try:
                    #         export_to_sheets(spreadsheet=spreadsheet,
                    #                          sheet_name='Industry Indeed',
                    #                          df=new_entry_df, mode='a')
                    #         print("Appended to sheet")
                    #     except Exception as e:
                    #         print(f"Error writing to sheet {e}")

                    print(f"Navigating back to original job URL: {url}")
                    sb.open(url)
                    sb.sleep(1)

            current_industries = new_scraped_industries
        except Exception as e_scrape_ind:
            print(f"Error scraping industry for {current_company_name}:"
                  f" {e_scrape_ind}")
            current_industries = "Not Available"

    result_data['industries'] = current_industries \
        if pd.notna(current_industries) else None

    result_data['get_time'] = datetime.now()

    # Create DataFrame with the specified column order
    final_df = pd.DataFrame([result_data])

    for col in FINAL_COLUMN_ORDER:
        if col not in final_df.columns:
            final_df[col] = None

    return final_df[FINAL_COLUMN_ORDER]
