def index_de():
    # import libraries
    import os
    import pickle
    import requests
    from bs4 import BeautifulSoup

    company_name = "index_de"
    FILE_PATH = os.path.abspath(os.path.dirname(__file__))


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    url = "https://jobs.index.de/de"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    
    job_listings = soup.find_all("div", class_="portlet")[1:]

    # loop through job postings, store details in dict
    current_jobs_dict = {}
    company = "index"
    date_posted = "N/A"

    for job_listing in job_listings:
        job_title_link = job_listing.find("div", class_="caption")
        title = job_title_link.text.strip()
        rel_link = job_title_link.find("a")["href"]
        link = f"https://jobs.index.de{rel_link}"

        location_details_div = job_listing.find("div", class_="portlet-body")
        location_details = location_details_div.find_all("span")
        location = " | ".join([l.text.strip() for l in location_details[1:-1]])
        if location == "":
            location = "Berlin (not further specified)"        

        current_jobs_dict.update({link: {"title": title,
                                         "company": company,
                                         "location": location,
                                         "date_posted": date_posted,
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
