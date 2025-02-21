def goodjobs_eu():
    # import libraries
    import pickle
    import math
    import re
    import requests
    from bs4 import BeautifulSoup

    company_name = "goodjobs_eu"


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    base_url = "https://goodjobs.eu/jobs?places=Berlin&distance=10&places_type=city&countrycode=DE&latlng=52.510885%2C13.3989367&job_search=1&sort_by_newest=true&num=25"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    # get number of jobs and determine number of pages to scrape
    n_jobs_string = soup.find("nav", attrs={"role": "navigation"}).text.strip()
    n_jobs = int(re.match(r"\d*", n_jobs_string)[0])

    JOBS_PER_PAGE = 25
    n_pages = math.ceil(n_jobs/JOBS_PER_PAGE)
    
    # loop through pages, extract all job postings, and store in dict
    current_jobs_dict = {}

    for page in range(1, n_pages+1):
        url = f"{base_url}&page={page}"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        
        jobcards = soup.find_all("a", class_="jobcard")
        print(f"Scraping page {page}/{n_pages}, {len(jobcards)} jobs found.")

        for jobcard in jobcards:
            title = jobcard.find("h3").text.strip()
            link = jobcard["href"]

            job_details = jobcard.find_all("div", recursive=False)[0].find_all("div", recursive=False)[0].find_all("div", recursive=False)[1].find_all("div", recursive=False)
            
            location_spans = job_details[0].find("div").find_all("span", recursive=False)
            location = ""
            for location_span in location_spans:
                location += location_span.text.strip()
            remote = job_details[0].find("div").find("p").text.strip().replace("| ", "")
            date_posted = job_details[1].text.strip()
            full_time = job_details[2].text.strip()
            language = job_details[3].text.strip()
            try:
                job_type = job_details[4].text.strip()
            except:
                job_type = "N/A"
            
            company = jobcard.find_all("div", recursive=False)[0].find_all("div", recursive=False)[1].find("p").text.strip()

            current_jobs_dict.update({link: {"title": title,
                                             "company": company,
                                             "location": location,
                                             "date_posted": date_posted,
                                             "details": " | ".join([remote, full_time, job_type]),
                                             "link": link}})

    print(f"Scraping completed, {len(current_jobs_dict)} jobs stored.")
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
        summary = f"{n_jobs} jobs found, {len(current_jobs_dict)} scraped, {len(new_jobs)} new jobs."
        return summary, new_jobs
    else:
        return None
