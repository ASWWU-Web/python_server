import os
import sys
import json
import bleach
import datetime
import tornado.web
import json
import random
import string
import glob

from settings import testing

import aswwu.models.pages as pages_model
from aswwu.base_handlers import BaseHandler


class UploadHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            fileinfo = self.request.files['file'][0]
            if not testing['dev']:
                server_url = 'https://aswwu.com/pages/media/static/'
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
        except Exception:
            response = {'error': str(sys.exc_info()[1])}
        self.write({"link": server_url + new_filename})


class LoadAllHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not testing['dev']:
            server_url = 'https://aswwu.com/pages/media/static/'
        else:
            server_url = 'http://localhost:8888/pages/media/static/'
        image_list = []
        for f in glob.glob("../media/cms/*"):
            filename = os.path.basename(f)
            image_list.append({
                "url": server_url + filename,
                "thumb": server_url + filename,
                "name": filename})
        self.write(json.dumps(image_list))


class LoadImageHandler(BaseHandler):
    def get(self, filename):
        image = open(glob.glob("../media/cms/" + filename)[0], "r")
        self.write(image.read())
