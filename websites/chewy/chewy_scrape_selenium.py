def chewy():
    # import libraries
    import math
    import pickle
    from datetime import datetime
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    # open last saved job postings (create empty dict if nonexistent)
    try:
        with open('websites/chewy/chewy_current_jobs_dict.pkl', 'rb') as f:
            saved_jobs_dict = pickle.load(f)
    except FileNotFoundError:
        saved_jobs_dict = {}
 
    # create dict to store scraped jobs
    current_jobs_dict = {}
  
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
    for page in range(1,n_pages+1):
        jobs = driver.find_elements(By.CLASS_NAME, 'jobs-list-item')

        for job in jobs:
            # extraxt id, title, city, link and date
            id = job.find_element(By.TAG_NAME, 'a').get_attribute('data-ph-at-job-id-text')
            title = job.find_element(By.TAG_NAME, 'a').text
            city = job.find_element(By.TAG_NAME, 'a').get_attribute('data-ph-at-job-location-text')
            date_posted_raw = job.find_element(By.TAG_NAME, 'a').get_attribute('data-ph-at-job-post-date-text')
            date_posted = datetime.strptime(date_posted_raw, '%Y-%m-%dT%H:%M:%S.%f%z').date()
            link = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
            
            # add to dict of jobs being scraped
            current_jobs_dict.update({id: {'title': title, 
                                           'city': city, 
                                           'date_posted': date_posted, 
                                           'link': link}})
        
        # if applicable, navigate to next page of search results
        if page < n_pages:
            next_page = str(page+1)
            next_page_link = driver.find_element(By.LINK_TEXT, next_page)
            next_page_link.click()

    # Quit WebDriver session
    driver.quit()

    # compare current jobs with last saved jobs (no changes -> return None and end function)
    if current_jobs_dict == saved_jobs_dict:
        print('No changes at Chewy.')
        return None
    else:
        # create list of ids from new jobs
        new_jobs = [job for job in current_jobs_dict if job not in saved_jobs_dict]
        # store current state of job postings for next execution
        with open('websites/chewy/chewy_current_jobs_dict.pkl', 'wb') as f:
            pickle.dump(current_jobs_dict, f)

    if new_jobs:
        # create email message
        text_body = 'New Jobs at Chewy:\n'
        html_body = '<h1>New Jobs at Chewy:</h1>\n'
        for job in new_jobs:
            text_body += (f'Title: {current_jobs_dict[job]["title"]}:\n'
                          f'Link: {current_jobs_dict[job]["link"]}\n'
                          #f'Location: {current_jobs_dict[job]["city"]}\n'
                          f'Posted on: {current_jobs_dict[job]["date_posted"]}\n\n'
                         )
            html_body += (f'<a href = "{current_jobs_dict[job]["link"]}">'
                          f'<b>{current_jobs_dict[job]["title"]}</b>'
                          f'</a><br>'
                          #f'Location: {current_jobs_dict[job]["city"]}<br>'
                          f'Posted on: {current_jobs_dict[job]["date_posted"]}<br><br>'
                         )
        print('New jobs at Chewy.')
        return {"text": text_body, "html" : html_body}
    else:
        print('No new jobs at Chewy.')
        return None