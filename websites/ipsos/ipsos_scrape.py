def ipsos():
    # import libraries
    import os
    import pickle
    import requests

    company_name = "ipsos"
    FILE_PATH = os.path.abspath(os.path.dirname(__file__))


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    url = "https://ecqf.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_2001,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,locationId=300000134782977,sortBy=POSTING_DATES_DESC"
    r = requests.get(url, headers=headers)

    job_listings = r.json()["items"][0]["requisitionList"]

    # loop through job postings, store details in dict
    current_jobs_dict = {}
    company = "Ipsos"
    location = "Berlin"

    for job_listing in job_listings:
        id = job_listing["Id"]
        link = f"https://ecqf.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/de/sites/IpsosCareers/job/{id}/"
        title = job_listing["Title"]
        date_posted = job_listing["PostedDate"]

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
