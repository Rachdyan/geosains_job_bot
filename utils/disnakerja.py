import cloudscraper
from bs4 import BeautifulSoup, Tag
import pandas as pd
from datetime import datetime
import re
import time


def parse_disnakerja(job_card_soup: BeautifulSoup, industries: str):
    """
    Parses a BeautifulSoup Tag object representing a single job card
    from Disnakerja.

    Args:
        job_card_soup: The BeautifulSoup Tag object for a job card.
        industries (str): The industries string to associate with this job.

    Returns:
        pandas.DataFrame: A single-row DataFrame containing extracted job
        information.
    """
    source = "disnakerja"
    job_id = None
    job_url = None
    job_company = None
    # job_title is not extracted in the R function from all_jobs_page,
    # it seems to be expected to be part of the input df in the enricher.
    # For a parser, we'd typically try to get it if available.
    # However, to match R, we'll omit direct title extraction here.

    # Extract job_id
    # R: html_attr("id") %>% str_after_first("-")
    try:
        raw_id = job_card_soup.get('id')
        if raw_id and isinstance(raw_id, str) and '-' in raw_id:
            job_id = raw_id.split('-', 1)[1]
        elif raw_id:
            job_id = raw_id
    except Exception as e:
        print(f"Error extracting job_id: {e}")
        job_id = None

    # Extract job_url and job_company from the first <a> tag
    # R: html_element("a")
    first_a_tag = None
    try:
        first_a_tag = job_card_soup.find('a')
    except Exception as e:
        print(f"Error finding 'a' tag: {e}")

    if first_a_tag:
        # Extract job_url
        # R: html_attr("href")
        try:
            job_url = first_a_tag.get('href')
            if not job_url or not job_url.strip():
                job_url = None
        except Exception as e:
            print(f"Error extracting job_url: {e}")
            job_url = None

        # Extract job_company
        # R: html_attr("title")
        try:
            job_company = first_a_tag.get('title')
            if not job_company or not job_company.strip():
                job_company = None
        except Exception as e:
            print(f"Error extracting job_company: {e}")
            job_company = None
    else:
        job_url = None
        job_company = None

    job_data = {
        'source': source,
        'job_id': job_id,
        'job_url': job_url,
        'job_company': job_company,
        'industries': industries,
        # Add other fields if they were part of the input or extracted
        # 'job_title': None, # Example if title were to be included
    }

    return pd.DataFrame([job_data])


def get_job_from_disnakerja_url(url, industry,
                                proxy_string=None):
    print(f'Getting job from {url}')

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://www.disnakerja.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.disnakerja.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/136.0.0.0 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", '
        '"Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    proxies_dict = None
    if proxy_string:
        proxies_dict = {
            'http': proxy_string,
            'https': proxy_string  # Assuming the same proxy for http and https
        }

    scraper = cloudscraper.create_scraper()
    response = scraper.get(
        url=url,
        # cookies=cookies,
        headers=headers,
        proxies=proxies_dict
    )

    soup = BeautifulSoup(response.text, 'html.parser')

    # Common selectors for job cards on Indeed. Adjust if necessary.
    # The R code uses "ul[class *= 'Results'] > li > div[class *= 'card']"

    # Dapatkan total hasil pencarian
    # Dapatkan elemen job card
    job_cards = soup.select_one("div[id *= 'site-container']")\
        .select_one("div[id *= 'primary'] > div")\
        .select_one("main > div").select("article")

    all_jobs_df = []
    print(f"Found {len(job_cards)} job cards on the first page.")
    try:
        for job_card in job_cards:
            job_info_df = parse_disnakerja(job_card, industries=industry)
            # Correctly check if the DataFrame is not None and not empty
            if job_info_df is not None and not job_info_df.empty:
                if job_info_df.iloc[0]['job_id'] is not None:
                    all_jobs_df.append(job_info_df)

        if len(all_jobs_df) > 0:
            all_jobs_df = pd.concat(all_jobs_df, ignore_index=True)

        print("All Jobs Df:")
        print(all_jobs_df)
        return all_jobs_df
    except Exception as e:
        print("Error", e)
        return None


def is_value_empty(value):
    """Checks if a value is None, NaN, or an empty string/list."""
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, list) and not value:
        return True
    return False


