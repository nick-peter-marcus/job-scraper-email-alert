def toast():
    # import libraries
    import pickle
    import requests
    from bs4 import BeautifulSoup

    # open last saved job postings (create empty dict if nonexistent)
    try:
        with open('websites/toast/toast_current_jobs_dict.pkl', 'rb') as f:
            saved_jobs_dict = pickle.load(f)
    except FileNotFoundError:
        saved_jobs_dict = {}
 
    # create dict to store scraped jobs
    current_jobs_dict = {}
   
    # get and parse webpage
    r = requests.get('https://careers.toasttab.com/jobs/search?page=1&country_codes%5B%5D=US').text
    soup = BeautifulSoup(r, 'html.parser')

    # check for additional pages, i.e. job listings displayed on several pages and store urls in list
    add_pages = soup.find_all('a', class_='page-link')
    if add_pages:
        urls = ['https://careers.toasttab.com' + x['href'] for x in add_pages[1:-1]]
    else:
        urls = ['https://careers.toasttab.com/jobs/search?page=1&country_codes%5B%5D=US']
    
    # loop through list of urls, extract all job postings, and store in dict
    for url in urls:
        # get and parse webpage
        r = requests.get(url).text
        soup = BeautifulSoup(r, 'html.parser')
        jobs = soup.find_all('div', class_='card-body job-search-results-card-body')

        for job in jobs:
            # Extraxt title, link, city (there is no id and date)
            title = job.find('a').text
            link = job.find('a')['href']
            city = job.find('span').text.strip()
            
            # add to dict of jobs being scraped (as there is no id, link will be used as unique identifier/key)
            current_jobs_dict.update({link: {'title': title, 'city': city}})

    # TO DO: FILTER LIST BASED ON CRITERIA: city in [Boston, NY, RI, Remote]

    # compare current jobs with last saved jobs (no changes -> return None and end function)
    if current_jobs_dict == saved_jobs_dict:
        print('No changes at Toast.')
        return None
    else:
        # create list of ids (here: link) from new jobs
        new_jobs = [job for job in current_jobs_dict if job not in saved_jobs_dict]
        # store current state of job postings for next execution
        with open('websites/toast/toast_current_jobs_dict.pkl', 'wb') as f:
            pickle.dump(current_jobs_dict, f)

    if new_jobs:
        # create email message (CHANGE ID; ADD LOCATION)
        text_body = 'New Jobs at Toast:\n'
        html_body = '<h1>New Jobs at Toast:</h1>\n'
        for job in new_jobs:
            text_body += (f'Title: {current_jobs_dict[job]["title"]}:\n'
                          f'Link: {job}\n'
                          f'Location: {current_jobs_dict[job]["city"]}\n\n'
                         )
            html_body += (f'<a href = "{job}">'
                          f'<b>{current_jobs_dict[job]["title"]}</b>'
                          f'</a><br>'
                          f'Location: {current_jobs_dict[job]["city"]}<br><br>'
                         )
        print('New jobs at Toast.')
        return {"text": text_body, "html" : html_body}
    else:
        print('No new jobs at Toast.')
        return None
