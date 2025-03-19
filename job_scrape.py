def main():
    # import libraries
    import os
    import re
    import smtplib
    from dotenv import load_dotenv
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    # import scraping modules
    from websites.goodjobs_eu.goodjobs_eu_scrape import goodjobs_eu
    from websites.greenjobs_de.greenjobs_de_scrape import greenjobs_de
    from websites.talents4good.talents4good_scrape import talents4good


    # create function for flagging titles that contain certain words (desired + undesired)
    def contains_words(input_string: str, search_words: list) -> bool:
        """ Checks whether a string contains specified key words
        Args: 
            input_string (str): The text to be searched in
            search_words (list): A list of words to be searched
        Returns:
            bool: True if any of the search_words appear in input_string.
        """
        re_search_terms = "|".join(search_words)
        matches = re.findall(re_search_terms, input_string.lower())
        return len(matches) > 0

    # define key words for relevant (pos) and irrelevant (neg) flagging
    pos_search_terms = ["data", "analyst", "analysis", "analytics", "machine learning"]
    pos_search_terms.extend(["daten", "analyse", "auswertung", "analytiker", "statistik"])
    pos_search_terms.extend(["marktforschung", "markt", "forschung", "market", "research"])
    pos_search_terms.extend([" ki ", " ai ", " ml "])
    
    neg_search_terms = ["trainee", "student", "studierend", "praktikum", "praktikant"]


    """
    POPULATE EMAIL BODY TEXTS WITH RESULTS OF SCRAPER MODULES
    """
    # initialize empty lists to store body texts for job alert message
    ls_text_body = []
    ls_html_body = []
    n_new_jobs_total = 0

    # call scraping function of each website (return dictionary)
    company_funcs = {'Goodjobs EU': goodjobs_eu,
                     'Greenjobs DE': greenjobs_de,
                     'Talents4Good': talents4good}

    for website_name, website_func in company_funcs.items():
        # make scraping function call.
        summary, new_company_jobs = website_func()
        print(f'{website_name}: {summary}')

        # skip if there are no new jobs
        n_new_company_jobs = len(new_company_jobs)
        if n_new_company_jobs == 0:
            continue

        # add sorting and color coding by relevance (acc. to search terms defined above)
        for job_details in new_company_jobs.values():
            # initiate key - value pairs
            job_details['relevance'] = 0
            job_details['font_style'] = ''
            # overwrite default if job title contains relevant words
            if contains_words(job_details['title'], pos_search_terms):
                job_details['relevance'] = 1
                job_details['font_style'] = 'style="color:green;"'
            # overwrite default or positive relevance if negative terms are present
            if contains_words(job_details['title'], neg_search_terms):
                job_details['relevance'] = -1
                job_details['font_style'] = 'style="color:purple;"'

        # sort dictionairy based on relevance (desc) and job title
        new_company_jobs_sorted = dict(sorted(new_company_jobs.items(),
                                              key=lambda x: (-x[1]['relevance'], x[1]['title'])))

        # initialize email text sections per company scraped
        text_body_comp = f'{n_new_company_jobs} new jobs at {website_name}:\n{summary}\n\n'
        html_body_comp = (f'<big><b>{n_new_company_jobs} new jobs at {website_name}:</b></big> <br>'
                          f'<small><i>{summary}</i></small> <br><br>')

        # add information for each job to company text section
        for job_details in new_company_jobs_sorted.values():
            link = job_details['link']
            title = job_details['title']
            company = job_details['company']
            location = job_details['location']
            date = job_details['date_posted']
            details = job_details['details'] if 'details' in job_details else None
            font_style = job_details['font_style']

            # Add job info to mail bodies
            text_body_comp += (f'Title: {title}:\nLink: {link}\nLocation: {location}')
            html_body_comp += (f'<a href="{link}" {font_style}><b>{title}</b></a>'
                               f'<br>Company: {company}'
                               f'<br>Location(s): {location}'
                               f'<br>Posted/Deadline: {date}')
            
            # Add element "details" to bodies if existent
            text_body_comp += f'\nDetails: {details}\n\n' if details else '\n\n'
            html_body_comp += f'<br>Details: {details}<br><br>' if details else '<br><br>'
        
        ls_text_body.append(text_body_comp)
        ls_html_body.append(html_body_comp)
        
        n_new_jobs_total += n_new_company_jobs
        
    # create final body messages by joining individual company body texts
    text_body = '<br><hr><br>'.join(ls_text_body)
    html_body = '<br><hr><br>'.join(ls_html_body)


    """
    SET UP CONNECTION AND SEND EMAIL
    """
    # send job alert per mail if new jobs were found (i.e. if bodies are not empty)
    if n_new_jobs_total == 0:
        print("No new jobs.")
        return
    
    # include mail account credentials from environment variables
    load_dotenv()
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_TO = os.getenv('EMAIL_TO')
    
    # set up email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'JOB ALERT ({n_new_jobs_total} new)'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_TO
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    # send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_TO, msg.as_string())

    print("New jobs, email notification sent.")


if __name__ == '__main__':
    main()