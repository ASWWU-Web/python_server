import requests
import settings

BASE_URL = settings.environment['base_url'] + ':' + str(settings.environment['port']) + 'forms'
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
