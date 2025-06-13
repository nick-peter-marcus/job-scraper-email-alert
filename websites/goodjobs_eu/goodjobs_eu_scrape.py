def goodjobs_eu():
    # import libraries
    import math
    import os
    import pickle
    import re
    import requests
    from bs4 import BeautifulSoup

    company_name = "goodjobs_eu"
    FILE_PATH = os.path.abspath(os.path.dirname(__file__))


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

        for jobcard in jobcards:
            title = jobcard.find("h3").text.strip()
            link = jobcard["href"]

            job_details = jobcard \
            .find("div") \
            .find("div") \
            .find_all("div", recursive=False)[2] \
            .find_all("div", recursive=False)
            
            salary, location, remote, date_posted, full_time, job_type = None, None, None, None, None, None

            if len(job_details) == 6:
                salary = job_details[0].find("span").text.strip()
                location = job_details[1].find("span").text.strip()
                remote = job_details[1].find("p").text.strip().replace("| ", "")
                date_posted = job_details[2].text.strip()
                full_time = job_details[3].find("p").text.strip()
                job_type = job_details[4].text.strip()
            if len(job_details) <= 5:
                location = job_details[0].find("span").text.strip()
                remote = job_details[0].find("p").text.strip().replace("| ", "")
                date_posted = job_details[1].text.strip()
                full_time = job_details[2].find("p").text.strip()
                job_type = job_details[3].text.strip()

            company = jobcard \
                .find("div") \
                .find_all("div", recursive=False)[1] \
                .find("p") \
                .text.strip()
            
            additional_details = " | ".join([remote, full_time])
            if job_type:
                additional_details += f" | {job_type}"
            if salary:
                additional_details += f" | {salary}"
                
            current_jobs_dict.update({link: {"title": title,
                                             "company": company,
                                             "location": location,
                                             "date_posted": date_posted,
                                             "details": additional_details,
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
    summary = f"{n_jobs} jobs listed, {len(current_jobs_dict)} scraped, {len(new_jobs)} new jobs."

    # return touple of summary and dict with new job postings if any, otherwise return None
    return (summary, new_jobs)
