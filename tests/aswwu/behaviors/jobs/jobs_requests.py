from builtins import str
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
URLS = {key : BASE_URL + "/" + URLS[key] for key in list(URLS.keys())}


# "new": "job/new",
def post_job_new(data, session=None):
    session = requests.Session() if session is None else session

    request_url = URLS["new"]
    resp = session.post(request_url, json=data)
    return resp


# "job_view": "job/view",
def get_job_view(job_id=None, session=None):
    """
    :param job_id: an integer job id, or None for all jobs
    :param session:
    :return:
    """
    job_id = "all" if job_id is None else str(job_id)
    session = requests.Session() if session is None else session

    request_url = URLS["job_view"] + "/" + job_id
    resp = session.get(request_url)
    return resp


# "job_delete": "job/delete",
def post_job_delete():
    pass


# "job_edit": "job/edit",
def post_job_edit(job_id, data, session=None):
    """
    :param job_id: an integer job id
    :param session:
    :return:
    """
    session = requests.Session() if session is None else session

    request_url = URLS["job_edit"] + "/" + str(job_id)
    resp = session.post(request_url, json=data)
    return resp


# "app_submit": "application/submit",
def post_app_submit(data, session=None):
    session = requests.Session() if session is None else session

    request_url = URLS["app_submit"]
    resp = session.post(request_url, json=data)
    return resp


# "app_view": "application/view",
def get_app_view(job_id=None, username=None, session=None):
    job_id = "all" if job_id is None else job_id
    username = "all" if username is None else username
    session = requests.Session() if session is None else session

    request_url = URLS["app_view"] + "/" + str(job_id) + "/" + username
    resp = session.get(request_url)
    return resp


# "app_status": "application/status",
def post_app_status():
    pass


# "app_export": "application/export",
def get_app_export():
    pass


# "resume_upload": "resume/upload",
def post_resume_upload(files, job_id, session=None):
    session = requests.Session() if session is None else session

    request_url = URLS["resume_upload"]
    response = session.post(request_url, files=files, data={"jobID": job_id})
    return response


# "resume_download": "resume/download",
def get_resume_download(job_id, username, session=None):
    session = requests.Session() if session is None else session

    request_url = URLS["resume_download"] + "/" + str(job_id) + "/" + username
    response = session.get(request_url, allow_redirects=True)
    return response