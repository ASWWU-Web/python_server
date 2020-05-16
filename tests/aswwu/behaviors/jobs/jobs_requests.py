import requests
import settings

BASE_URL = settings.environment['base_url'] + ':' + str(settings.environment['port']) + '/forms'
URLS = {
    "new": "job/new",
    "job_view": "job/view",
    "job_delete": "job/delete",
    "job_edit": "job/edit",
    "app_submit": "application/submit",
    "app_view": "application/view",
    "app_status": "application/status",
    "app_export": "application/export",
    "resume_upload": "resume/upload",
    "resume_download": "resume/download",
}
URLS = {key : BASE_URL + "/" + URLS[key] for key in URLS.keys()}


# "new": "job/new",
def post_job_new(data, session=None):
    session = requests.Session() if session is None else session

    request_url = URLS["new"]
    resp = session.post(request_url, json=data)
    return resp


# "job_view": "job/view",
def get_job_view():
    pass


# "job_delete": "job/delete",
def post_job_delete():
    pass


# "job_edit": "job/edit",
def post_job_edit():
    pass


# "app_submit": "application/submit",
def post_app_submit():
    pass


# "app_view": "application/view",
def get_app_view():
    pass


# "app_status": "application/status",
def post_app_status():
    pass


# "app_export": "application/export",
def get_app_export():
    pass


# "resume_upload": "resume/upload",
def post_resume_upload():
    pass


# "resume_download": "resume/download",
def get_resume_download():
    pass
