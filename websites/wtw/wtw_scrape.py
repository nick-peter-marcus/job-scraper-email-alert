def wtw():
    # import libraries
    import json
    import pickle
    import requests

    company_name = 'wtw'


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    r = requests.get('https://jobsapi-internal.m-cloud.io/api/job?callback=jobsCallback&latitude=42.3600825&longitude=-71.0588801&LocationRadius=25&Limit=40&Organization=2045&offset=1').text
    # returns job postings in JSON format, but wrapped in 'jobsCallback(...)' which needs to be removed
    r_json_ready = r[:-1].replace('jobsCallback(', '')
    r_json = json.loads(r_json_ready)

    jobs = r_json['queryResult']

    # Extraxt title, link, city, id, and date
    current_jobs_dict = {}
    for job in jobs:
        id = job['id']
        title = job['title']
        link = job['url']
        location = job['primary_city']
        date_posted = job['open_date']
        
        # add to dict of jobs being scraped
        current_jobs_dict.update({id: {'title': title,
                                         'location': location,
                                         'date_posted': date_posted,
                                         'link': link}})

    
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
    new_jobs = [job for job in current_jobs_dict if job not in saved_jobs_dict]

    # return dict with new job postings if any, otherwise return None
    if new_jobs:
        return {job: current_jobs_dict[job] for job in new_jobs}
    else:
        return None