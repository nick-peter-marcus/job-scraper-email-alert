def chewy():
    # import libraries
    import math
    import pickle
    from datetime import datetime
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    company_name = 'chewy'


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # create instance of Chrome WebDriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    # navigate to webpage
    driver.get('https://careers.chewy.com/us/en/search-results?keywords=&p=ChIJGzE9DS1l44kRoOhiASS_fHg&location=Boston,%20MA,%20USA')
    
    # check job count and determine number of pages to search through (here: 10 postings per page)
    n_jobs = int(driver.find_element(By.CLASS_NAME, 'result-count').text)
    n_pages = math.ceil(n_jobs/10)

    # scrape jobs on all search result pages
    current_jobs_dict = {}
    for page in range(1,n_pages+1):
        jobs = driver.find_elements(By.CLASS_NAME, 'jobs-list-item')
        for job in jobs:
            # extraxt id, title, city, link and date
            id = job.find_element(By.TAG_NAME, 'a').get_attribute('data-ph-at-job-id-text')
            title = job.find_element(By.TAG_NAME, 'a').text
            link = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
            location = job.find_element(By.TAG_NAME, 'a').get_attribute('data-ph-at-job-location-text')
            date_posted_raw = job.find_element(By.TAG_NAME, 'a').get_attribute('data-ph-at-job-post-date-text')
            date_posted = datetime.strptime(date_posted_raw, '%Y-%m-%dT%H:%M:%S.%f%z').date()
            
            # add to dict of jobs being scraped
            current_jobs_dict.update({id: {'title': title, 
                                           'location': location, 
                                           'date_posted': date_posted, 
                                           'link': link}})
        
        # if applicable, navigate to next page of search results
        if page < n_pages:
            next_page = str(page+1)
            # Last page sometimes not existent, NoSuchElementException thrown.
            try:
                next_page_link = driver.find_element(By.LINK_TEXT, next_page)
            except:
                pass
            else:
                next_page_link.click()

    # Quit WebDriver session
    driver.quit()


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