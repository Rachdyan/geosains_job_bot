import pandas as pd
import re
import asyncio
import random
import telegram
from datetime import datetime
from dateutil.relativedelta import relativedelta


async def send_telegram_message(row_series: pd.Series, bot_token: str,
                                chat_id: str) -> pd.DataFrame:
    """
    Formats and sends a job posting to a Telegram chat via a bot
    (asynchronously), and logs the action.

    Args:
        row_series (pd.Series): A pandas Series containing job information
        (e.g., a row from a DataFrame). Expected columns: 'job_description',
        'job_title', 'job_company', 'job_location', 'seniority_level',
        'job_url', 'source'.
        bot_token (str): The Telegram bot token.
        chat_id (str): The Telegram chat ID to send the message to.

    Returns:
        pd.DataFrame: A single-row DataFrame containing logging information
        (source, url, title, company, posted_at).
    """
    bot = telegram.Bot(token=bot_token)

    description = row_series.get('job_description')

    newline_count = 0
    if isinstance(description, str):
        newline_count = description.count("\n")

    if pd.isna(description):
        description = ""

    source_val = row_series.get('source')
    is_not_petromindo = False
    if pd.notna(source_val) and source_val != "petromindo":
        is_not_petromindo = True

    # Truncate description logic
    if len(description) > 300 and newline_count > 60 and is_not_petromindo:
        description = description[:300]
        description = description.rstrip()
        description = re.sub(r"<[^>]*$", "", description)
        description = description.rstrip()
        description = re.sub(r"<[^/][^>]*>$", "", description)
        description = description.rstrip()
        description = re.sub(r"<[^/][^>]*>[^<]*$", "", description)
        description = re.sub(r"<[^/][^>]*>[^<]*$", "", description)
        description = description.rstrip()
        description = f"{description}...\n\nRead more on website:"
    elif len(description) > 500:
        description = description[:500]
        description = description.rstrip()
        description = re.sub(r"<[^>]*$", "", description)
        description = description.rstrip()
        description = re.sub(r"<[^/][^>]*>$", "", description)
        description = description.rstrip()
        description = re.sub(r"<[^/][^>]*>[^<]*$", "", description)
        description = re.sub(r"<[^/][^>]*>[^<]*$", "", description)
        description = description.rstrip()
        description = f"{description}...\n\nRead more on website:"
    else:
        description = f"{description}\n\n"

    # Message construction logic
    job_title_upper = str(row_series.get('job_title', '')).upper()
    job_company = row_series.get('job_company', '')
    job_location_raw = row_series.get('job_location')
    job_location = ""
    if pd.notna(job_location_raw):
        job_location = str(job_location_raw).replace(', Indonesia', '')

    seniority_level = row_series.get('seniority_level')
    job_url = row_series.get('job_url', '')

    message_parts = []
    message_parts.append(f"<strong>{job_title_upper}</strong>")
    message_parts.append(f"<em>{job_company}</em>")

    if source_val == "disnakerja":
        if job_location:
            message_parts.append(f"\nLocation: {job_location}")
        message_parts.append(f"\n{description}")
        message_parts.append(job_url)
    elif pd.isna(job_location_raw) and pd.isna(seniority_level):
        message_parts.append(f"\n{description}")
        message_parts.append(job_url)
    elif pd.isna(seniority_level) or source_val == "Jobstreet":
        if job_location:
            message_parts.append(f"\nLocation: {job_location}")
        message_parts.append(f"\n{description}")
        message_parts.append(job_url)
    elif pd.isna(job_location_raw):
        if pd.notna(seniority_level):
            message_parts.append(f"\nLevel: {seniority_level}")
        message_parts.append(f"\n{description}")
        message_parts.append(job_url)
    else:
        if job_location:
            message_parts.append(f"\nLocation: {job_location}")
        if pd.notna(seniority_level):
            message_parts.append(f"Level: {seniority_level}")
        message_parts.append(f"\n{description}")
        message_parts.append(job_url)

    message = "\n".join(filter(None, message_parts))

    # Clean up excessive newlines in the final message
    message = re.sub(r"(\n{2,})\n+", "\n\n", message)
    message = re.sub(r"\n\n\s+\n\n", "\n\n", message)
    message = re.sub(r"\n{2,}\s*\n", "\n\n", message)
    message = message.strip()

    print("Sending msg for"
          f"{row_series.get('job_title', 'N/A')} - {job_url}")

    send_status_id = None
    try:
        # Use await for async call and constants.ParseMode for v20+
        sent_message = await bot.send_message(chat_id=chat_id, text=message,
                                              parse_mode='html')
        send_status_id = sent_message.message_id
    except Exception as e:
        print(f"Error sending message for"
              f"{row_series.get('job_title', 'N/A')} - {job_url}\nError: {e}")
        # send_status_id remains None

    # Using asyncio.sleep for non-blocking sleep in async function
    await asyncio.sleep(random.randint(2, 4))

    # Prepare log entry
    log_data = {
        'source': source_val,
        'job_url': job_url,
        'job_title': row_series.get('job_title'),
        'job_company': job_company
    }

    if send_status_id is None:
        log_data['posted_at'] = datetime.now() + relativedelta(years=50)
    else:
        log_data['posted_at'] = datetime.now()

    log_entry_df = pd.DataFrame([log_data])

    return log_entry_df


async def process_all_jobs(df, bot_token, chat_id):
    """
    Iterates through a DataFrame and sends a Telegram message for each job.
    Collects logging information.
    """
    all_log_entries = []

    for index, row_series in df.iterrows():
        print(f"\nProcessing job: {row_series.get('job_title', 'N/A')}")
        try:
            # Make sure to pass the row (which is a pandas Series)
            log_entry_df = await send_telegram_message(row_series,
                                                       bot_token, chat_id)
            all_log_entries.append(log_entry_df)
            print(f"Successfully sent and logged:"
                  f"{row_series.get('job_title', 'N/A')}")
        except Exception as e:
            print(f"Failed to process job"
                  f"{row_series.get('job_title', 'N/A')}: {e}")
            # Optionally, create a log entry for failures too
            # failure_log = pd.DataFrame([{
            #     'source': row_series.get('source'),
            #     'job_url': row_series.get('job_url'),
            #     'job_title': row_series.get('job_title'),
            #     'job_company': row_series.get('job_company'),
            #     'posted_at': datetime.now()
            #     'error': str(e)
            # }])

    if all_log_entries:
        # Concatenate all individual log DataFrames into one
        final_log_df = pd.concat(all_log_entries, ignore_index=True)
        return final_log_df
    else:
        return pd.DataFrame()
