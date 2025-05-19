import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import time
import requests
import random
import json


def parse_jobstreet(job_card):
    job_id = job_card.get('data-job-id')
    # Ekstrak judul pekerjaan
    title_tag = job_card.find('a', attrs={"data-automation": "jobTitle"})
    title = title_tag.get_text(strip=True) if title_tag else 'N/A'

    # Ekstrak nama perusahaan
    company_name_tag = job_card.find('a',
                                     attrs={"data-automation": "jobCompany"})
    company_name = company_name_tag.get_text(strip=True) \
        if company_name_tag else 'N/A'

    # Ekstrak gaji
    salary_tag = job_card.find('span', attrs={"data-automation": "jobSalary"})
    salary = salary_tag.get_text(strip=True) if salary_tag else 'N/A'

    # Ekstrak lokasi
    location_tags = job_card.find_all('a',
                                      attrs={"data-automation": "jobLocation"})
    location = ', '.join([tag.get_text(strip=True) for tag in location_tags]) \
        if location_tags else 'N/A'

    # Ekstrak link pekerjaan
    link_tag = job_card.find('a',
                             href=True, attrs={"data-automation": "jobTitle"})
    link = f"https://id.jobstreet.com{link_tag['href']}" if link_tag else 'N/A'

    result = ({
        'source': 'jobstreet',
        'job_id': job_id,
        'job_url': link,
        'job_title': title,
        'job_company': company_name,
        'job_location': location,
        'job_salary': salary,
        'job_list_date': None  # Storing as datetime object, can be formatted

    })

    return pd.DataFrame([result])


def get_job_from_jobstreet_url(url, proxy_string=None):
    print(f'Getting job from {url}')

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'origin': 'https://id.jobstreet.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://id.jobstreet.com/id/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136",'
                    ' "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"\
             " AppleWebKit/537.36 (KHTML, like Gecko)"\
                 " Chrome/136.0.0.0 Safari/537.36',
        'x-datadog-origin': 'rum',
        # 'x-datadog-parent-id': '1715740275156720130',
        'x-datadog-sampling-priority': '1',
        # 'x-datadog-trace-id': '16471256710346544044',
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
    job_cards = soup.find_all('article',
                              attrs={"data-automation": "normalJob"})

    all_jobs_df = []
    print(f"Found {len(job_cards)} job cards on the first page.")
    try:
        for job_card in job_cards:
            job_info_df = parse_jobstreet(job_card)
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


