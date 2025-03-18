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


    """
    POPULATE EMAIL BODY TEXTS WITH RESULTS OF SCRAPER MODULES
    """
    # initialize empty lists to store body texts for job alert message
    ls_text_body = []
    ls_html_body = []
    n_new_jobs_total = 0

    # call scraping function of each website (return dictionary)
    company_funcs = {'Goodjobs EU': goodjobs_eu,
                     'Greenjobs DE': greenjobs_de}

    for website_name, website_func in company_funcs.items():
        # make scraping function call.
        summary, new_company_jobs = website_func()
        print(f'{website_name}: {summary}')

        # skip if there are no new jobs
        n_new_company_jobs = len(new_company_jobs)
        if n_new_company_jobs == 0:
            continue

        # initialize email bodies per company scraped
        text_body_comp = f'{n_new_company_jobs} new jobs at {website_name}:\n{summary}\n\n'
        html_body_comp = (f'<big><b>{n_new_company_jobs} new jobs at {website_name}:</b></big> <br>'
                          f'<small><i>{summary}</i></small> <br><br>')

        # gather information for each job
        for job_details in new_company_jobs.values():
            link = job_details['link']
            title = job_details['title']
            company = job_details['company']
            location = job_details['location']
            date = job_details['date_posted']
            details = job_details['details'] if 'details' in job_details else None

            # Highlight titles if search words appear
            pos_search_terms = ["data", "analyst", "analysis", "analytics", "machine learning"]
            pos_search_terms.extend(["daten", "analyse", "auswertung", "analytiker", "statistik"])
            pos_search_terms.extend(["marktforschung", "markt", "forschung", "market", "research"])
            pos_search_terms.extend([" ki ", " ai ", " ml "])
            
            neg_search_terms = ["trainee", "student", "studierend", "praktikum", "praktikant"]

            highlight_job_pos = contains_words(title, pos_search_terms)
            highlight_job_neg = contains_words(title, neg_search_terms)

            font_style = ''
            if highlight_job_pos:
                font_style = 'style="color:green;"'
            if highlight_job_neg:
                font_style = 'style="color:purple;"'

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
        
    # create final body messages by joining individual body texts
    text_body = '<br><hr><br>'.join(ls_text_body)
    html_body = '<br><hr><br>'.join(ls_html_body)

    print(n_new_jobs_total)
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