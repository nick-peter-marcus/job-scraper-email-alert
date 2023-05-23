def gfk():
    # import libraries
    import pickle 
    import re
    import requests
    from bs4 import BeautifulSoup
    from datetime import timedelta, date

    # get and parse webpage
    r = requests.get('https://www.gfk.com/careers/search-for-jobs?locations5=locationsBoston').text
    #r = requests.get('https://www.gfk.com/careers/search-for-jobs').text
    soup = BeautifulSoup(r, 'html.parser')
    jobs = soup.find_all('a', class_='job_item')

    # open last saved job postings (create empty dict if nonexistent)
    try:
        with open('websites/gfk/gfk_current_jobs_dict.pkl', 'rb') as f:
            saved_jobs_dict = pickle.load(f)
    except FileNotFoundError:
        saved_jobs_dict = {}
    
    # create dict to store scraped jobs
    current_jobs_dict = {}

    for job in jobs:
        # Extraxt title, link, city, id, and date
        title = job.find_all('h6')[0].text.strip()
        link = 'https://www.gfk.com' + job['href']
        city_raw, id_raw, days_ago_raw = job.find_all('p')
        city = city_raw.text.strip().replace('\n', '').replace('  ', '').replace(',', ', ')
        id = id_raw.text.strip()
        days_ago = int(re.findall('\d+', days_ago_raw.text)[0])
        date_posted = date.today() - timedelta(days=days_ago)
        
        # add to dict of jobs being scraped
        current_jobs_dict.update({id: {'title': title, 
                                       'city': city, 
                                       'date_posted': date_posted, 
                                       'link': link}})

    # compare current jobs with last saved jobs (no changes -> return None and end function)
    if current_jobs_dict == saved_jobs_dict:
        print('No changes at GfK.')
        return None
    else:
        # create list of ids from new jobs
        new_jobs = [job for job in current_jobs_dict if job not in saved_jobs_dict]
        # store current state of job postings for next execution
        with open('websites/gfk/gfk_current_jobs_dict.pkl', 'wb') as f:
            pickle.dump(current_jobs_dict, f)

    if new_jobs:
        # create email message
        text_body = 'New Jobs at GfK:\n'
        html_body = '<h1>New Jobs at GfK:</h1>\n'
        for job in new_jobs:
            text_body += (f'Title: {current_jobs_dict[job]["title"]}:\n'                          
                          f'Link: {current_jobs_dict[job]["link"]}\n'
                          f'Posted on: {current_jobs_dict[job]["date_posted"]}\n\n'
                         )
            html_body += (f'<a href = "{current_jobs_dict[job]["link"]}">'
                          f'<b>{current_jobs_dict[job]["title"]}</b>'
                          f'</a><br>'
                          f'Posted on: {current_jobs_dict[job]["date_posted"]}<br><br>'
                         )
        print('New jobs at GfK.')
        return {"text": text_body, "html" : html_body}
    else:
        print('No new jobs at GfK.')
        return None

