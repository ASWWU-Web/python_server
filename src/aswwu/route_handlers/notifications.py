



# TODO change all this to work for a notification (this is just a template of copied from forms for reference)

class NewNotification(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            if 'notifications-admin' in user.roles:
                notification = 0 # Method for getting the notification
                notification.notification_name = bleach.clean(self.get_argument('notification_name'))
                notification.notification_link = bleach.clean(self.get_argument('notification_link'))
                if self.get_argument('visibility') == '1' or self.get_argument('visibility').lower() == 'true':
                    notification.visibility = 1
                else:
                    notification.visibility = 0
                notification.start_time = bleach.clean(self.get_argument('start_time'))
                notification.end_time = bleach.clean(self.get_argument('end_time'))
                notification.severity = bleach.clean(self.get_argument('severity'))
                notification.owners = bleach.clean(self.get_argument('owners'))



                # TODO complete validation that this is a new notification below here



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
