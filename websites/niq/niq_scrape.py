def niq():
    # import libraries
    import os
    import pickle
    import requests
    from bs4 import BeautifulSoup

    company_name = "niq"
    FILE_PATH = os.path.abspath(os.path.dirname(__file__))


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    url = "https://nielseniq.com/?s=&market=global&language=en&orderby=date&order=DESC&post_type=career_job&job_locations=germany&job_teams=&job_types="
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    
    n_jobs = soup.find("h1", class_="h5")["data-posts-found"]
    job_listings = soup.find_all("article")

    # loop through job postings, store details in dict
    current_jobs_dict = {}
    company = "NiQ"

    for job_listing in job_listings:
        link = job_listing.find("a")["href"]
        title = job_listing.find("h5").text.strip()
        location = job_listing.find("span", class_="tax-term").text
        date_posted = "N/A"

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
    summary = f"{n_jobs} listed, {len(job_listings)} jobs found, {len(current_jobs_dict)} scraped, {len(new_jobs)} new jobs."

    # return touple of summary and dict with new job postings if any, otherwise return None
    return (summary, new_jobs)
