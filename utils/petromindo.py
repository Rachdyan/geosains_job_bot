import pandas as pd
from bs4 import BeautifulSoup
import re
import cloudscraper
from datetime import datetime
import time


def parse_petromindo(job_card_soup: BeautifulSoup, industries: str):
    """
    Parses a BeautifulSoup Tag object representing a single job card from
    Petromindo.

    Args:
        job_card_soup (BeautifulSoup): The BeautifulSoup Tag object for a job
        card.
        This element itself is expected to have 'id' and 'title' attributes.
        industries (str): The industries string to associate with this job.

    Returns:
        pandas.DataFrame: A single-row DataFrame containing extracted job
        information.
    """
    source = "petromindo"
    job_id = None
    job_company = None
    job_title = None
    job_url = None

    # Extract job_id
    # R: html_attr("id") %>% str_after_first("-")
    try:
        raw_id = job_card_soup.get('id')
        if raw_id and isinstance(raw_id, str) and '-' in raw_id:
            job_id = raw_id.split('-', 1)[1]  # Get part after the first hyphen
        elif raw_id:
            job_id = raw_id
    except Exception as e:
        print(f"Error extracting job_id from Petromindo card: {e}")
        # job_id remains None

    # Extract job_company and job_title from the 'title' attribute of the
    # job_card_soup
    title_attribute_text = None
    try:
        title_attribute_text = job_card_soup.get('title')
    except Exception as e:
        print(f"Error getting 'title' attribute from Petromindo card: {e}")

    if title_attribute_text and isinstance(title_attribute_text, str):
        # Extract job_company
        # R: str_before_first(";")
        try:
            if ';' in title_attribute_text:
                job_company = title_attribute_text.split(';', 1)[0].strip()
            else:
                job_company = title_attribute_text.strip()
            if not job_company:
                job_company = None
        except Exception as e:
            print(f"Error extracting job_company from title "
                  f"attribute '{title_attribute_text}': {e}")
            job_company = None

        # Extract job_title
        # R: str_after_first("; ") %>% str_squish() %>% ...
        try:
            if '; ' in title_attribute_text:
                title_part = title_attribute_text.split('; ', 1)[1]

                title_part = " ".join(title_part.split()).strip()
                title_part = title_part.replace("2 of 2 ads", "(2)")
                title_part = title_part.replace("1 of 2 ads", "(1)")
                # R: str_remove_all(";")
                job_title = title_part.replace(";", "").strip()
            elif ';' not in title_attribute_text and \
                 job_company == title_attribute_text:
                job_title = None
            elif ';' not in title_attribute_text:
                job_title = None

            if not job_title:
                job_title = None
        except Exception as e:
            print(f"Error extracting job_title from title attribute"
                  f" '{title_attribute_text}': {e}")
            job_title = None
    else:
        job_company = None
        job_title = None

    try:
        first_a_tag = job_card_soup.find('a')
        if first_a_tag:
            job_url = first_a_tag.get('href')
            if not job_url or not job_url.strip():
                job_url = None
        else:
            job_url = None
    except Exception as e:
        print(f"Error extracting job_url from Petromindo card: {e}")
        job_url = None

    # R: tibble(...)
    job_data = {
        'source': source,
        'job_id': job_id,
        'job_url': job_url,
        'job_title': job_title,
        'job_company': job_company,
        'industries': industries
    }

    return pd.DataFrame([job_data])


def get_job_from_petromindo_url(url, industry,
                                proxy_string=None):
    print(f'Getting job from {url}')

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        # 'content-length': '0',
        'origin': 'https://www.petromindo.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.petromindo.com/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", \
            "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/136.0.0.0 Safari/537.36',
        # 'cookie': 'ar_debug=1',
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

    job_cards = soup.select("article")

    all_jobs_df = []
    print(f"Found {len(job_cards)} job cards on the first page.")
    try:
        all_jobs_df = pd.concat([
            parse_petromindo(
                job_card_soup=job_card, industries="oil-gas")
            for job_card in job_cards
        ])
        print("All Jobs Df:")
        print(all_jobs_df)
        return all_jobs_df
    except Exception as e:
        print("Error", e)
        return None


