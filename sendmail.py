#!sendmail.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Application-specific modules
import config
import log

def email(subject, text, html):
    smtpServer = config.Get("smtpServer")
    smtpPort = int(config.Get("smtpPort"))
    smtpUser = config.Get("smtpUser")
    smtpPass = config.Get("smtpPass")
    addrTo = config.Get("emailAddress")
    if smtpServer != None and smtpUser != None and smtpPass != None and addrTo != None:
        #addrFrom = smtpUser
        addrFrom = "Vesta<" + smtpUser + ">"
        if html != None:
            msg = MIMEMultipart('alternative')
            # Record the MIME types of both parts - text/plain and text/html
            part1 = MIMEText(text, 'plain')
            msg.attach(part1)
            part2 = MIMEText(html, 'html')
            msg.attach(part2)
        else: # No HTML
            msg = MIMEText(text)
        msg['To'] = addrTo
        msg['From'] = addrFrom
        msg['Subject'] = subject
        # Send the message via an SMTP server
        try:
            s = smtplib.SMTP_SSL(smtpServer, smtpPort)
            s.ehlo()
            s.login(smtpUser, smtpPass)
            s.sendmail(addrFrom, addrTo, msg.as_string())
            s.close()
            #s.quit()
        except:
            log.fault("SMTP failed to send")
            log.debug("Sending to:" + addrTo + ", and from:" + addrFrom)
            log.debug("smtpServer:" + smtpServer + ", port:" + str(smtpPort))
            log.debug("smtpUser:" + smtpUser + ", smtpPass:" + smtpPass)
            if html != None:
                log.debug("HTML:" + html)
            log.debug("Text:" + text)
    else:
        log.fault("Need smtpUser, smtpPass, smtpServer and emailAddress in config.txt")