def gfk():
    # import libraries
    import pickle 
    import re
    import requests
    from bs4 import BeautifulSoup
    from datetime import timedelta, date

    company_name = 'gfk'


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    r = requests.get('https://www.gfk.com/careers/search-for-jobs?country_codes29=country_codesUS').text
    soup = BeautifulSoup(r, 'html.parser')
    jobs = soup.find_all('a', class_='job_item')

    # Extraxt title, link, city, id, and date
    current_jobs_dict = {}
    for job in jobs:
        title = job.find_all('h6')[0].text.strip()
        link = 'https://www.gfk.com' + job['href']
        location_raw, id_raw, days_ago_raw = job.find_all('p')
        location = location_raw.text.strip().replace('\n', '').replace('  ', '').replace(',', ', ')
        id = id_raw.text.strip()
        days_ago = int(re.findall('\d+', days_ago_raw.text)[0])
        date_posted = date.today() - timedelta(days=days_ago)
        
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