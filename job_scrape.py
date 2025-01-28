def main():
    # import libraries
    import os
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    # import scraping modules
    from websites.gfk.gfk_scrape import gfk
    from websites.toast.toast_scrape import toast
    from websites.chewy.chewy_scrape_selenium import chewy
    from websites.wtw.wtw_scrape import wtw


    """
    POPULATE EMAIL BODY TEXTS WITH RESULTS OF SCRAPER MODULES
    """
    # initialize empty lists to store body texts for job alert message
    ls_text_body = []
    ls_html_body = []

    # call scraping function of each company (return dictionary)
    company_funcs = {'GfK': gfk, 
                     'Toast': toast, 
                     'Chewy': chewy, 
                     'WTW': wtw}

    for name, func in company_funcs.items():
        new_company_jobs = func()
        if new_company_jobs:
            text_body = f'New Jobs at {name}:\n'
            html_body = f'<h1>New Jobs at {name}:</h1>\n'
            for job_details in new_company_jobs.values():
                title = job_details['title']
                link = job_details['link']
                location = job_details['location']
                date = job_details['date_posted']

                text_body += (f'Title: {title}:\nLink: {link}\nLocation: {location}\n\n')
                html_body += (f'<a href = "{link}"><b>{title}</b></a><br>Location: {location}<br><br>')
        
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
        EMAIL_ADDRESS = os.environ.get('USER_EMAIL')
        EMAIL_PASSWORD = os.environ.get('USER_PW')
        EMAIL_TO = os.environ.get('RECEIVER_EMAIL')
        
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