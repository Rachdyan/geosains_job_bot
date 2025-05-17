from seleniumbase import SB
import pandas as pd
from pydrive2.auth import GoogleAuth
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from dotenv import load_dotenv
import os
from gspread_dataframe import get_as_dataframe
import asyncio


from utils.indeed import get_job_from_indeed_url, enrich_indeed
from utils.gsheet_utils import export_to_sheets
from utils.telegram_utlis import process_all_jobs

load_dotenv(override=True)

user = os.environ['PROXY_USER']
password = os.environ['PROXY_PASSWORD']
proxy_host = os.environ['PROXY_HOST']
proxy_port = os.environ['PROXY_PORT']

proxy_string = f"{user}:{password}@{proxy_host}:{proxy_port}"

private_key_id = os.environ['SA_PRIVKEY_ID']
sa_client_email = os.environ['SA_CLIENTMAIL']
sa_client_x509_url = os.environ['SA_CLIENT_X509_URL']
private_key = os.environ['SA_PRIVKEY']

private_key = private_key.replace('\\n', '\n')
full_private_key = f"-----BEGIN PRIVATE KEY-----\n"\
                    f"{private_key}\n-----END PRIVATE KEY-----\n"

service_account_dict = {
    "type": "service_account",
    "project_id": "keterbukaan-informasi-idx",
    "private_key_id": private_key_id,
    "private_key": full_private_key,
    "client_email": sa_client_email,
    "client_id": "116805150468350492730",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url":
    "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": sa_client_x509_url,
    "universe_domain": "googleapis.com"
}

scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

gauth = GoogleAuth()

try:
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        service_account_dict, scope
    )
except Exception as e:
    print(f"Error loading credentials from dictionary: {e}")
    # Handle error appropriately, maybe exit
    exit(1)

creds = gauth.credentials
gc = None
spreadsheet = None
worksheet = None
try:
    gc = gspread.authorize(creds)
    print("Google Sheets client (gspread) initialized successfully.")

    sheet_key = "1TFt8FJjsLidlYkSIRstXq5raBipXN91G2bmwwgd64DM"
    spreadsheet = gc.open_by_key(sheet_key)

    print(f"Successfully opened spreadsheet: '{spreadsheet.title}'")

except gspread.exceptions.SpreadsheetNotFound:
    print("Error: Spreadsheet not found. \n"
          "1. Check if the name/key/URL is correct.\n")
    # Decide if you want to exit or continue without sheet access
    exit(1)
except gspread.exceptions.APIError as e:
    print(f"Google Sheets API Error: {e}")
    exit(1)
except Exception as e:
    # Catch other potential errors during gspread initialization/opening
    print(f"An error occurred during Google Sheets setup: {e}")
    exit(1)

urls = ["https://id.indeed.com/jobs?q=geology&sort=date",
        "https://id.indeed.com/jobs?q=geologi&sort=date",
        "https://id.indeed.com/jobs?q=geologist&sort=date",
        "https://id.indeed.com/jobs?q=mine&sort=date",
        "https://id.indeed.com/jobs?q=mining&sort=date",
        "https://id.indeed.com/jobs?q=oil+and+gas&sort=date",
        "https://id.indeed.com/jobs?q=migas&sort=date",
        "https://id.indeed.com/jobs?q=geodesi&sort=date",
        "https://id.indeed.com/jobs?q=tambang&sort=date",
        # 'https://id.indeed.com/jobs?q="gis"&sort=date'
        ]

