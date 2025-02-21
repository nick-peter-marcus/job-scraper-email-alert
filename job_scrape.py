def main():
    # import libraries
    import os
    import re
    import smtplib
    from dotenv import load_dotenv
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    # import scraping modules
    # from websites.gfk.gfk_scrape import gfk
    # from websites.wtw.wtw_scrape import wtw
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

    # call scraping function of each website (return dictionary)
    # company_funcs = {'GfK': gfk, 
    #                  'WTW': wtw,
    #                  'Goodjobs EU': goodjobs_eu}
    company_funcs = {'Goodjobs EU': goodjobs_eu,
                     'Greenjobs DE': greenjobs_de}

    for website_name, website_func in company_funcs.items():
        # make scraping function call.
        summary, new_company_jobs = website_func()
        
        # skip if there are no new jobs
        if not new_company_jobs:
            continue

        # initialize email bodies
        html_body = f'<big><b>New Jobs at {website_name}:</b></big> <br> <small><i>{summary}</i></small> <br><br>'
        text_body = f'New Jobs at {website_name}:\n{summary}\n\n'

        # gather information for each job
        for job_details in new_company_jobs.values():
            link = job_details['link']
            title = job_details['title']
            company = job_details['company']
            location = job_details['location']
            date = job_details['date_posted']
            details = job_details['details'] if 'details' in job_details else None

            # Highlight titles if search words appear
            search_terms = ["data", "analyst", "analysis", "analytics", "machine learning"]
            search_terms.extend(["daten", "analyse", "auswertung", "analytiker", "statistik"])
            search_terms.extend(["marktforschung", "markt", "forschung", "market", "research"])
            search_terms.extend([" ki ", " ai ", " ml "])
            highlight_job = contains_words(title, search_terms)
            font_style = ''
            if highlight_job:
                font_style += 'style="color:green;"'

            # Add job info to mail bodies
            html_body += (f'<a href="{link}" {font_style}><b>{title}</b></a>'
                          f'<br>Company: {company}'
                          f'<br>Location(s): {location}'
                          f'<br>Posted/Deadline: {date}')
            text_body += (f'Title: {title}:\nLink: {link}\nLocation: {location}')
            
            # Add element "details" to bodies if existent
            html_body += f'<br>Details: {details}<br><br>' if details else '<br><br>'
            text_body += f'\nDetails: {details}\n\n' if details else '\n\n'
    
        ls_text_body.append(text_body)
        ls_html_body.append(html_body)
        
    # create final body messages by joining individual body texts
    text_body = '<br><hr><br>'.join(ls_text_body)
    html_body = '<br><hr><br>'.join(ls_html_body)


    """
    SET UP CONNECTION AND SEND EMAIL
    """
    # send job alert per mail if new jobs were found (i.e. if bodies are not empty)
    if text_body or html_body:
        # include mail account credentials from environment variables
        load_dotenv()
        EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
        EMAIL_TO = os.getenv('EMAIL_TO')
        
        # set up email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'JOB ALERT'
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
    else:
        print("No new jobs.")


if __name__ == '__main__':
    main()