def enrich_petromindo(job_info_series: pd.Series, proxy_string):
    """
    Enriches a single job's information by visiting its Petromindo page.

    Args:
        job_info_series (pd.Series): A pandas Series containing initial
        job information.
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

    # Predefined list of Indonesian locations from the R script
    INDONESIAN_LOCATIONS = [
        "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi",
        "Sumatera Selatan", "Bengkulu", "Lampung", "Kepulauan Bangka Belitung",
        "Kepulauan Riau", "Jakarta", "Jawa Barat", "Jawa Tengah",
        "Yogyakarta", "Jawa Timur", "Banten", "Bali ",
        "Nusa Tenggara Barat", "Nusa Tenggara Timur", "Kalimantan Barat",
        "Kalimantan Tengah",
        "Kalimantan Selatan", "Kalimantan Timur", "Kalimantan Utara",
        "Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan",
        "Sulawesi Tenggara",
        "Gorontalo", "Sulawesi Barat", "Maluku", "Maluku Utara", "Papua Barat",
        "Papua", "Pontianak", "Banjarmasin", "Samarinda", "Balikpapan",
        "Palangkaraya",
        "Banjarbaru", "Tarakan", "Sanggau"
    ]
    # Normalize the locations for Python (e.g., strip trailing spaces)

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        # 'content-length': '0',
        'origin': 'https://www.petromindo.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.petromindo.com/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", \
            "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/136.0.0.0 Safari/537.36',
        # 'cookie': 'ar_debug=1',
    }

    proxies_dict = None
    if proxy_string:
        proxies_dict = {
            'http': proxy_string,
            'https': proxy_string  # Assuming the same proxy for http and https
        }
    result_data = {col: job_info_series.get(col) for col in FINAL_COLUMN_ORDER}
    result_data.update(job_info_series.to_dict())

    # Fields to be extracted or defaulted
    result_data['job_location'] = None
    result_data['job_list_date'] = None
    result_data['job_description'] = None
    result_data['job_salary'] = None      # Hardcoded NA in R
    result_data['employment_type'] = None
    result_data['seniority_level'] = None
    result_data['applicant'] = None       # Hardcoded NA in R
    result_data['get_time'] = datetime.now()

    url = result_data.get('job_url')
    job_title_display = result_data.get('job_title', 'N/A')
    job_company_display = result_data.get('job_company', 'N/A')

    print(f"Getting Job Details for {job_title_display}"
          f" - {job_company_display} from Petromindo - {url}")

    if not url:
        print("Error: Job URL is missing for Petromindo processing.")
        result_data['job_description'] = "Job URL missing"
        for col in FINAL_COLUMN_ORDER:
            result_data.setdefault(col, None)
        return pd.DataFrame([result_data])[FINAL_COLUMN_ORDER]

    time.sleep(1)

    page_soup = None
    error_message_http = None
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url, headers=headers,
                               proxies=proxies_dict,
                               timeout=15)
        response.raise_for_status()
        page_soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        error_message_http = str(e)
        print(f"Error fetching page {url}: {e}")

    if page_soup:
        # --- Job Location ---
        desc_text_for_location = None
        try:
            location_desc_container = page_soup\
                .select_one(
                    "div[class*='col-12'][class*='col-md-8'] > article > div")
            if location_desc_container:
                desc_text_for_location = location_desc_container.get_text(
                    separator=" ", strip=True)
        except Exception as e_loc_text:
            print(f"Error extracting text for location analysis: {e_loc_text}")

        if not (desc_text_for_location is None or
                (isinstance(desc_text_for_location, float) and
                 pd.isna(desc_text_for_location)) or
                (isinstance(desc_text_for_location, str) and
                 not desc_text_for_location.strip()) or
                (isinstance(desc_text_for_location, list) and
                 not desc_text_for_location)):
            location_counts = {loc: desc_text_for_location.lower()
                               .count(loc.lower())
                               for loc in INDONESIAN_LOCATIONS}

            max_count = 0
            if location_counts:
                max_count = max(location_counts.values())

            if max_count > 0:
                max_locations = [loc for loc, count in location_counts.items()
                                 if count == max_count]
                if len(max_locations) == 1:
                    result_data['job_location'] = " ".join(max_locations[0]
                                                           .split()).strip()
                else:
                    print(f"Multiple locations found with max count "
                          f"({max_count}): {max_locations}."
                          f"Setting location to None.")
                    result_data['job_location'] = None
            else:
                result_data['job_location'] = None
        else:
            result_data['job_location'] = None

        # --- Job List Date ---
        try:
            date_span_element = page_soup.select_one(
                "header[class*='header'] > p > span")
            if date_span_element:
                date_text_raw = date_span_element.get_text(strip=True)
                if ": " in date_text_raw:
                    date_str_to_parse = date_text_raw.split(": ", 1)[1]
                    try:
                        parsed_date_obj = datetime.strptime(
                            date_str_to_parse, '%B %d, %Y').date()
                        result_data['job_list_date'] = parsed_date_obj
                    except ValueError as ve:
                        print(f"Could not parse date string "
                              f"'{date_str_to_parse}' with mdy format: {ve}")
                        pass
        except Exception as e_date:
            print(f"Error extracting job_list_date: {e_date}")

        job_list_date_val = result_data.get('job_list_date')
        if job_list_date_val is None or \
           (isinstance(job_list_date_val, float) and
            pd.isna(job_list_date_val)) or \
           (isinstance(job_list_date_val, str) and
            not job_list_date_val.strip()) or \
           (isinstance(job_list_date_val, list) and not job_list_date_val):
            result_data['job_list_date'] = None

        # --- Job Description ---
        description_raw_container = None
        try:
            selector_desc_container = "div[class*='container'] > "\
                "div[class*='row'] > div > article > div"
            description_raw_container = page_soup.select_one(
                selector_desc_container)
        except Exception as e_desc_container:
            print(f"Error selecting description_raw_container:"
                  f"{e_desc_container}")

        if description_raw_container:
            try:
                p_tags = description_raw_container.find_all("p")
                full_desc_html_from_p = "".join([str(p) for p in p_tags]) \
                    if p_tags else ""

                if not full_desc_html_from_p and description_raw_container:
                    print("No <p> tags found in description container, "
                          "using full container HTML for description.")
                    full_desc_html_from_p = str(description_raw_container)

                desc_text = full_desc_html_from_p
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

                tags_to_remove_pattern = (
                    r"<div[^>]*>|<div>|</div>|<ul[^>]*>|<ul>|</li>|</p>|"
                    r"</ol>|<br\s*/?>|<span[^>]*>|<span>|</span>"
                )
                desc_text = re.sub(tags_to_remove_pattern, "", desc_text,
                                   flags=re.IGNORECASE)

                desc_text = re.sub(r"<p[^>]*>|<ol>", "\n\n", desc_text,
                                   flags=re.IGNORECASE)
                desc_text = re.sub(r"<li[^>]*>", "\n • ", desc_text,
                                   flags=re.IGNORECASE)
                desc_text = re.sub(r"\n\s+\n", "\n\n", desc_text)
                desc_text = re.sub(r"\n\n<strong>\n\n", "<strong>\n\n",
                                   desc_text, flags=re.IGNORECASE)
                desc_text = re.sub(r"•\s*\n(\s*\n)?", "• ", desc_text)
                desc_text = re.sub(r"\s+•", " •", desc_text)
                desc_text = re.sub(r"(\n\s*){2,}", "\n\n", desc_text)
                desc_text = re.sub(r"\n\n</strong>\n", "\n</strong>\n",
                                   desc_text, flags=re.IGNORECASE)

                desc_text = desc_text.strip() if \
                    desc_text and desc_text.strip() else None

                if desc_text and len(desc_text) > 5000:
                    desc_text = desc_text[:5000]

                result_data['job_description'] = desc_text

            except Exception as e_desc_clean:
                print(f"Error cleaning Petromindo description: {e_desc_clean}")

        job_description_val = result_data.get('job_description')

        if job_description_val is None or \
           (isinstance(job_description_val, float) and
            pd.isna(job_description_val)) or \
           (isinstance(job_description_val, str) and
            not job_description_val.strip()) or \
           (isinstance(job_description_val, list) and not job_description_val):
            result_data['job_description'] = None

        result_data['get_time'] = datetime.now()

    else:
        print(f"Failed to fetch or parse page {url}."
              f"Error: {error_message_http}")
        error_val_for_fields = error_message_http if error_message_http \
            else "Page fetch/parse failed"
        result_data['job_location'] = error_val_for_fields
        result_data['job_list_date'] = error_val_for_fields
        result_data['job_description'] = error_val_for_fields
        result_data['get_time'] = datetime.now()

    final_df = pd.DataFrame([result_data])
    for col in FINAL_COLUMN_ORDER:
        if col not in final_df.columns:
            final_df[col] = None

    return final_df[FINAL_COLUMN_ORDER]
