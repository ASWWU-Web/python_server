import glob
import json
import logging
import os

import bleach
import tornado.web

from aswwu import BaseHandler

logger = logging.getLogger("aswwu")


class NewFormHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            if('forms' in user.roles):
                form = JobForm()
                form.job_name = bleach.clean(self.get_argument('job_name'))
                form.job_description = bleach.clean(self.get_argument('job_description'))
                if self.get_argument('visibility') == '1' or self.get_argument('visibility').lower() == 'true':
                    form.visibility = 1
                else:
                    form.visibility = 0
                form.department = bleach.clean(self.get_argument('department'))
                form.owner = bleach.clean(self.get_argument('owner'))
                form.image = bleach.clean(self.get_argument('image'))
                addOrUpdateForm(form)
                form = jobs_s.query(JobForm).filter_by(job_name=str(form.job_name)).one()
                questions = json.loads(self.get_argument('questions'))
                for q in questions:
                    if 'question' in q:
                        question = JobQuestion()
                        question.question = q['question']
                        question.jobID = form.id
                        addOrUpdateForm(question)
                self.set_status(201)
                self.write({"status": "submitted"})
            else:
                self.set_status(401)
                self.write({"status": "Unauthorized"})
        except Exception as e:
            logger.error("NewFormHandler: error.\n" + str(e.message))
            jobs_s.rollback()
            self.set_status(500)
            self.write({"status": "Error"})

class ViewFormHandler(BaseHandler):
    def get(self, jobID):
        try:
            if(jobID == "all"):
                forms = query_all_Forms(JobForm)
                self.write({'forms': [f.min() for f in forms]})
            else:
                form = jobs_s.query(JobForm).filter_by(id=str(jobID)).one()
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
                form = jobs_s.query(JobForm).filter_by(id=self.get_argument("jobID")).one()
                for q in form.questions:
                    delete_thing_Forms(jobs_s.query(JobQuestion).filter_by(id=int(q.id)).one())
                delete_thing_Forms(form)
                self.set_status(200)
                self.write({"status": "Form Deleted"})
            else:
                self.set_status(401)
                self.write({"status": "Unauthorized"})
        except Exception as e:
            logger.error("DeleteFormHandler: error.\n" + str(e.message))
            self.set_status(500)
            jobs_s.rollback()
            self.write({"status": "Error"})


class SubmitApplicationHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            tempVar = False
            user = self.current_user
            if user.username == self.get_argument("username"):
                answers = json.loads(self.get_argument('answers'))
                if len(answers) > 50:
                    raise ValueError("Too many answers submitted")
                try:
                    app = jobs_s.query(JobApplication).filter_by(jobID=self.get_argument("jobID"), username=user.username).one()
                except Exception as e:
                    tempVar = True
                    app = JobApplication()
                    app.status = "new"
                app.jobID = bleach.clean(self.get_argument('jobID'))
                app.username = user.username
                addOrUpdateForm(app)
                if tempVar:
                    app = jobs_s.query(JobApplication).filter_by(jobID=self.get_argument("jobID"),
                                                             username=user.username).one()
                for a in answers:
                    try:
                        answer = jobs_s.query(JobAnswer).filter_by(applicationID=app.id, questionID=a['questionID']).one()
                    except Exception as e:
                        answer = JobAnswer()
                    if 'questionID' in a:
                        answer.questionID = bleach.clean(a['questionID'])
                        answer.answer = bleach.clean(a['answer'])
                        answer.applicationID = app.id
                        addOrUpdateForm(answer)
                self.set_status(201)
                self.write({"status": "submitted"})
            else:
                self.set_status(401)
                self.write({"status": "Unauthorized"})
        except Exception as e:
            logger.error("SubmitApplicationHandler: error.\n" + str(e.message))
            jobs_s.rollback()
            self.set_status(500)
            self.write({"status": "Error"})


class ViewApplicationHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, jobID, username):
        try:
            user = self.current_user
            if jobID == "all" and username == "all":
                if 'forms-admin' in user.roles:
                    apps = query_all_Forms(JobApplication)
                    self.write({'applications': [a.min() for a in apps]})
            elif jobID=="all" and username != "all":
                if 'forms-admin' in user.roles or username == user.username:
                    apps = jobs_s.query(JobApplication).filter_by(username=username)
                    self.write({'applications': [a.min() for a in apps]})
            elif username=="all" and jobID != "all":
                if('forms-admin' in user.roles):
                    apps = jobs_s.query(JobApplication).filter_by(jobID=jobID)
                    self.write({'applications': [a.min() for a in apps]})
            else:
                if 'forms-admin' in user.roles or username == user.username:
                    app = jobs_s.query(JobApplication).filter_by(jobID=str(jobID), username=username).one()
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
                app = jobs_s.query(JobApplication).filter_by(jobID=str(self.get_argument("jobID")), username=self.get_argument("username")).one()
                app.status = bleach.clean(self.get_argument("status"))
                addOrUpdateForm(app)
                self.set_status(200)
                self.write({"status": "success"})
            else:
                self.set_status(401)
                self.write({"status": "Unauthorized"})
        except Exception as e:
            logger.error("ApplicationStatusHandler: error.\n" + str(e.message))
            jobs_s.rollback()
            self.set_status(500)
            self.write({"status": "Error"})


class ResumeUploadHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        try:
            jobID = self.get_argument("jobID")
            try:
                jobs_s.query(JobForm).filter_by(id=jobID).one()
            except Exception:
                self.set_status(404)
                self.write({"status": "Error", "message": "Job doesn't exist"})
            fileinfo = self.request.files['file'][0]
            if os.path.splitext(fileinfo['filename'])[1] in ['.pdf', '.docx', '.doc', '.zip', '.odt']:
                for f in glob.glob("../databases/resume/" + user.username + "_" + jobID.replace("/", "").replace("..",
                                                                                                                 "") + "*"):
                    os.remove(f)
                fh = open(
                    "../databases/resume/" + user.username + "_" + jobID + os.path.splitext(fileinfo['filename'])[1],
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
    def get(self, jobID, username):
        user = self.current_user
        try:
            if 'forms' in user.roles:
                uname = username.replace("/","")
            else:
                uname = user.username
            try:
                File = open(glob.glob("../databases/resume/" + uname + "_" + jobID + "*")[0], "r")
                self.set_status(200)
                self.set_header("Content-type", "application/" + os.path.splitext(File.name)[1].replace(".",""))
                self.set_header('Content-Disposition', 'inline; filename=' + os.path.basename(File.name) + '')
                self.write(File.read())
                File.close()
            except:
                self.set_status(404)
                self.write({"status": "Error", "message": "File not found"})
        except Exception as e:
            logger.error("ViewResumeHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "Error"})
