import os
import sys
import json
import tornado.web
import random
import string
import glob

from settings import testing

from aswwu.base_handlers import BaseHandler


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
            if not testing['dev']:
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
        if not testing['dev']:
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
        image = open(glob.glob("../media/cms/" + filename)[0], "r")
        self.set_header("Content-Type", "image/*")
        self.write(image.read())
