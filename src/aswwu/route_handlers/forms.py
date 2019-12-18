import glob
import json
import logging
import os

import bleach
import tornado.web

from src.aswwu.base_handlers import BaseHandler
from settings import email, database
import src.aswwu.models.forms as forms_model
import src.aswwu.alchemy_new.jobs as alchemy

logger = logging.getLogger("aswwu")

class NewFormHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            if 'forms-admin' in user.roles:
                form = forms_model.JobForm()
                form.job_name = bleach.clean(self.get_argument('job_name'))
                form.job_description = bleach.clean(self.get_argument('job_description'))
                if self.get_argument('visibility') == '1' or self.get_argument('visibility').lower() == 'true':
                    form.visibility = 1
                else:
                    form.visibility = 0
                form.department = bleach.clean(self.get_argument('department'))
                form.owner = bleach.clean(self.get_argument('owner'))
                form.image = bleach.clean(self.get_argument('image'))
                form.featured = True if self.get_argument('featured') == 'true' else False
                job_list = (alchemy.jobs_db.query(forms_model.JobForm).filter_by(job_name=str(form.job_name)).all())
                if len(job_list) == 0:
                    alchemy.add_or_update_form(form)
                else:
                    self.set_status(400)
                    self.write({"status": "Error: A job named " + form.job_name + " already exists."})
                    return
                form = alchemy.jobs_db.query(forms_model.JobForm).filter_by(job_name=str(form.job_name)).one()
                questions = json.loads(self.get_argument('questions'))
                for q in questions:
                    if 'question' in q:
                        question = forms_model.JobQuestion()
                        question.question = q['question']
                        question.jobID = form.id
                        alchemy.add_or_update_form(question)
                self.set_status(201)
                self.write({"status": "submitted"})
            else:
                self.set_status(401)
                self.write({"status": "Unauthorized"})
        except Exception as e:
            logger.error("NewFormHandler: error.\n" + str(e.message))
            alchemy.jobs_db.rollback()
            self.set_status(500)
            self.write({"status": "Error"})


class ViewFormHandler(BaseHandler):
    def get(self, job_id):
        try:
            if job_id == "all":
                forms = alchemy.query_all_forms(forms_model.JobForm)
                self.write({'forms': [f.min() for f in forms]})
            else:
                form = alchemy.jobs_db.query(forms_model.JobForm).filter_by(id=str(job_id)).one()
                self.write({'form': form.serialize()})
        #         TODO: exception handle
        except Exception as e:
            logger.error("ViewFormHandler: error.\n" + str(e.message))
            self.set_status(404)
            self.write({"status": "Form not found"})


class DeleteFormHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            if 'forms-admin' in user.roles:
                form = alchemy.jobs_db.query(forms_model.JobForm).filter_by(id=self.get_argument("jobID")).one()
                for q in form.questions:
                    alchemy.delete_thing_forms(alchemy.jobs_db.query(forms_model.JobQuestion)
                                               .filter_by(id=int(q.id)).one())
                alchemy.delete_thing_forms(form)
                self.set_status(200)
                self.write({"status": "Form Deleted"})
            else:
                self.set_status(401)
                self.write({"status": "Unauthorized"})
        except Exception as e:
            logger.error("DeleteFormHandler: error.\n" + str(e.message))
            self.set_status(500)
            alchemy.jobs_db.rollback()
            self.write({"status": "Error"})


class EditFormHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, jobID):
        try:
            user = self.current_user
            form = alchemy.jobs_db.query(forms_model.JobForm).filter_by(id=jobID).one()
            if 'forms-admin' in user.roles or user.username == form.owner:
                form.job_name = bleach.clean(self.get_argument('job_name'))
                form.job_description = bleach.clean(self.get_argument('job_description'))
                if self.get_argument('visibility') == '1' or self.get_argument('visibility').lower() == 'true':
                    form.visibility = 1
                else:
                    form.visibility = 0
                form.department = bleach.clean(self.get_argument('department'))
                form.owner = bleach.clean(self.get_argument('owner'))
                form.image = bleach.clean(self.get_argument('image'))
                form.featured = True if self.get_argument('featured') == 'true' else False
                alchemy.add_or_update_form(form)
                new_questions = json.loads(self.get_argument('questions'))
                for question in form.questions:
                    for q in new_questions:
                        if question.id == q['id']:
                            question.question = q['question']
                            alchemy.add_or_update_form(question)
                self.set_status(200)
                self.write({"status": "Form Updated"})
            else:
                self.set_status(401)
                self.write({"status": "Unauthorized"})
        except Exception as e:
            logger.error("DeleteFormHandler: error.\n" + str(e.message))
            self.set_status(500)
            alchemy.jobs_db.rollback()
            self.write({"status": "Error"})


class SubmitApplicationHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            job_id = self.get_argument("jobID")
            form = alchemy.jobs_db.query(forms_model.JobForm).filter_by(id=str(job_id)).one()
            temp_var = False
            user = self.current_user
            if user.username == self.get_argument("username"):
                answers = json.loads(self.get_argument('answers'))
                if len(answers) > 50:
                    raise ValueError("Too many answers submitted")
                try:
                    app = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(jobID=job_id,
                                                                                      username=user.username).one()
                except:
                    temp_var = True
                    app = forms_model.JobApplication()
                    app.status = "new"
                    email_notify(user.username, form.owner, job_id)
                    email_confirm(user.username, job_id)
                app.jobID = bleach.clean(job_id)
                app.username = user.username
                alchemy.add_or_update_form(app)
                if temp_var:
                    app = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(jobID=job_id,
                                                                                      username=user.username).one()
                for a in answers:
                    try:
                        answer = alchemy.jobs_db.query(forms_model.JobAnswer)\
                            .filter_by(applicationID=app.id, questionID=a['questionID']).one()
                    except:
                        answer = forms_model.JobAnswer()
                    if 'questionID' in a:
                        answer.questionID = bleach.clean(str(a['questionID']))
                        answer.answer = bleach.clean(a['answer'])
                        answer.applicationID = app.id
                        alchemy.add_or_update_form(answer)
                self.set_status(201)
                self.write({"status": "submitted"})
            else:
                self.set_status(401)
                self.write({"status": "Unauthorized"})
        except Exception as e:
            logger.error("SubmitApplicationHandler: error.\n" + str(e.message))
            alchemy.jobs_db.rollback()
            self.set_status(500)
            self.write({"status": "Error"})


class ViewApplicationHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, job_id, username):
        try:
            user = self.current_user
            if job_id == "all" and username == "all":
                if 'forms-admin' in user.roles:
                    apps = alchemy.query_all_forms(forms_model.JobApplication)
                    self.write({'applications': [a.min() for a in apps]})
                    return
            elif job_id == "all" and username != "all":
                if 'forms-admin' in user.roles or username == user.username:
                    apps = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(username=username)
                    self.write({'applications': [a.min() for a in apps]})
                    return
            elif username == "all" and job_id != "all":
                form = alchemy.jobs_db.query(forms_model.JobForm).filter_by(id=str(job_id)).one()
                if 'forms-admin' in user.roles or ('forms' in user.roles and form.owner == user.username):
                    apps = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(jobID=job_id)
                    self.write({'applications': [a.min() for a in apps]})
                    return
            else:
                form = alchemy.jobs_db.query(forms_model.JobForm).filter_by(id=str(job_id)).one()
                if 'forms-admin' in user.roles or username == user.username or 'forms' in user.roles and (form.owner == user.username or form.id == 1):
                    app = alchemy.jobs_db.query(forms_model.JobApplication)\
                        .filter_by(jobID=str(job_id), username=username).one()
                    response = {'application': app.serialize()}
                    # check if resume exists
                    try:
                        resume = open(glob.glob(database['location'] + "/resume/" + app.username + "_" + app.jobID + "*")[0], "r")
                        resume.close()
                    except:
                        response['application']['resume'] = None
                    # response
                    self.write(response)
                    return
            self.set_status(404)
            self.write({"status": "Insufficient Permissions"})
        except Exception as e:
            logger.error("ViewApplicationHandler: error.\n" + str(e.message))
            self.set_status(404)
            self.write({"status": "Application not found"})


class ApplicationStatusHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            job_id = str(self.get_argument("jobID"))
            uname = self.get_argument("username")
            user = self.current_user
            form = alchemy.jobs_db.query(forms_model.JobForm).filter_by(id=job_id).one()
            if 'forms' in user.roles or ('forms' in user.roles and form.owner == user.username):
                app = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(jobID=job_id, username=uname).one()
                app.status = bleach.clean(self.get_argument("status"))
                alchemy.add_or_update_form(app)
                self.set_status(200)
                self.write({"status": "success"})
            else:
                self.set_status(401)
                self.write({"status": "Unauthorized"})
        except Exception as e:
            logger.error("ApplicationStatusHandler: error.\n" + str(e.message))
            alchemy.jobs_db.rollback()
            self.set_status(500)
            self.write({"status": "Error"})


class ResumeUploadHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        try:
            job_id = self.get_argument("jobID")
            try:
                alchemy.jobs_db.query(forms_model.JobForm).filter_by(id=job_id).one()
            except:
                self.set_status(404)
                self.write({"status": "Error", "message": "Job doesn't exist"})
            fileinfo = self.request.files['file'][0]
            if os.path.splitext(fileinfo['filename'])[1] in ['.pdf', '.docx', '.doc', '.zip', '.odt']:
                for f in glob.glob(database['location'] + "/resume/" + user.username + "_"
                                   + job_id.replace("/", "").replace("..",  "") + "*"):
                    os.remove(f)
                fh = open(
                    database['location'] + "/resume/" + user.username + "_" + job_id + os.path.splitext(fileinfo['filename'])[1],
                    'w+')
                fh.write(fileinfo['body'])
                self.set_status(201)
                self.write({"status": "Submitted"})
            else:
                self.set_status(415)
                self.write({"status": "Error", "message": "Bad file type"})
        except Exception as e:
            logger.error("ResumeUploadHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "Error"})


class ViewResumeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, job_id, username):
        user = self.current_user
        try:
            form = alchemy.jobs_db.query(forms_model.JobForm).filter_by(id=job_id).one()
            if 'forms-admin' in user.roles or ('forms' in user.roles and form.owner == user.username):
                uname = username.replace("/", "")
            else:
                self.set_status(401)
                self.write({"status": "Unauthorized"})
                return
            try:
                resume = open(glob.glob(database['location'] + "/resume/" + uname + "_" + job_id + "*")[0], "r")
                self.set_status(200)
                self.set_header("Content-type", "application/" + os.path.splitext(resume.name)[1].replace(".", ""))
                self.set_header('Content-Disposition', 'inline; filename=' + os.path.basename(resume.name) + '')
                self.write(resume.read())
                resume.close()
            except:
                self.set_status(404)
                self.write({"status": "Error", "message": "File not found"})
        except Exception as e:
            logger.error("ViewResumeHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "Error"})


class ExportApplicationsHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, job_id):
        try:
            user = self.current_user
            if 'forms' not in user.roles:
                self.set_status(401)
                self.write({"error": "Unauthorized"})
                return
            generic_questions = alchemy.jobs_db.query(forms_model.JobQuestion).filter_by(jobID=1)
            specific_questions = alchemy.jobs_db.query(forms_model.JobQuestion).filter_by(jobID=job_id)
            questions = []
            for question in generic_questions:
                questions.append('"' + question.question.replace('"', "'") + '"')
            for question in specific_questions:
                questions.append('"' + question.question.replace('"', "'") + '"')
            questions.append("Submitted Resume")
            questions.append("Resume Link")

            apps = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(jobID=job_id)
            applicants = []
            for app in apps:
                applicant_answers = []
                generic_app = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(jobID=1, username=app.username).one()
                for answer in generic_app.answers:
                    applicant_answers.append('"' + answer.answer.replace('"', "'") + '"')
                for answer in app.answers:
                    applicant_answers.append('"' + answer.answer.replace('"', "'") + '"')
                applicant_answers.append("Yes" if len(glob.glob(database['location'] + '/resume/' + app.username + "_" + job_id + "*")) > 0 else "No")
                applicant_answers.append("https://aswwu.com/server/forms/resume/download/" + job_id + "/" + app.username if len(glob.glob(database['location'] + '/resume/' + app.username + "_" + job_id + "*")) > 0 else "")
                applicants.append(applicant_answers)

            self.set_header('Content-Type', 'text/csv')
            self.set_header('content-Disposition', 'attachment; filename=dump.csv')
            self.write(','.join(questions)+'\r\n')  # File header
            for line in range(0, len(applicants)):
                self.write(','.join(applicants[line])+'\r\n')
                yield self.flush()
        except Exception as e:
            logger.error("ViewApplicationHandler: error.\n" + str(e.message))
            self.set_status(404)
            self.write({"status": "error"})

def email_notify(applicant, owner, job_id):
    # dont send email for generic job
    if job_id == '1':
        return
    # construct email
    from_address = email['username']
    to_address = owner + "@wallawalla.edu"
    subject = "New Job Application Submitted"
    text = applicant + " has submitted an application for job ID " + job_id +\
        ". To view this application click here: https://aswwu.com/jobs/admin/review/" + job_id + "/" + applicant
    # send email
    send_email(from_address, to_address, subject, text)

def email_confirm(applicant, job_id):
    # dont send email for generic job
    if job_id == '1':
        return
    # construct email
    from_address = email['username']
    to_address = applicant + "@wallawalla.edu"
    subject = "Job Application Submitted"
    text = "Thank you for submitting your job application."
    # send email
    send_email(from_address, to_address, subject, text)

def send_email(from_address, to_address, subject, text):
    # connect to SMTP server
    import smtplib
    smtpsrv = "smtp.office365.com"
    smtpserver = smtplib.SMTP(smtpsrv, 587)
    # send the email
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(from_address, email['password'])
    header = 'To:' + to_address + '\n' + 'From: ' + from_address + '\n' + 'Subject:%s \n' % subject
    msgbody = header + '\n %s \n\n' % text
    smtpserver.sendmail(from_address, to_address, msgbody)
    # close the SMTP server connection
    smtpserver.close()

