# Python script for job alerts and email notification.

I built this Python script to get email notifications whenever new job ads have been posted on career sites of companies relevant to me.

There is one central modular script, <b>job_scrape.py</b>, calling the individual functions/scrapers in <i>/websites/</i> which each handles scraping a different webpage.

Each scraper module works as follows:
1. Parse<i>*</i> webpages containing current job listings.
2. Process and store job details in a dictionary.
3. Compare the current postings with those stored at the last execution.
4. Extract only new postings and, if applicable, filter on relevant criteria (e.g. location).
5. Return a dictionary containing the details of the filtered postings, or None when there are no now new jobs.

The results are then joined as formatted email texts (MIMEMultipart class) in job_scrape.py. A secured SMTP connection will be started, and the email will be send.

This script is executed every 24h as a scheduled task on <a href="https://www.pythonanywhere.com/">PythonAnywhere</a>.

<i><sup>*</sup>Note:
For static webpages, the <b>BeautifulSoup</b> package is used to scrape and parse HTML-documents.
For dynamic webpages, <b>Selenium</b>'s WebDriver is utilized, initiating a headless browser to capture rendered data.</i>