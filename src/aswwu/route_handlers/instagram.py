import logging

from tornado.httpclient import HTTPClient

from src.aswwu.base_handlers import BaseHandler
from settings import environment

logger = logging.getLogger(environment["log_name"])


# This is the instagram handler for the atlas (I did this to hide the access token).
class FeedHandler(BaseHandler):
    def get(self):
        name = self.get_argument('name', '')
        if name == "atlas":
            with open("/var/www/atlas/access.token", 'r') as f:
                token = f.read()
                f.close()
                token = token.rstrip('\n')
                # TODO: Make this asynchronous and move access.token to aswwu/databases git repo
                http_client = HTTPClient()
                try:
                    response = http_client.fetch("https://api.instagram.com/v1/users/self/media/recent/?access_token="
                                                 + token)
                    self.write(response.body)
                except Exception as e:
                    self.write("{error: '" + str(e) + "'}")
                http_client.close()
        elif name == "issuu":
            http_client = HTTPClient()
            try:
                response = http_client.fetch("http://search.issuu.com/api/2_0/document?username=aswwucollegian&pageSize"
                                             "=1&responseParams=title,description&sortBy=epoch")
                self.write(response.body)
            except Exception as e:
                self.write("{error: '" + str(e) + "'}")
            http_client.close()
        else:
            self.write("Something went wrong.")
