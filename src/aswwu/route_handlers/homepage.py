import logging

import bleach
import datetime
import tornado.web
import json
from settings import email

from src.aswwu.base_handlers import BaseHandler

logger = logging.getLogger("aswwu")


def


class NotificationHandler(BaseHandler):
    """
    List and create endpoints for elections.
    """

    def get(self):
        # build query parameter dict
        search_criteria = build_query_params(self.request.arguments)

        # get the notification
        notification = _alchemy.query_notification(notification_text=search_criteria.get('notification_text', None),
                                                     notification_links=search_criteria.get('links', None),
                                                     start_time=search_criteria.get('start_time', None),
                                                     end_time=search_criteria.get('end_time', None),
                                                     severity=search_criteria.get('severity', None),
                                                     visible=search_criteria.get('visible', None),
                                                     notification_owners=search_criteria.get('notification_owners', None))
        # response
        self.set_status(200)
        self.write('Hello World')



class OpenForumHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        maxChars = 1000
        reply_to = self.current_user.username
        try:
            json_data = json.loads(self.request.body.decode('utf-8'))
            for key in json_data:
                if key == "recipient":
                    to = adminUsernameExpander(bleach.clean(json_data[key]))
                elif key == "message_body":
                    body = json_data[key]
                    if len(body) > maxChars:
                        body = body[0:maxChars]
                    body = bleach.clean(body)
                elif key == "reply-to":
                    reply_to = bleach.clean(json_data[key])
                else:
                    self.set_status(500)
                    self.write({'status': 'invalid parameters'})
                    return
            subject = "Message from " + reply_to

            emailAdministration(to, subject, body, reply_to)
            self.set_status(200)
            self.write({"status": "success"})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "Error"})
            print(e.message)
        

def adminUsernameExpander(recipient):
    """Convert an admin position title into the corresponding email address username
    
    TODO: uncomment real addresses

    Arguments:
        recipient {string} -- the title of an admin position
    Raises:
        ValueError -- When the recipient field doesn't match an ASWWU position
    Returns:
        string -- the username of the aswwu position
    """

    adminEmails =	{
        "President": "aswwu.pres",
        "Vice President": "aswwu.evp",
        "Financial VP": "aswwu.fvp",
        "Social VP": "aswwu.spiritual",
        "Spiritual VP": "aswwu.social",
        "Marketing VP": "aswwu.marketing"
    }
    if recipient in adminEmails:
        return adminEmails[recipient]
    else:
        raise ValueError('The selected recipient is not a valid ASWWU Open Forum Recipient.')


def emailAdministration(TO, SUBJECT, BODY, REPLY_TO):
    """Send an email using the webmaster account and a custom Reply-To address.
    Arguments:
        TO {string} -- username of email recipient
        SUBJECT {string} -- subject line of the email
        BODY {string} -- body text of the email
        REPLY_TO {string} -- username of message author
    """
    import smtplib
    
    domain = "wallawalla.edu"
    SEND_USING = email['username']  # Webmaster account, contains @wallawalla.edu
    SEND_TO = TO + "@" + domain # admin recipient 
    REPLY_TO = REPLY_TO + "@" + domain # user who sent the message
    SUBJECT = "Open Forum Submission: " + SUBJECT
    TEXT = ("---- Message from " + REPLY_TO + ", Sent at " + str(datetime.datetime.now()) + " ----\n\n" + BODY + "\n\n---- End Message ----")

    smtpsrv = "smtp.office365.com"
    smtpserver = smtplib.SMTP(smtpsrv)
    # smtpserver.set_debuglevel(1)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(SEND_USING, email['password'])

    header = (
        'To:' + SEND_TO + '\n' 
        + 'From:' + SEND_USING + '\n' 
        + 'Reply-To:' + REPLY_TO + '\n'
        + 'Subject:%s \n' % SUBJECT
    )
    msgbody = header + '\n %s \n\n' % TEXT

    smtpserver.sendmail(SEND_USING, SEND_TO, msgbody)
    smtpserver.close()
        

