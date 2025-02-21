def greenjobs_de():
    # import libraries
    import pickle
    import math
    import re
    import requests
    from bs4 import BeautifulSoup

    company_name = "greenjobs_de"


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}

    urls = ["https://www.greenjobs.de/angebote/index.html?s=&loc=Berlin%2C+Deutschland&countrycode=de&dist=20&lng=13.39894&lat=52.51089",
            "https://www.greenjobs.de/angebote/index.html?s=&loc=remote&countrycode=de&dist=10&lng=&lat="]
    
    # loop through pages, extract all job postings, and store in dict
    current_jobs_dict = {}
    n_jobs_found = 0
    n_jobs_scraped = 0

    for url in urls:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        job_table = soup.find("table", class_="overview_jobs")
        job_rows = job_table.find_all("tr")
        n_jobs_found += len(job_rows)

        for job_row in job_rows:
            link = job_row.find("a")["href"].replace(" ", "")

            tds = job_row.find_all("td")
            if len(tds) <= 1:
                n_jobs_found -= 1
                continue
            n_jobs_scraped += 1

            title = tds[0].text.replace("Angebot von eejobs.de: Öffnet sich in neuem Fenster", "").strip()
            company = tds[2].text.strip()
            zip_code = tds[3].text.strip()
            cities = tds[4].text.strip()
            deadline = tds[5].text.strip()

            current_jobs_dict.update({link: {"title": title,
                                             "company": company,
                                             "location": cities,
                                             "date_posted": deadline,
                                             "link": link}})

    """
    LOAD RESULTS OF LAST EXECUTION - STORE CURRENT RESULTS
    """
    # open last saved job postings (create empty dict if nonexistent)
    try:
        with open(f'websites/{company_name}/{company_name}_current_jobs_dict.pkl', 'rb') as f:
            saved_jobs_dict = pickle.load(f)
    except FileNotFoundError:
        saved_jobs_dict = {} 

    # store current state of job postings for next execution
    with open(f'websites/{company_name}/{company_name}_current_jobs_dict.pkl', 'wb') as f:
        pickle.dump(current_jobs_dict, f)


    """
    FILTER JOBS AND RETURN RESULTS AS DICTIONARY
    """
    # create list containing only ids of new jobs
    new_jobs = {job: current_jobs_dict[job] for job in current_jobs_dict if job not in saved_jobs_dict}
    
    # return dict with new job postings if any, otherwise return None
    if new_jobs:
        summary = f"{n_jobs_found} jobs found, {n_jobs_scraped} scraped, {len(current_jobs_dict)} stored, {len(new_jobs)} new jobs."
        return (summary, new_jobs)
    else:
        return (None, None)
