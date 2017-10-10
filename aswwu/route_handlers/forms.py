import glob
import json
import logging
import os

import bleach
import tornado.web

from aswwu.base_handlers import BaseHandler
import aswwu.models.forms as forms_model
import aswwu.alchemy as alchemy

logger = logging.getLogger("aswwu")

class NewFormHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            if 'forms' in user.roles:
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
                alchemy.addOrUpdateForm(form)
                form = alchemy.jobs_db.query(forms_model.JobForm).filter_by(job_name=str(form.job_name)).one()
                questions = json.loads(self.get_argument('questions'))
                for q in questions:
                    if 'question' in q:
                        question = forms_model.JobQuestion()
                        question.question = q['question']
                        question.jobID = form.id
                        alchemy.addOrUpdateForm(question)
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
                forms = alchemy.query_all_Forms(forms_model.JobForm)
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
                    alchemy.delete_thing_Forms(alchemy.jobs_db.query(forms_model.JobQuestion)
                                               .filter_by(id=int(q.id)).one())
                alchemy.delete_thing_Forms(form)
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


class SubmitApplicationHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            temp_var = False
            user = self.current_user
            if user.username == self.get_argument("username"):
                answers = json.loads(self.get_argument('answers'))
                if len(answers) > 50:
                    raise ValueError("Too many answers submitted")
                try:
                    app = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(jobID=self.get_argument("jobID"),
                                                                                      username=user.username).one()
                except Exception as e:
                    temp_var = True
                    app = forms_model.JobApplication()
                    app.status = "new"
                app.jobID = bleach.clean(self.get_argument('jobID'))
                app.username = user.username
                alchemy.addOrUpdateForm(app)
                if temp_var:
                    app = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(jobID=self.get_argument("jobID"),
                                                                                      username=user.username).one()
                for a in answers:
                    try:
                        answer = alchemy.jobs_db.query(forms_model.JobAnswer)\
                            .filter_by(applicationID=app.id, questionID=a['questionID']).one()
                    except Exception as e:
                        answer = forms_model.JobAnswer()
                    if 'questionID' in a:
                        answer.questionID = bleach.clean(a['questionID'])
                        answer.answer = bleach.clean(a['answer'])
                        answer.applicationID = app.id
                        alchemy.addOrUpdateForm(answer)
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
                    apps = alchemy.query_all_Forms(forms_model.JobApplication)
                    self.write({'applications': [a.min() for a in apps]})
            elif job_id == "all" and username != "all":
                if 'forms-admin' in user.roles or username == user.username:
                    apps = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(username=username)
                    self.write({'applications': [a.min() for a in apps]})
            elif username == "all" and job_id != "all":
                if 'forms-admin' in user.roles:
                    apps = alchemy.jobs_db.query(forms_model.JobApplication).filter_by(jobID=job_id)
                    self.write({'applications': [a.min() for a in apps]})
            else:
                if 'forms-admin' in user.roles or username == user.username:
                    app = alchemy.jobs_db.query(forms_model.JobApplication)\
                        .filter_by(jobID=str(job_id), username=username).one()
                    self.write({'application': app.serialize()})
        #             TODO: Exception Handle
        except Exception as e:
            logger.error("ViewApplicationHandler: error.\n" + str(e.message))
            self.set_status(404)
            self.write({"status": "Application not found"})


class ApplicationStatusHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            if 'forms' in user.roles:
                app = alchemy.jobs_db.query(forms_model.JobApplication)\
                    .filter_by(jobID=str(self.get_argument("jobID")), username=self.get_argument("username")).one()
                app.status = bleach.clean(self.get_argument("status"))
                alchemy.addOrUpdateForm(app)
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
            except Exception:
                self.set_status(404)
                self.write({"status": "Error", "message": "Job doesn't exist"})
            fileinfo = self.request.files['file'][0]
            if os.path.splitext(fileinfo['filename'])[1] in ['.pdf', '.docx', '.doc', '.zip', '.odt']:
                for f in glob.glob("../databases/resume/" + user.username + "_"
                                   + job_id.replace("/", "").replace("..",  "") + "*"):
                    os.remove(f)
                fh = open(
                    "../databases/resume/" + user.username + "_" + job_id + os.path.splitext(fileinfo['filename'])[1],
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
            if 'forms' in user.roles:
                uname = username.replace("/", "")
            else:
                uname = user.username
            try:
                resume = open(glob.glob("../databases/resume/" + uname + "_" + job_id + "*")[0], "r")
                self.set_status(200)
                self.set_header("Content-type", "application/" + os.path.splitext(resume.name)[1].replace(".", ""))
                self.set_header('Content-Disposition', 'inline; filename=' + os.path.basename(resume.name) + '')
                self.write(resume.read())
                resume.close()
            except Exception as e:
                self.set_status(404)
                self.write({"status": "Error", "message": "File not found"})
        except Exception as e:
            logger.error("ViewResumeHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "Error"})
