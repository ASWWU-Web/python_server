import os
import sys
import json
import tornado.web
import random
import string
import glob

from settings import config, buildMediaPath

from src.aswwu.base_handlers import BaseHandler

PROFILE_PHOTOS_LOCATION = buildMediaPath("profiles")
PENDING_PROFILE_PHOTOS_LOCATION = buildMediaPath("pending_profile_photos")
DISMAYED_PROFILE_PHOTOS_LOCATION = buildMediaPath("dismayed_profiles")
MEDIA_LOCATION = buildMediaPath("")
CURRENT_YEAR = config.mask.get('current_year')

class UploadHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            if not ('administrator' in user.roles or 'pages-admin' in user.roles):
                self.write({'error': 'insufficient permissions'})
                return
        except:
            self.write({'error': 'authentication error'})
            return
        try:
            fileinfo = self.request.files['file'][0]
            if not os.environ['ENVIRONMENT'] == 'development':
                server_url = 'https://aswwu.com/server/pages/media/static/'
            else:
                server_url = 'http://localhost:8888/pages/media/static/'
            new_filename = ''.\
                join(random.choice(string.ascii_lowercase + string.digits) for _ in range(50)) + os.path.splitext(fileinfo['filename'])[1]
            print("new filename: " + new_filename)
            extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
            if os.path.splitext(fileinfo['filename'])[1] in extensions:
                fh = open(
                    "../media/cms/" + new_filename,
                    'w+')
                fh.write(fileinfo['body'])
            response = {"link": server_url + new_filename, "media_URI": "cms/" + new_filename}
        except Exception:
            response = {'error': str(sys.exc_info()[1])}
            self.set_status(500)
        self.write(response)


class LoadAllHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not os.environ['ENVIRONMENT'] == 'development':
            server_url = 'https://aswwu.com/server/pages/media/static/'
        else:
            server_url = 'http://localhost:8888/pages/media/static/'
        thumbnail_url = 'https://aswwu.com/media/img-sm/cms/'
        image_list = []
        for f in glob.glob("../media/cms/*"):
            filename = os.path.basename(f)
            image_list.append({
                "url": server_url + filename,
                "thumb": thumbnail_url + filename,
                "name": filename})
        self.write(json.dumps(image_list))


class LoadImageHandler(BaseHandler):
    def get(self, filename):
        print(MEDIA_LOCATION + filename)
        image_name = MEDIA_LOCATION + "/" + filename
        glob_results = glob.glob(image_name)
        if not glob_results:
            self.write({'error': 'could not find: ' + filename})
            return
        image = open(glob.glob(image_name)[0], "r")
        self.set_header("Content-Type", "image/gif")
        self.write(image.read())
        # image = open(glob.glob("../media/cms/" + filename)[0], "r")
        # self.set_header("Content-Type", "image/*")
        # self.write(image.read())