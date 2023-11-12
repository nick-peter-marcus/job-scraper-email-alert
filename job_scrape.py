def main():
    # import libraries
    import os
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from websites.gfk.gfk_scrape import gfk
    from websites.toast.toast_scrape import toast
    from websites.chewy.chewy_scrape_selenium import chewy

    # initialize empty lists to story body texts for job alert message
    ls_text_body = []
    ls_html_body = []

    # call scraping function of each company and store listings as list (if not empty)
    company_funcs = [gfk, toast, chewy]
    for func in company_funcs:
        company_jobs = func()
        if company_jobs:
            ls_text_body.append(company_jobs["text"])
            ls_html_body.append(company_jobs["html"])

    # create final body messages by joining individual body texts
    text_body = '<br><hr><br>'.join(ls_text_body)
    html_body = '<br><hr><br>'.join(ls_html_body)

    # send job alert per mail if new jobs were found (i.e. bodies not empty)
    if text_body and html_body:
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

        print("New jobs, mail sent.")
    else:
        print("No new jobs.")


if __name__ == '__main__':
    main()
    