def enrich_disnakerja(job_info_series: pd.Series,
                      proxy_string=None):
    """
    Enriches a single job's information by visiting its Disnakerja page.

    Args:
        job_info_series (pd.Series): A pandas Series containing initial
        job information.
        Expected keys: 'job_url', 'job_company', etc.
        The 'job_title' from this input will be overridden.

    Returns:
        pandas.DataFrame: A single-row DataFrame with enriched job information.
    """

    FINAL_COLUMN_ORDER_DISNAKERJA = [
        "source", "job_id", "job_url", "job_title", "job_company",
        "job_location", "job_salary", "job_list_date", "seniority_level",
        "employment_type", "industries", "job_description", "applicant",
        "get_time"
    ]
    # Initialize result_data with values from input job_info_series,
    # then override/add new fields.
    result_data = {col: job_info_series.get(col)
                   for col in FINAL_COLUMN_ORDER_DISNAKERJA}
    result_data.update(job_info_series.to_dict())

    # Fields to be extracted or defaulted
    result_data['job_title'] = None
    result_data['job_location'] = None
    result_data['employment_type'] = None
    result_data['seniority_level'] = None
    result_data['job_list_date'] = None
    result_data['job_description'] = None
    result_data['job_salary'] = None
    result_data['applicant'] = None
    result_data['get_time'] = datetime.now()

    url = job_info_series.get('job_url')
    job_company_display = job_info_series.get('job_company', 'N/A')

    print(f"Getting Job Details for {job_company_display}"
          f" from Disnakerja - {url}")

    if not url:
        print("Error: Job URL is missing for Disnakerja processing.")
        result_data['job_description'] = "Job URL missing"
        for col in FINAL_COLUMN_ORDER_DISNAKERJA:
            result_data.setdefault(col, None)
        return pd.DataFrame([result_data])[FINAL_COLUMN_ORDER_DISNAKERJA]

    time.sleep(1)

    proxies_dict = None
    if proxy_string:
        proxies_dict = {
            'http': proxy_string,
            'https': proxy_string  # Assuming the same proxy for http and https
        }
    page_soup = None
    error_message_http = None
    scraper = cloudscraper.create_scraper()
    try:
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://www.disnakerja.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.disnakerja.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/136.0.0.0 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", '
            '"Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        response = scraper.get(url,
                               headers=headers,
                               proxies=proxies_dict,
                               timeout=15)
        response.raise_for_status()
        page_soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        error_message_http = str(e)
        print(f"Error fetching page {url}: {e}")

    if page_soup:
        # Job Title
        try:
            title_element = page_soup.select_one("div.entry-meta > span")
            if title_element:
                title_text = title_element.get_text(strip=True)
                result_data['job_title'] = f"{title_text} Posisi" \
                    if title_text else None
        except Exception as e_title:
            print(f"Error parsing job_title: {e_title}")
            pass

        # Specs Raw (List of <li> elements)
        specs_elements = []
        try:
            # R: html_element("div[id = 'specs'] > ul") %>% html_elements("li")
            specs_ul = page_soup.select_one("div#specs > ul")
            if specs_ul:
                specs_elements = specs_ul.find_all("li", recursive=False)
        except Exception as e_specs:
            print(f"Error parsing specs_raw: {e_specs}")

        if not specs_elements:
            print("Specs section (specs_raw) not found or empty.")

        # Job Location (from specs_elements[2] - 3rd li)
        try:
            if len(specs_elements) > 2:
                location_text = specs_elements[2].get_text(strip=True)
                location_text = location_text.replace("Lokasi:", "").strip()
                result_data['job_location'] = location_text \
                    if location_text else None
        except Exception as e_loc:
            print(f"Error parsing job_location: {e_loc}")
            pass

        # Employment Type (from specs_elements[3] - 4th li)
        try:
            if len(specs_elements) > 3:
                type_text = specs_elements[3].get_text(strip=True)
                type_text = type_text.replace("Tipe Pekerjaan:", "").strip()
                result_data['employment_type'] = type_text\
                    if type_text else None
        except Exception as e_emptype:
            print(f"Error parsing employment_type: {e_emptype}")
            pass

        # Seniority Level (from specs_elements[5] - 6th li)
        try:
            if len(specs_elements) > 5:
                level_text = specs_elements[5].get_text(strip=True)
                level_text = level_text.replace("Pengalaman:", "").strip()
                result_data['seniority_level'] = level_text\
                    if level_text else None
        except Exception as e_level:
            print(f"Error parsing seniority_level: {e_level}")
            pass

        # Job List Date (from specs_elements[0] - 1st li)
        try:
            if len(specs_elements) > 0:

                time_element = specs_elements[0]\
                    .select_one("time[itemprop='datePublished']")
                if time_element:
                    datetime_str = time_element.get('datetime')
                    if datetime_str:
                        parsed_date = datetime.fromisoformat(
                            datetime_str.replace("Z", "+00:00")).date()
                        result_data['job_list_date'] = parsed_date
        except Exception as e_date:
            print(f"Error parsing job_list_date: {e_date}")
            pass
        if is_value_empty(result_data['job_list_date']):
            result_data['job_list_date'] = None

        # Job Description
        description_html_parts = []
        try:
            description_container = page_soup.select_one("div#description")
            if description_container:
                children = [child for child in description_container.children
                            if isinstance(child, Tag)]
                if len(children) > 2 + 4:
                    description_elements_for_processing = children[2:-4]
                    description_html_parts = [
                        str(el) for el in description_elements_for_processing]
                elif children:
                    description_elements_for_processing = children
                    description_html_parts = [
                        str(el) for el in description_elements_for_processing]

        except Exception as e_desc_parts:
            print(f"Error selecting description parts: {e_desc_parts}")

        if description_html_parts:
            try:
                # R: as.character() %>% str_flatten()
                full_desc_html = "".join(description_html_parts)
                desc_text = full_desc_html
                desc_text = re.sub(r'\n|\t', '', desc_text)
                desc_text = re.sub(r'\"', "'", desc_text)
                desc_text = " ".join(desc_text.split()).strip()
                desc_text = re.sub(r"<p><br\s*/?></p>", "\n\n", desc_text,
                                   flags=re.IGNORECASE)
                desc_text = re.sub(r"</ul\s*>", "\n\n", desc_text,
                                   flags=re.IGNORECASE)
                desc_text = re.sub(r"<h[1-9][^>]*>", "<strong>", desc_text,
                                   flags=re.IGNORECASE)
                desc_text = re.sub(r"</h[1-9]>", "</strong>", desc_text,
                                   flags=re.IGNORECASE)

                # Extended remove pattern from R
                tags_to_remove_pattern_disnakerja = (
                    r"<div[^>]*>|<div>|</div>|<ul[^>]*>|<ul>|</li>|</p>|"
                    r"</ol>|<br\s*/?>|<span[^>]*>|<span>|</span>|"
                    r"<script[^>]*>.*?</script>|<ins[^>]*>.*?</ins>|<hr[^>]*>|"
                    r"<img[^>]*>|<noscript>.*?</noscript>|"
                    r"<iframe[^>]*>.*?</iframe>|<table[^>]*>.*?</table>|"
                    r"<tbody[^>]*>.*?</tbody>"
                )
                desc_text = re.sub(tags_to_remove_pattern_disnakerja, "",
                                   desc_text, flags=re.IGNORECASE | re.DOTALL)

                desc_text = desc_text.replace(
                    "(adsbygoogle = window.adsbygoogle || []).push({});", "")
                # R: str_remove_all("")
                desc_text = re.sub(r"", "", desc_text, flags=re.DOTALL)

                # R: str_replace_all("<tr>|</tr>|<td.*?>|</td>", "\n")
                desc_text = re.sub(r"</tr>|</td>", "\n", desc_text,
                                   flags=re.IGNORECASE)
                desc_text = re.sub(r"<tr>|<td[^>]*>", "\n", desc_text,
                                   flags=re.IGNORECASE)

                desc_text = re.sub(r"<p[^>]*>|<ol>", "\n\n", desc_text,
                                   flags=re.IGNORECASE)

                # R: str_replace_all("<li>|<li.*?>", "\n • ")
                desc_text = re.sub(r"<li[^>]*>", "\n • ", desc_text,
                                   flags=re.IGNORECASE)

                desc_text = re.sub(r"\n\s+\n", "\n\n", desc_text)
                desc_text = re.sub(r"\n\n<strong>\n\n", "<strong>\n\n",
                                   desc_text, flags=re.IGNORECASE)

                # R: str_remove_all("•  \n|• \n|• \n\n")
                desc_text = re.sub(r"•\s*\n(\s*\n)?", "• ", desc_text)

                desc_text = re.sub(r"\s+•", " •", desc_text)
                desc_text = re.sub(r"(\n\s*){2,}", "\n\n", desc_text)
                desc_text = re.sub(r"\n\n</strong>\n", "\n</strong>\n",
                                   desc_text, flags=re.IGNORECASE)

                result_data['job_description'] = desc_text.strip() \
                    if desc_text and desc_text.strip() else None
            except Exception as e_desc_clean:
                print(f"Error cleaning description: {e_desc_clean}")
                pass

        if is_value_empty(result_data['job_description']):
            result_data['job_description'] = None

        result_data['get_time'] = datetime.now()

    else:
        print(f"Failed to parse page {url}. Error: {error_message_http}")
        # Set multiple fields to the error message as per R logic's error case
        error_val_for_fields = error_message_http if error_message_http \
            else "Page fetch/parse failed"
        result_data['job_location'] = error_val_for_fields
        result_data['job_list_date'] = error_val_for_fields
        result_data['job_description'] = error_val_for_fields

        result_data['get_time'] = datetime.now()

    # Create final DataFrame with specified column order
    final_df = pd.DataFrame([result_data])
    for col in FINAL_COLUMN_ORDER_DISNAKERJA:
        if col not in final_df.columns:
            final_df[col] = None  # Ensure all columns exist

    return final_df[FINAL_COLUMN_ORDER_DISNAKERJA]