def enrich_jobstreet(job_info_series: pd.Series,
                     proxy_string=None):
    """
    Enriches a single job's information by visiting its JobStreet page.
    Helper functions `is_empty_python` and `safe_read_html_python` have been
    inlined.

    Args:
        job_info_series (pd.Series): A pandas Series containing initial job
        information.
        Expected keys: 'job_url', 'job_title', 'job_company', etc.

    Returns:
        pandas.DataFrame: A single-row DataFrame with enriched job information.
    """

    FINAL_COLUMN_ORDER = [
        "source", "job_id", "job_url", "job_title", "job_company",
        "job_location", "job_salary", "job_list_date", "seniority_level",
        "employment_type", "industries", "job_description", "applicant",
        "get_time"
    ]

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'origin': 'https://id.jobstreet.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://id.jobstreet.com/id/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136",'
                    ' "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"\
             " AppleWebKit/537.36 (KHTML, like Gecko)"\
                 " Chrome/136.0.0.0 Safari/537.36',
        'x-datadog-origin': 'rum',
        # 'x-datadog-parent-id': '1715740275156720130',
        'x-datadog-sampling-priority': '1',
        # 'x-datadog-trace-id': '16471256710346544044',
    }

    # Initialize a dictionary from the input series to store all data
    # Ensure all expected final columns are present, defaulting to None
    result_data = {col: job_info_series.get(col) for col in FINAL_COLUMN_ORDER}
    result_data.update(job_info_series.to_dict())

    # Set default values for fields to be enriched if not already present
    result_data.setdefault('job_description', None)
    result_data.setdefault('seniority_level', None)
    result_data.setdefault('industries', None)
    result_data['get_time'] = datetime.now()

    url = result_data.get('job_url')
    job_title_display = result_data.get('job_title', 'N/A')
    job_company_display = result_data.get('job_company', 'N/A')

    print(f"Getting Job Details for {job_title_display}"
          f"- {job_company_display} (URL: {url})")

    if not url:
        print("Error: Job URL is missing.")
        result_data['job_description'] = "Job URL missing"
        result_data['seniority_level'] = "Job URL missing"
        for col in FINAL_COLUMN_ORDER:
            result_data.setdefault(col, None)
        return pd.DataFrame([result_data])[FINAL_COLUMN_ORDER]

    time.sleep(random.randint(1, 3))

    # --- Inlined safe_read_html_python logic ---

    proxies_dict = None
    if proxy_string:
        proxies_dict = {
            'http': proxy_string,
            'https': proxy_string  # Assuming the same proxy for http and https
        }
    page_soup = None
    error_message = None
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url,
                               headers=headers,
                               proxies=proxies_dict,
                               timeout=20)
        response.raise_for_status()
        page_soup = BeautifulSoup(response.content, 'html.parser')
    except cloudscraper.exceptions.CloudflareChallengeError as e_cf:
        error_message = str(f"Cloudflare challenge encountered: {e_cf}")
    except requests.exceptions.RequestException as e_req:
        error_message = str(f"Request failed: {e_req}")
    except Exception as e_parse:
        error_message = str(f"HTML parsing or other error: {e_parse}")
    # --- End of inlined safe_read_html_python logic ---

    if page_soup:
        desc_info_raw = None
        try:
            selector_desc_info = "div[data-automation*='jobAdDetails'] > div"
            desc_info_raw = page_soup.select_one(selector_desc_info)
        except Exception as e_desc_raw:
            print(f"Error selecting desc_info_raw: {e_desc_raw}")
            pass

        description_elements_html = []
        if desc_info_raw:
            try:
                all_children = list(desc_info_raw.find_all(recursive=False))
                if all_children:
                    description_elements_html = [
                        str(child) for child in all_children[:-1]]
                else:
                    description_elements_html = [str(desc_info_raw)]
            except Exception as e_desc_children:
                print(f"Error processing description"
                      f"children: {e_desc_children}")
                pass

        cleaned_description_parts = []
        if description_elements_html:
            for html_part in description_elements_html:
                try:
                    desc_text = html_part
                    desc_text = re.sub(r'\n|\t', '', desc_text)
                    desc_text = re.sub(r'\"', "'", desc_text)
                    desc_text = " ".join(desc_text.split()).strip()
                    desc_text = re.sub(r"<p><br\s*/?></p>", "\n\n",
                                       desc_text, flags=re.IGNORECASE)
                    desc_text = re.sub(r"</ul\s*>", "\n\n",
                                       desc_text, flags=re.IGNORECASE)
                    desc_text = re.sub(r"<h4[^>]*>", "<strong>",
                                       desc_text, flags=re.IGNORECASE)
                    desc_text = re.sub(r"</h4>", "</strong>",
                                       desc_text, flags=re.IGNORECASE)
                    tags_to_remove_pattern = (
                        r"<div[^>]*>|<div>|</div>|<ul[^>]*>|<ul>|</li>|</p>|"
                        r"</ol>|<br\s*/?>|<span[^>]*>|<span>|</span>"
                    )
                    desc_text = re.sub(tags_to_remove_pattern, "",
                                       desc_text, flags=re.IGNORECASE)
                    desc_text = re.sub(r"<p>|<ol>", "\n\n",
                                       desc_text, flags=re.IGNORECASE)
                    desc_text = re.sub(r"<li[^>]*>", "\n • ",
                                       desc_text, flags=re.IGNORECASE)
                    desc_text = re.sub(r"•\s*\n", "• ", desc_text)
                    desc_text = re.sub(r"\s+•", " •", desc_text)
                    desc_text = re.sub(r"(\n\s*){2,}", "\n\n", desc_text)
                    desc_text = re.sub(r"\n\n</strong>\n", "\n</strong>\n",
                                       desc_text, flags=re.IGNORECASE)
                    cleaned_description_parts.append(desc_text.strip())
                except Exception as e_clean:
                    print(f"Error cleaning description part: {e_clean}")
                    cleaned_description_parts.append(html_part)

        final_job_description = None
        if cleaned_description_parts:
            # --- Inlined is_empty_python logic for all parts ---
            all_parts_empty = True
            for part in cleaned_description_parts:
                if not (part is None or (
                    isinstance(part, float) and pd.isna(part)
                    )
                      or (isinstance(part, str) and not part.strip())):
                    all_parts_empty = False
                    break
            # --- End of inlined is_empty_python logic ---
            if all_parts_empty:
                final_job_description = None
            else:
                final_job_description = "\n\n".join(
                    filter(None, cleaned_description_parts))
                if not final_job_description.strip():
                    final_job_description = None

        result_data['job_description'] = final_job_description

        try:
            industry_element = page_soup\
                .select_one(
                    "span[data-automation='job-detail-classifications'] > a"
                    )
            if industry_element:
                industry = industry_element.get_text()
                result_data['industries'] = industry
        except Exception as e:
            print(f"Error getting industries: {e}")
            pass

        try:
            employment_type_element = page_soup\
                .select_one("span[data-automation='job-detail-work-type'] > a")
            if employment_type_element:
                employment_type = employment_type_element.get_text()
                result_data['employment_type'] = employment_type
        except Exception as e:
            print(f"Error getting employment_type: {e}")
            pass

        new_job_list_date_parsed = None
        try:
            server_state_script = page_soup.find('script',
                                                 attrs={'data-automation':
                                                        'server-state'})
            if server_state_script and server_state_script.string:
                script_content = server_state_script.string

                # Try to extract SEEK_REDUX_DATA
                redux_pattern = r"window\.SEEK_REDUX_DATA\s*=\s*(\{.*?\});"
                redux_data_match = re.search(redux_pattern,
                                             script_content, re.DOTALL)
                if redux_data_match:
                    json_str = redux_data_match.group(1)
                    data = json.loads(json_str)
                    date_posted_str = data.get('jobdetails', {})\
                        .get('result', {}).get('job', {})\
                        .get('listedAt', {}).get('dateTimeUtc')
                    if date_posted_str:
                        if date_posted_str.endswith('Z'):
                            dt_obj = datetime.strptime(date_posted_str,
                                                       '%Y-%m-%dT%H:%M:%S.%fZ')
                        else:
                            dt_obj = datetime.fromisoformat(
                                date_posted_str.replace('Z', '+00:00'))
                        new_job_list_date_parsed = dt_obj.date()

                if not new_job_list_date_parsed:
                    apollo_pattern = (r"window\.SEEK_APOLLO_DATA"
                                      r"\s*=\s*(\{.*?\});")
                    apollo_data_match = re.search(apollo_pattern,
                                                  script_content, re.DOTALL)
                    if apollo_data_match:
                        json_str = apollo_data_match.group(1)
                        data = json.loads(json_str)
                        # We need to find the key that contains "jobDetails"
                        job_details_key = None
                        for key in data.get("ROOT_QUERY", {}).keys():
                            if key.startswith("jobDetails:"):
                                job_details_key = key
                                break

                        if job_details_key:
                            date_posted_str = data.get("ROOT_QUERY", {})\
                                .get(job_details_key, {}).get('job', {})\
                                .get('listedAt', {}).get('dateTimeUtc')
                            if date_posted_str:
                                if date_posted_str.endswith('Z'):
                                    dt_obj = datetime\
                                        .strptime(date_posted_str,
                                                  '%Y-%m-%dT%H:%M:%S.%fZ')
                                else:
                                    dt_obj = datetime.fromisoformat(
                                        date_posted_str.replace('Z', '+00:00'))
                                new_job_list_date_parsed = dt_obj.date()

        except Exception as e_script_date:
            print(f"Error extracting date from data-automation='server-state'"
                  f" script: {e_script_date}")

        if new_job_list_date_parsed:
            result_data['job_list_date'] = new_job_list_date_parsed
            # print(f"Updated job_list_date from script tag:
            # {new_job_list_date_parsed}")

        result_data['get_time'] = datetime.now()

    else:
        print(f"Failed to fetch or parse page. Error: {error_message}")
        result_data['job_description'] = error_message
        result_data['seniority_level'] = error_message
        result_data['industries'] = None
        result_data['get_time'] = datetime.now()

    final_df = pd.DataFrame([result_data])
    for col in FINAL_COLUMN_ORDER:
        if col not in final_df.columns:
            final_df[col] = None

    return final_df[FINAL_COLUMN_ORDER]
