def greenjobs_de():
    # import libraries
    import os
    import pickle
    import requests
    from bs4 import BeautifulSoup

    company_name = "greenjobs_de"
    FILE_PATH = os.path.abspath(os.path.dirname(__file__))
    
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

        job_rows = soup.find_all("div", class_="jobitem")
        n_jobs_found += len(job_rows)

        for job_row in job_rows[:4]:
            link = job_row.find("a")["href"].replace(" ", "%20")
            title = job_row.find("a").text.strip()
            company_location = job_row.text.strip()
            company_location = company_location.replace(title, "")
            company_location = company_location.replace("Angebot von eejobs.de: Öffnet sich in neuem Fenster", "")
            company, location = company_location.split(" | ")

            current_jobs_dict.update({link: {"title": title,
                                             "company": company,
                                             "location": location,
                                             "date_posted": "N/A",
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
    summary = f"{n_jobs_found} jobs found, {n_jobs_scraped} scraped, {len(current_jobs_dict)} stored, {len(new_jobs)} new."
    
    # return touple of summary and dict with new job postings if any, otherwise return None
    return (summary, new_jobs)
