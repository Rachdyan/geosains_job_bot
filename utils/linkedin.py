from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import random


def get_linkedin(all_jobs_page_soup):
    """
    Extracts job information from a BeautifulSoup element representing a job
    listing on LinkedIn.

    Args:
        all_jobs_page_soup (BeautifulSoup.Tag): A BeautifulSoup Tag object
                                                 representing a single
                                                 job listing.

    Returns:
        pandas.DataFrame: A DataFrame with a single row containing the
        extracted job information. Returns a DataFrame with error
          messages if extraction fails.
    """
    source = "linkedin"

    job_id = None
    try:
        job_id_element = all_jobs_page_soup.\
            select_one("div[data-entity-urn], a[data-entity-urn]")
        if job_id_element:
            job_id_urn = job_id_element.get("data-entity-urn")
            if job_id_urn:
                job_id = job_id_urn.split(":")[-1]
    except Exception:
        pass

    job_url = f"https://www.linkedin.com/jobs/view/{job_id}" \
        if job_id else None

    job_title = None
    try:
        title_element = all_jobs_page_soup.select_one("h3")
        if title_element:
            job_title = title_element.get_text(strip=True)
    except Exception:
        pass

    job_company = None
    try:
        company_element = all_jobs_page_soup.select_one("h4")
        if company_element:
            job_company = company_element.get_text(strip=True)
    except Exception:
        pass

    job_location = None
    try:
        location_element = all_jobs_page_soup\
            .select_one("div[class*='metadata'] > span[class*='location']")
        if location_element:
            job_location_text = location_element.get_text(strip=True)
            if not job_location_text.endswith(", Indonesia"):
                job_location = f"{job_location_text}, Indonesia"
            else:
                job_location = job_location_text
    except Exception:
        pass

    job_salary = None
    try:
        salary_element = all_jobs_page_soup.\
            select_one("div[class*='metadata'] > span[class*='salary']")
        if salary_element:
            job_salary = salary_element.get_text(strip=True)
    except Exception:
        pass

    job_list_date = None
    try:
        date_element = all_jobs_page_soup.\
            select_one("div[class*='metadata'] > time[class*='listdate']")
        if date_element:
            job_list_date = date_element.get('datetime')
    except Exception:
        pass

    try:
        job_info_df = pd.DataFrame({
            'source': [source],
            'job_id': [job_id],
            'job_url': [job_url],
            'job_title': [job_title],
            'job_company': [job_company],
            'job_location': [job_location],
            'job_salary': [job_salary],
            'job_list_date': [job_list_date]
        })
        return job_info_df
    except Exception:
        return pd.DataFrame({
            'job_id': ["Error"],
            'job_url': ["Error"],
            'job_title': [None],
            'job_company': [None],
            'job_location': [None],
            'job_salary': [None],
            'job_list_date': [None]
        })


def get_job_from_linkedin_url(url, sb):
    print(f"Getting job from {url}")
    sb.open(url)
    sb.sleep(2)
    # last_height = sb.execute_script("return document.body.scrollHeight")
    last_height = 0

    while True:
        sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sb.sleep(3)  # Delay by 3 seconds to allow content to load
        # print(f":Last Height: {last_height}")
        new_height = sb.execute_script("return document.body.scrollHeight")
        # print(f"New Height: {new_height}")
        if last_height == new_height:
            break
        else:
            last_height = new_height

    page = sb.get_page_source()
    soup = BeautifulSoup(page, 'html5lib')

    all_jobs_page = soup.select("ul[class*='results-list'] > li")

    job_listings_data = [get_linkedin(job_element)
                         for job_element in all_jobs_page]
    all_jobs_df = pd.concat(job_listings_data, ignore_index=True)
    return all_jobs_df