if __name__ == "__main__":
    with SB(uc=True,
            # headless=True,
            xvfb=True,
            proxy=proxy_string,
            # incognito=True,
            maximize=True,
            ) as sb:
        sb.driver.execute_cdp_cmd(
                "Network.setExtraHTTPHeaders",
                {
                    "headers": {
                        'Accept': 'text/html,application/xhtml+xml,application\
                            /xml;q=0.9,image/avif,image/webp,image/apng,*/*;\
                                q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'Accept-Encoding': 'gzip, deflate, br, zstd',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Cache-Control': "no-cache",
                        'Pragma': "no-cache",
                        'Priority': "u=0, i",
                        'Sec-Ch-Ua': '"Chromium";v="134", \
                            "Not:A-Brand";v="24","Google Chrome";v="134"',
                        'Sec-Ch-Mobile': "?0",
                        'Sec-Ch-Ua-Platform': '"macOS"',
                        'Sec-Fetch-Dest': "document",
                        'Sec-Fetch-Mode': "navigate",
                        'Sec-Fetch-User': "?1",
                        'Upgrade-Insecure-Requests': '1',
                    }
                }
            )

        sb.driver.execute_cdp_cmd(
                "Network.setUserAgentOverride",
                {
                    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X \
                        10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) \
                            Chrome/134.0.0.0 Safari/537.36"
                },
            )

        sb.driver.execute_script("Object.defineProperty(navigator, \
                                 'webdriver',{get: () => undefined})")

        # sb.open("https://id.indeed.com")
        sb.driver.uc_open_with_reconnect("https://id.indeed.com",
                                         reconnect_time=5)
        # sb.uc_gui_click_cf()
        sb.uc_gui_handle_cf()
        sb.sleep(3)
        all_jobs_df = pd.concat([
            get_job_from_indeed_url(
                url=url, sb=sb)
            for url in urls
            ])

        previously_scraped_df_sheet = spreadsheet\
            .worksheet('Scraped not Filtered')
        previously_scraped_df = get_as_dataframe(previously_scraped_df_sheet)
        previously_scraped_df['job_id'] = pd.to_numeric(
            previously_scraped_df['job_id'], errors='coerce')\
            .astype('Int64')
        # Then convert to string
        previously_scraped_df['job_id'] = previously_scraped_df['job_id']\
            .astype(str)
        # Replace '<NA>' if you had NaNs and don't want them as strings
        previously_scraped_df['job_id'] = previously_scraped_df['job_id']\
            .replace('<NA>', pd.NA)
        # previously_scraped_df

        all_jobs_df_filtered = all_jobs_df[
            ~all_jobs_df.job_id.isin(previously_scraped_df.job_id.tolist())]
        # all_jobs_df_filtered

        enriched_job_data = []
        # all_jobs_sample = all_jobs_df_filtered.sample(10)
        for index, row in all_jobs_df_filtered.iterrows():
            enriched_info = enrich_indeed(row, spreadsheet=spreadsheet, sb=sb)
            enriched_job_data.append(enriched_info)

        print("Enriching job data...")
        enriched_all_jobs_df = pd.concat(enriched_job_data, ignore_index=True)

        print("Exporting filtered job data...")
        export_to_sheets(spreadsheet=spreadsheet, sheet_name='Geosains Job',
                         df=enriched_all_jobs_df, mode='a')


BOT_TOKEN = os.environ['BOT_TOKEN']
TARGET_CHAT_ID = "1415309056"


async def main():
    """
    Main asynchronous function to process jobs and return the log report.
    """
    print("Starting job processing...")
    final_log_report_internal = pd.DataFrame()

    if not enriched_all_jobs_df.empty:
        final_log_report_internal = await process_all_jobs(
            enriched_all_jobs_df, BOT_TOKEN, TARGET_CHAT_ID)
        print("\n--- Internal Log Report (within main) ---")
        if not final_log_report_internal.empty:
            print(final_log_report_internal.head())
        else:
            print("No jobs were processed or logged internally.")
    else:
        print("The DataFrame `enriched_all_jobs__filtered_df` is empty."
              "Nothing to process.")

    return final_log_report_internal

if __name__ == "__main__":
    # Run the main asynchronous function and capture its return value
    script_level_log_report = asyncio.run(main())

    print("\n--- Final Log Report ---")
    if (script_level_log_report is not None and
       not script_level_log_report.empty):
        print(script_level_log_report)
    elif script_level_log_report is not None and script_level_log_report.empty:
        print("Log report is empty (no jobs processed or logged).")
    else:
        print("Log report was not generated (e.g., BOT_TOKEN not set).")
