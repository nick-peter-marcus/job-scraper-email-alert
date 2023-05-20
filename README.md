# App for job alerts and email notification.

job_scrape.py acts as the central script, collecting info from individual scraping modules under <i>/websites/</i>, which each handles a different webpage (i.e. career sites from relevant companies). 

Each scraper module works as follows:
1. Scrape job info from webpage containing current job listings.
2. Process and store info in a dictionary, having the job id (if applicable) as key.
3. Compare the dict of scraped postings with the version of last execution.
4. When new job postings are found, their info is collected in a string for later use in an email.
5. Returns a dictionary containing email-text in plain and html format, or None when there are no updates.

After collecting the info of each module, job_scrape.py gathers the new jobs in one email message (a MIMEMultipart class) and sends it via email.

This script is run as a scheduled task on <a href="https://www.pythonanywhere.com/">PythonAnywhere</a>.