def enrich_linkedin(job_info_df, driver):
    """
    Navigates to a LinkedIn job URL, extracts detailed job information,
    and adds it as new columns to the input DataFrame.

    Args:
        job_info_df (pd.DataFrame): A DataFrame containing basic job
        information for a single job (expected to have one row). driver
        (selenium.webdriver.remote.webdriver.WebDriver):
        The Selenium WebDriver instance.

    Returns:
        pd.DataFrame: The input DataFrame with added columns for
        detailed job info.
    """

    url = job_info_df['job_url'].iloc[0]
    job_title = job_info_df['job_title'].iloc[0]
    job_company = job_info_df['job_company'].iloc[0]
    print(f"Getting Job Details for {job_title} - {job_company}")

    # Initialize new columns with default None values.
    # This ensures they exist even if extraction fails later.
    job_info_df['seniority_level'] = None
    job_info_df['employment_type'] = None
    job_info_df['industries'] = None
    job_info_df['job_description'] = None
    job_info_df['applicant'] = None
    job_info_df['get_time'] = pd.Timestamp\
        .now()  # Set initial get_time

    try:
        driver.get(url)
    except Exception as e:
        print(f"Failed to get URL {url}: {e}")
        # job_info_df already has None for new columns and current get_time
        return job_info_df

    time.sleep(3)

    # User added script execution - ensure 'driver' is used
    try:
        driver.execute_script("document.elementFromPoint(10, 10).click();")
        print("Executed click script.")
        time.sleep(1)
    except Exception as e:
        print(f"Could not execute click script: {e}")

    try:
        show_more_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "button[class*='show-more-less-html__button']"))
        )
        show_more_button.click()
        print("Clicked 'Show more' button for description.")
        time.sleep(1)  # Wait for description to expand
    except (NoSuchElementException, TimeoutException):
        print("Could not find or click 'Show more' button for description.")

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    keywords = ["Job ID", "Job Type",
                "Location", "Categories", "Applications close"]

    extracted_job_description = None  # Use a temporary variable for extraction
    try:
        description_element = soup.select_one(
            "div[class*='show-more-less-html__markup']")
        if description_element:
            extracted_job_description = str(description_element)
            # Apply cleaning rules
            extracted_job_description = re.sub(r'[\"\']', "'",
                                               extracted_job_description)
            div_wrapper_pattern = (
                r"<div class='show-more-less-html__markup "
                r"show-more-less-html__markup--clamp-after-5\s+relative "
                r"overflow-hidden'>|<div class='show-more-less-html__markup "
                r"relative overflow-hidden'>"
            )
            extracted_job_description = re.sub(
                div_wrapper_pattern,
                "",
                extracted_job_description,
                flags=re.IGNORECASE
            )

            extracted_job_description = re.sub(r'[\n\t]+', ' ',
                                               extracted_job_description)
            extracted_job_description = re.sub(r'\s{2,}', ' ',
                                               extracted_job_description)
            extracted_job_description = re.sub(r"<p><br></p>", "\n\n",
                                               extracted_job_description,
                                               flags=re.IGNORECASE)
            extracted_job_description = re.sub(r"</p>|<br\s*/?>", "\n\n",
                                               extracted_job_description,
                                               flags=re.IGNORECASE)
            extracted_job_description = re.sub(r"</ul>", "\n\n",
                                               extracted_job_description,
                                               flags=re.IGNORECASE)
            extracted_job_description = re.sub(r"</li>", "\n",
                                               extracted_job_description,
                                               flags=re.IGNORECASE)
            extracted_job_description = re.sub(
                r"<div>|</div>|<ul>|</ol>|<span>|</span>", "",
                extracted_job_description, flags=re.IGNORECASE)
            extracted_job_description = re.sub(r"<p>|<ol>", "\n\n",
                                               extracted_job_description,
                                               flags=re.IGNORECASE)
            extracted_job_description = re.sub(r"<li>", "\n • ",
                                               extracted_job_description,
                                               flags=re.IGNORECASE)
            extracted_job_description = re.sub(r"•\s*\n", "• ",
                                               extracted_job_description)
            extracted_job_description = re.sub(r"\s+•", " •",
                                               extracted_job_description)
            extracted_job_description = re.sub(r"(\n\s*){3,}", "\n\n",
                                               extracted_job_description)
            extracted_job_description = re.sub(r"\n\n</strong>\n",
                                               "\n</strong>\n",
                                               extracted_job_description,
                                               flags=re.IGNORECASE)

            if extracted_job_description:
                for keyword_text in keywords:
                    escaped_keyword = re.escape(keyword_text)
                    cur_pattern_str = r"(?<=\b" + escaped_keyword + r"\b)\n\n"
                    extracted_job_description = re.sub(
                        cur_pattern_str, "\n", extracted_job_description)

            if extracted_job_description:
                job_info_df['job_description'] = extracted_job_description\
                    .strip()

    except Exception as e:
        print(f"An error occurred during job description processing: {e}")
        # job_description remains None or its last successfully processed state
        pass

    # --- Extract other details ---
    extracted_applicant_count = None
    try:
        applicant_selectors = (
            "figcaption[class*='applicants'], "
            "span[class*='num-applicants__caption'], "
            "span[class*='applicants']"
        )
        applicant_element = soup.select_one(applicant_selectors)
        if applicant_element:
            extracted_applicant_count = applicant_element.get_text(strip=True)
            job_info_df['applicant'] = extracted_applicant_count
    except Exception as e:
        print(f"Error extracting applicant count: {e}")
        pass

    # Update get_time to reflect the actual processing time
    job_info_df['get_time'] = pd.Timestamp.now()

    extracted_seniority_level = None
    extracted_employment_type = None
    extracted_industries = None

    job_criteria_selectors = (
        "ul[class*='job-criteria__list'] > li.job-criteria__item, "
        "ul[class*='description__job-criteria-list'] > "
        "li.description__job-criteria-item"
    )
    job_criteria_elements = soup.select(job_criteria_selectors)

    if job_criteria_elements:

        criteria_map = {}
        for item in job_criteria_elements:
            header_el = item\
                .select_one("h3[class*='job-criteria__subheader'], dt")
            value_el = item.select_one("span[class*='job-criteria__text'], dd")

            if header_el and value_el:
                header_text = header_el.get_text(strip=True).lower()
                value_text = value_el.get_text(strip=True)
                criteria_map[header_text] = value_text
            else:
                item_text_parts = [s.strip() for s in item
                                   .get_text(separator='\n', strip=True)
                                    .split('\n') if s.strip()]
                if len(item_text_parts) == 2:
                    criteria_map[item_text_parts[0]
                                 .lower()] = item_text_parts[1]
                elif len(item_text_parts) == 1:
                    pass

        # Assign from map
        extracted_seniority_level = criteria_map.get("seniority level")
        extracted_employment_type = criteria_map.get("employment type")
        extracted_industries = criteria_map.get("industries") or criteria_map.\
            get("job function")

        if extracted_seniority_level:
            job_info_df['seniority_level'] = extracted_seniority_level
        if extracted_employment_type:
            job_info_df['employment_type'] = extracted_employment_type
        if extracted_industries:
            job_info_df['industries'] = extracted_industries
    else:
        print("Job criteria elements not found or structure not recognized.")

    time.sleep(random.uniform(1, 3))

    return job_info_df
