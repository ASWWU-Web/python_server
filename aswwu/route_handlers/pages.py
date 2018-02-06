import logging

import bleach
import tornado.web

from aswwu.base_handlers import BaseHandler
import aswwu.models.pages as pages_model
import aswwu.alchemy as alchemy

logger = logging.getLogger("aswwu")


class GetAllHandler(BaseHandler):
    def get(self):
        try:
            # page = alchemy.query_by_page_id(pages_model.Page, page_id)
            # TODO: Need get all alchemy function
            if len(page) == 0:
                self.write({'error': 'no page found'})
            elif len(page) > 1:
                self.write({'error': 'too many pages found'})
            else:
                logger.info(page[0].serialize())
                self.write(page[0].serialize())
        except Exception as e:
            logger.error("PagesHandler: error.\n" + str(e.message))
            self.write({'error': str(e.message)})


class SpecificPageHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, url):
        try:
            user = self.current_user
            page = alchemy.query_by_url(pages_model.Page, url)
            editors = []
            for temp_dict in page[0].serialize()['editors']:
                temp = temp_dict['name']
                editors.append(temp)
            print(editors)
            if user.username in editors or user.username == page.author:
                if not len(page):
                    page = [pages_model.Page()]
                elif len(page) > 1:
                    raise ValueError('Too many pages found')
                else:
                    page[0].url = bleach.clean(self.get_argument('url'))
                    page[0].title = bleach.clean(self.get_argument('title'))
                    page[0].content = bleach.clean(
                        self.get_argument('content'))
                    page[0].author = bleach.clean(self.get_argument('author'))
                    page[0].editors = bleach.clean(
                        self.get_argument('editors'))
                    page[0].is_visible = bleach.clean(
                        self.get_argument('is_visible'))
                    page[0].tags = bleach.clean(self.get_argument('tags'))
                    page[0].category = bleach.clean(
                        self.get_argument('category'))
                    page[0].theme_blob = bleach.clean(
                        self.get_argument('theme_blob'))
                alchemy.add_or_update_page(page[0])

        except Exception as e:
            logger.error("PagesUpdateHandler: error.\n" + str(e.message))
