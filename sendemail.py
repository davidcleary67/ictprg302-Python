#!/usr/bin/python3

import smtplib

def main():
    """
    This Python code demonstrates the following features:
    
    * send an email using the Google smtp server.
    
    """
    sendEmail("ERROR: The program has crashed!")

smtp = {"sender": "dcleary@sunitafe.edu.au",
        "recipient": "davidcgcleary@gmail.com",
        "server": "smtp.gmail.com",
        "port": 587,
        "user": "davidcgcleary@gmail.com", # need to specify a gmail email address with an app password setup
        "password": "buaytgfwfrxxudme"}    # need a gmail app password     

def sendEmail(message):
    """
    Send an email message to the specified recipient."
    """
    email = 'To: ' + smtp["recipient"] + '\n' + 'From: ' + smtp["sender"] + '\n' + 'Subject: Backup Error\n\n' + message + '\n'

    # connect to email server and send email
    try:
        smtp_server = smtplib.SMTP(smtp["server"], smtp["port"])
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.ehlo()
        smtp_server.login(smtp["user"], smtp["password"])
        smtp_server.sendmail(smtp["sender"], smtp["recipient"], email)
        smtp_server.close()
    except Exception as e:
        print("ERROR: An error occurred.")
        
if __name__ == "__main__":
    main()