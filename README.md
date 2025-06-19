<div id="top">

<!-- HEADER STYLE: COMPACT -->
<img src="readmeai/assets/logos/purple.svg" width="30%" align="left" style="margin-right: 15px">

# GEOSAINS_JOB_BOT
<em>Empowering job seekers with curated geoscientist opportunities.</em>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/Rachdyan/geosains_job_bot?style=plastic&logo=opensourceinitiative&logoColor=white&color=blueviolet" alt="license">
<img src="https://img.shields.io/github/last-commit/Rachdyan/geosains_job_bot?style=plastic&logo=git&logoColor=white&color=blueviolet" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/Rachdyan/geosains_job_bot?style=plastic&color=blueviolet" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/Rachdyan/geosains_job_bot?style=plastic&color=blueviolet" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Selenium-43B02A.svg?style=plastic&logo=Selenium&logoColor=white" alt="Selenium">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=plastic&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=plastic&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
<img src="https://img.shields.io/badge/pandas-150458.svg?style=plastic&logo=pandas&logoColor=white" alt="pandas">

<br clear="left"/>

## Table of Contents

1. [Table of Contents](#table-of-contents)
2. [Overview](#overview)
3. [Features](#features)
4. [Project Structure](#project-structure)
    4.1. [Project Index](#project-index)
5. [Getting Started](#getting-started)
    5.1. [Prerequisites](#prerequisites)
    5.2. [Installation](#installation)
    5.3. [Usage](#usage)
    5.4. [Testing](#testing)
6. [Roadmap](#roadmap)
7. [Contributing](#contributing)
8. [License](#license)
9. [Acknowledgments](#acknowledgments)

---

## Overview

The Geosains Job Bot is a specialized tool designed to streamline the job search process for the geoscience community. It automatically scrapes various online sources for job vacancies in fields such as geology, geophysics, mining, and petroleum engineering. All discovered listings are then consolidated and broadcasted to the dedicated Telegram channel, [Loker Geosains](t.me/lokergeo).

**Why geosains_job_bot?**

This project simplifies data extraction and enrichment from platforms like LinkedIn, Jobstreet and more. The core features include:

- **🔍 Enhanced Data Scraping:** Leveraging libraries like BeautifulSoup, Pandas, and Selenium for efficient data extraction.
- **📊 Seamless Google Sheets Integration:** Manage and export data seamlessly to Google Sheets for organized data handling.
- **📱 Interactive Communication:** Utilize python-telegram-bot for real-time updates and notifications.
- **⚡ Asynchronous Processing:** Process job data from multiple sources asynchronously for faster results.

---

## Features

|      | Component       | Details                              |
| :--- | :-------------- | :----------------------------------- |
| ⚙️  | **Architecture**  | <ul><li>Follows a modular design with separate modules for scraping different job platforms like Indeed, Jobstreet, LinkedIn, etc.</li><li>Utilizes object-oriented programming principles for better organization and maintainability.</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Consistent code style and formatting throughout the project.</li><li>Includes docstrings for functions and classes to improve code readability.</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Integrates with various third-party libraries like BeautifulSoup, Selenium, Pandas for web scraping and data manipulation.</li><li>Uses Python-Telegram-Bot for Telegram integration.</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Codebase is divided into separate modules for different functionalities, promoting reusability and maintainability.</li><li>Each scraper module is responsible for scraping a specific job platform, enhancing modularity.</li></ul> |
| ⚡️  | **Performance**   | <ul><li>Efficiently utilizes cloudscraper for handling anti-bot measures during web scraping.</li><li>Optimizes data processing using Pandas for faster data manipulation.</li></ul> |
| 🛡️ | **Security**      | <ul><li>Utilizes cloudscraper to bypass anti-bot measures and ensure secure web scraping.</li><li>Follows best practices for handling sensitive data obtained during scraping.</li></ul> |
| 📦 | **Dependencies**  | <ul><li>Relies on a variety of dependencies like BeautifulSoup, Pandas, Selenium, and Python-Telegram-Bot for different functionalities.</li><li>Dependencies are managed using requirements.txt and specific YAML files for different scraping tasks.</li></ul> |

---

## Project Structure

```sh
└── geosains_job_bot/
    ├── .github
    │   ├── scrape_indeed.yml
    │   └── workflows
    ├── img
    │   └── ss_checkbox2.png
    ├── requirements.txt
    ├── scrape_disnakerja.py
    ├── scrape_indeed.py
    ├── scrape_jobstreet.py
    ├── scrape_linkedin.py
    ├── scrape_petromindo.py
    └── utils
        ├── .DS_Store
        ├── .gitignore
        ├── __init__.py
        ├── __pycache__
        ├── disnakerja.py
        ├── gsheet_utils.py
        ├── indeed.py
        ├── jobstreet.py
        ├── linkedin.py
        ├── petromindo.py
        └── telegram_utlis.py
```

### Project Index

<details open>
	<summary><b><code>GEOSAINS_JOB_BOT/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Enhance data scraping capabilities by leveraging various libraries like BeautifulSoup, Pandas, and Selenium<br>- Integrate with Google Sheets using gspread and PyDrive2 for seamless data management<br>- Additionally, utilize python-telegram-bot for interactive communication and cloudscraper for web scraping tasks<br>- This file specifies essential dependencies to support these functionalities within the project architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/scrape_petromindo.py'>scrape_petromindo.py</a></b></td>
					<td style='padding: 8px;'>- Scrape and enrich job data from Petromindo, filter and export to Google Sheets<br>- Process jobs asynchronously and log results<br>- Initialize Google Sheets client and handle potential errors<br>- Utilize service account credentials for authentication<br>- Ensure data integrity by avoiding duplicates.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/scrape_linkedin.py'>scrape_linkedin.py</a></b></td>
					<td style='padding: 8px;'>- Scrape LinkedIn job data, enrich it, and export to Google Sheets<br>- Initialize Google Sheets client, handle errors, and set up LinkedIn job search URLs<br>- Use SeleniumBase for web scraping, process job data, and generate log reports asynchronously<br>- Ensure BOT_TOKEN is set for Telegram notifications.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/scrape_disnakerja.py'>scrape_disnakerja.py</a></b></td>
					<td style='padding: 8px;'>- Scrape job data from Disnakerja, filter and enrich it, then export to Google Sheets<br>- Process jobs asynchronously and generate a log report<br>- Handles credentials, error cases, and proxy settings<br>- Integrates with Google Drive and Sheets APIs<br>- Utilizes pandas, gspread, and asyncio for efficient data manipulation and communication.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/scrape_indeed.py'>scrape_indeed.py</a></b></td>
					<td style='padding: 8px;'>- Scrape Indeed job listings, enrich data, and export to Google Sheets<br>- Initialize Google Sheets client, handle errors, and process jobs asynchronously<br>- Utilize SeleniumBase for web scraping and Google APIs for Sheets integration<br>- Ensure data integrity and logging for job processing.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/scrape_jobstreet.py'>scrape_jobstreet.py</a></b></td>
					<td style='padding: 8px;'>- Scrape JobStreet data, enriches it, and exports to Google Sheets<br>- Handles credentials, proxies, and job filtering<br>- Asynchronously processes jobs and logs results<br>- Integrated with Telegram bot for notifications<br>- Manages data flow from web scraping to data enrichment and final reporting.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- utils Submodule -->
	<details>
		<summary><b>utils</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ utils</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/utils/petromindo.py'>petromindo.py</a></b></td>
					<td style='padding: 8px;'>- SummaryThe <code>petromindo.py</code> file in the <code>utils</code> directory of the project is responsible for parsing job information from a single job card on the Petromindo website<br>- It utilizes BeautifulSoup for parsing HTML content and Pandas for structuring the extracted data into a DataFrame<br>- The function <code>parse_petromindo</code> takes a BeautifulSoup Tag object representing a job card and an industries string as input, and returns a DataFrame containing the extracted job information<br>- This file plays a crucial role in extracting and organizing job data from Petromindo, contributing to the overall data processing and analysis capabilities of the project.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/utils/telegram_utlis.py'>telegram_utlis.py</a></b></td>
					<td style='padding: 8px;'>- Send job postings to Telegram chat asynchronously, format messages, and log actions<br>- Process all jobs in a DataFrame, sending messages for each job and collecting logging information<br>- Handle message truncation, construction, and error handling<br>- Utilize asyncio for non-blocking operations.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/utils/gsheet_utils.py'>gsheet_utils.py</a></b></td>
					<td style='padding: 8px;'>- Export data to Google Sheets with ease using the <code>export_to_sheets</code> function in <code>gsheet_utils.py</code><br>- This function allows for seamless interaction with Google Sheets, enabling writing, appending, or reading data based on the specified mode<br>- Simply provide the spreadsheet, sheet name, data frame, and mode to efficiently manage your data within Google Sheets.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/utils/disnakerja.py'>disnakerja.py</a></b></td>
					<td style='padding: 8px;'>- Project SummaryThe <code>disnakerja.py</code> file in the <code>utils</code> directory of the project contains a function <code>parse_disnakerja</code> that is responsible for parsing job card information from Disnakerja website<br>- This function takes a BeautifulSoup Tag object representing a single job card and an industries string as input, and returns a single-row DataFrame containing extracted job information<br>- The function extracts details such as job source, job ID, job URL, and job company from the provided job card.This code file plays a crucial role in the projects architecture by handling the extraction and parsing of job information from Disnakerja, contributing to the overall data processing and analysis pipeline of the application.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/utils/linkedin.py'>linkedin.py</a></b></td>
					<td style='padding: 8px;'>- Extracts job information from LinkedIn job listings and enriches it with detailed job data<br>- The code file <code>utils/linkedin.py</code> utilizes BeautifulSoup and Selenium to scrape job details like title, company, location, salary, and more<br>- It also navigates to job URLs to extract additional information such as seniority level, employment type, and industries, enhancing the job data for analysis.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/utils/jobstreet.py'>jobstreet.py</a></b></td>
					<td style='padding: 8px;'>- Parse and extract job information from JobStreet URLs, enriching data with additional details like seniority level, employment type, and job description<br>- The code interacts with JobStreet pages, retrieves job listings, and formats the data into a structured DataFrame<br>- It handles exceptions and ensures data integrity throughout the process.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/utils/indeed.py'>indeed.py</a></b></td>
					<td style='padding: 8px;'>- SummaryThe <code>indeed.py</code> file in the <code>utils</code> directory of the project is responsible for parsing job card information from Indeed<br>- It utilizes BeautifulSoup to extract job details such as job title, company, location, salary, and more from the provided job card HTML<br>- The extracted data is then structured into a single-row pandas DataFrame, mimicking the functionality of the get_indeed' R function<br>- This file plays a crucial role in fetching and organizing job information from Indeed, contributing to the overall data collection and processing capabilities of the project.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- .github Submodule -->
	<details>
		<summary><b>.github</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ .github</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/.github/scrape_indeed.yml'>scrape_indeed.yml</a></b></td>
					<td style='padding: 8px;'>- Automates scraping job data from Indeed using Selenium and Python<br>- Sets up necessary dependencies, Chrome, and chromedriver<br>- Verifies pytest functionality and Chrome binaries<br>- Executes the scraping process with debug mode enabled, utilizing proxy settings and secret tokens.</td>
				</tr>
			</table>
			<!-- workflows Submodule -->
			<details>
				<summary><b>workflows</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ .github.workflows</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/.github/workflows/scrape_indeed_xfvb.yml'>scrape_indeed_xfvb.yml</a></b></td>
							<td style='padding: 8px;'>- Execute a workflow that scrapes job listings from Indeed, setting up Python, system dependencies, and Chrome<br>- It ensures Python dependencies, checks Chrome binaries, and runs tests with SeleniumBase<br>- Finally, it initiates the job scraping process with debug mode, utilizing proxies and authentication tokens for secure access.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/.github/workflows/scrape_disnakerja.yml'>scrape_disnakerja.yml</a></b></td>
							<td style='padding: 8px;'>- Automates scraping Disnakerja data using scheduled workflows<br>- Sets up Python environment, installs dependencies, Chrome, and chromedriver<br>- Checks Chrome binaries and runs pytest for validation<br>- Executes Python script to scrape data with debug mode, utilizing secret credentials.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/.github/workflows/scrape_linkedin.yml'>scrape_linkedin.yml</a></b></td>
							<td style='padding: 8px;'>- Automate LinkedIn scraping by setting up Python, installing dependencies, checking Chrome binaries, and running the scrape_data.py script<br>- This workflow ensures smooth execution and debugging, enhancing productivity for scraping tasks.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/.github/workflows/scrape_petromindo.yml'>scrape_petromindo.yml</a></b></td>
							<td style='padding: 8px;'>- Automate scraping of Petromindo data using scheduled workflows<br>- Install dependencies, set up Python environment, and ensure Chrome compatibility<br>- Run pytest tests and verify SeleniumBase functionality<br>- Scrape data with provided secrets for authentication.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/.github/workflows/scrape_jobstreet.yml'>scrape_jobstreet.yml</a></b></td>
							<td style='padding: 8px;'>- Automate scraping Jobstreet data using scheduled workflows<br>- Set up Python environment, install dependencies, check Chrome binaries, and run data scraping script<br>- Ensure pytest and Chrome configurations are working seamlessly.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/geosains_job_bot/blob/master/.github/workflows/scrape_indeed_windows2.yml'>scrape_indeed_windows2.yml</a></b></td>
							<td style='padding: 8px;'>- Execute a workflow that scrapes job data from Indeed on Windows using Python 3.11<br>- The workflow runs daily at specific times, installing dependencies, checking code quality, and ensuring SeleniumBase functions correctly<br>- Finally, it executes a Python script to scrape data, utilizing various secret environment variables for authentication.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Pip

### Installation

Build geosains_job_bot from the source and intsall dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/Rachdyan/geosains_job_bot
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd geosains_job_bot
    ```

3. **Install the dependencies:**

<!-- SHIELDS BADGE CURRENTLY DISABLED -->
[![pip][pip-shield]][pip-link]

[pip-shield]: https://img.shields.io/badge/Pip-3776AB.svg?style=flat&logo=pypi&logoColor=white
[pip-link]: https://pypi.org/project/pip/

**Using [pip](https://pypi.org/project/pip/):**

```sh
❯ pip install -r requirements.txt
```



---

## Roadmap

- [ ] **`Task 1`**: Add support for other job sites

---

## Contributing

- **💬 [Join the Discussions](https://github.com/Rachdyan/geosains_job_bot/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/Rachdyan/geosains_job_bot/issues)**: Submit bugs found or log feature requests for the `geosains_job_bot` project.
- **💡 [Submit Pull Requests](https://github.com/Rachdyan/geosains_job_bot/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/Rachdyan/geosains_job_bot
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/Rachdyan/geosains_job_bot/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=Rachdyan/geosains_job_bot">
   </a>
</p>
</details>

---

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Disclaimer

The **geosains_job_bot** is a personal project developed solely for educational purposes. It is not a commercial service. While the bot is designed to aggregate relevant job listings, the creator assumes no liability for:

- The accuracy, completeness, or timeliness of the information provided.
- Any decisions made or actions taken based on the data from this bot.

Please use the information provided as a starting point and always confirm details with the official hiring company.


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
