import logging

import bleach
import datetime
import tornado.web
import json
from settings import email

from aswwu.base_handlers import BaseHandler

logger = logging.getLogger("aswwu")


class OpenForumHandler(BaseHandler):
    def post(self):
        try:
            json_data = json.loads(self.request.body.decode('utf-8'))
            for key in json_data:
                if key == "to":
                    TO = json_data[key]
                elif key == "subject":
                    SUBJECT = json_data[key]
                elif key == "body":
                    BODY = json_data[key]
                elif key == "reply-to":
                    REPLY_TO = json_data[key]
                else:
                    self.set_status(500)
                    self.write({'status': 'invalid json parameters'})
                
                emailAdministration(TO, SUBJECT, BODY, REPLY_TO)

                self.write({"status": "success"})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "Error"})
        



def emailAdministration(TO, SUBJECT, BODY, REPLY_TO):
    import smtplib

    FROM = email['username']
    TO = TO + "@wallawalla.edu"
    SUBJECT = "Open Forum Submission " + SUBJECT
    TEXT = BODY

    smtpsrv = "smtp.office365.com"
    smtpserver = smtplib.SMTP(smtpsrv, 587)

    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(FROM, email['password'])
    header = 'To:' + TO + '\n' + 'From: ' + FROM + '\n' + 'Subject:%s \n' % SUBJECT
    msgbody = header + '\n %s \n\n' % TEXT
    smtpserver.sendmail(FROM, TO, msgbody)
    smtpserver.close()