def toast():
    # import libraries
    import pickle
    import requests
    from bs4 import BeautifulSoup

    company_name = 'toast'


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    r = requests.get('https://careers.toasttab.com/jobs/search?page=1&country_codes%5B%5D=US').text
    soup = BeautifulSoup(r, 'html.parser')

    # check for additional pages, i.e. job listings displayed on several pages, and store urls in list
    add_pages = soup.find_all('a', class_='page-link')
    if add_pages:
        urls = ['https://careers.toasttab.com' + x['href'] for x in add_pages[1:-1]]
    else:
        urls = ['https://careers.toasttab.com/jobs/search?page=1&country_codes%5B%5D=US']
    
    # loop through list of urls, extract all job postings, and store in dict
    current_jobs_dict = {}
    for url in urls:
        # get and parse webpage
        r = requests.get(url).text
        soup = BeautifulSoup(r, 'html.parser')
        jobs = soup.find_all('div', class_='card-body job-search-results-card-body')

        for job in jobs:
            # Extraxt title, link, city (there is no id and date)
            title = job.find('a').text
            link = job.find('a')['href']
            location = job.find('span').text.strip()
            date_posted = None
            
            # add to dict of jobs being scraped (as there is no id, link will be used as unique identifier/key)
            current_jobs_dict.update({link: {'title': title,
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

    # Filter jobs (dict keys) according to filter condition (here: job location)
    filter_cond = ['Remote', 'Boston, Massachusetts, United States']
    new_filtered_jobs = [job for job in new_jobs if current_jobs_dict[job]['location'] in filter_cond]

    # return dict with new job postings if any, otherwise return None
    if new_filtered_jobs:
        return {job: current_jobs_dict[job] for job in new_filtered_jobs}
    else:
        return None
