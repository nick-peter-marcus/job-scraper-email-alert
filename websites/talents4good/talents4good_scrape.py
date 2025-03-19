def talents4good():
    # import libraries
    import os
    import pickle
    import re
    import requests
    from bs4 import BeautifulSoup

    company_name = "talents4good"
    FILE_PATH = os.path.abspath(os.path.dirname(__file__))


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    url = "https://jobs.talents4good.org/jm-ajax/get_listings/search_location=Berlin&filter_job_type%5B%5D=remote&filter_job_type%5B%5D=hybrid&filter_job_type%5B%5D=vollzeit&filter_job_type%5B%5D="
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.json()["html"], 'html.parser')

    job_listings = soup.find_all("li")

    # loop through job postings, store details in dict
    current_jobs_dict = {}

    for job_listing in job_listings:
        link = job_listing.find("a")["href"]
        title = job_listing.find("h3", class_="t4g-job-title").text.strip()
        company = job_listing.find("div", class_ = "t4g-company-name").text.strip()
        location = job_listing.find("span", class_ = "t4g-job-location").text.strip()
        date_posted = job_listing.find("time")["datetime"]

        status = job_listing.find("span", class_ = "acf_job_status").text.strip()
        job_type = job_listing.find("span", class_ = "t4g-job-types").text.strip()
        job_type_clean = re.sub(r"\s{2,}", " | ", job_type)
        job_details = f"{job_type_clean} | {status}"

        current_jobs_dict.update({link: {"title": title,
                                         "company": company,
                                         "location": location,
                                         "date_posted": date_posted,
                                         "details": job_details,
                                         "link": link}})


    """
    LOAD RESULTS OF LAST EXECUTION - STORE CURRENT RESULTS
    """
    # open last saved job postings (create empty dict if nonexistent)
    try:
        with open(f'{FILE_PATH}/{company_name}_current_jobs_dict.pkl', 'rb') as f:
            saved_jobs_dict = pickle.load(f)
    except FileNotFoundError:
        saved_jobs_dict = {} 

    # store current state of job postings for next execution
    with open(f'{FILE_PATH}/{company_name}_current_jobs_dict.pkl', 'wb') as f:
        pickle.dump(current_jobs_dict, f)


    """
    FILTER JOBS AND RETURN RESULTS AS DICTIONARY
    """
    # create list containing only ids of new jobs
    new_jobs = {job: current_jobs_dict[job] for job in current_jobs_dict if job not in saved_jobs_dict}
    # create written summary
    summary = f"{len(job_listings)} jobs found, {len(current_jobs_dict)} scraped, {len(new_jobs)} new jobs."

    # return touple of summary and dict with new job postings if any, otherwise return None
    return (summary, new_jobs)
