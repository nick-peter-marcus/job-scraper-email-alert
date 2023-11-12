# Python script for job alerts and email notification.

I built this Python script to get email notifications whenever new job ads have been posted on career sites of companies relevant to me.

There is one central modular script, <b>job_scrape.py</b>, calling the individual functions/scrapers in <i>/websites/</i> which each handle a different webpage.

Each scraper module works as follows:
1. Parse<sup>*</sup> webpages containing current job listings.
2. Process and store job data in a dictionary, utilizing job id (if applicable) as key.
3. Compare the dict of current postings with the stored version of the last execution.
4. Extract only new postings and prepare their details to be displayed in the email.
5. Returns a dictionary containing email-texts in plain and html format, or None when there are no now new jobs.

The individual email texts are joined in job_scrape.py as a MIMEMultipart class, a secured SMTP connection is started, and the email will be send.

This script is executed every 24h as a scheduled task on <a href="https://www.pythonanywhere.com/">PythonAnywhere</a>.

<i><sup>*</sup>Note:
For static webpages, the <b>BeautifulSoup</b> package is used to scrape and parse HTML-documents.
For dynamic webpages, <b>Selenium</b>'s WebDriver is utilized, initiating a headless browser to capture the rendered data.</i>