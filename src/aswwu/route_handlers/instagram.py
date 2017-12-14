import logging

from tornado.httpclient import HTTPClient

from src.aswwu.base_handlers import BaseHandler

logger = logging.getLogger("aswwu")


# This is the instagram handler for the atlas (I did this to hide the access token).
class FeedHandler(BaseHandler):
    def get(self):
        name = self.get_argument('name', '')
        if name == "atlas":
            self.get_atlas()
        elif name == "issuu":
            self.get_issuu()
        else:
            self.write("Something went wrong.")

    def get_atlas(self):
        with open("/var/www/atlas/access.token", 'r') as f:
            token = f.read()
            f.close()
            token = token.rstrip('\n')
            # TODO: Make this asynchronous and move access.token to aswwu/databases git repo
            http_client = HTTPClient()
            try:
                url = "https://api.instagram.com"\
                        "/v1/users/self/media/recent/?access_token="
                response = http_client.fetch(url + token)
                self.write(response.body)
            except Exception as e:
                self.write("{error: '" + str(e) + "'}")
            http_client.close()

    def get_issuu(self):
        http_client = HTTPClient()
        try:
            url = "http://search.issuu.com/api/2_0/"\
                    "document?username=aswwucollegian&pageSize=1"\
                    "&responseParams=title,description&sortBy=epoch"
            response = http_client.fetch(url)
            self.write(response.body)
        except Exception as e:
            self.write("{error: '" + str(e) + "'}")
        http_client.close()
