import logging

import bleach
import tornado.web
import ast

from aswwu.base_handlers import BaseHandler
import aswwu.models.pages as pages_model
import aswwu.alchemy as alchemy

logger = logging.getLogger("aswwu")


class GetAllHandler(BaseHandler):
    def get(self):
        try:
            pages = alchemy.get_all_visible_current_pages()
            self.write({"results": [p.serialize_preview() for p in pages]})
        except Exception as e:
            logger.error("GetAllHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})


class GetHandler(BaseHandler):
    def get(self, url):
        try:
            page = alchemy.query_by_page_url(url)
            if page is None:
                logger.error("PagesUpdateHandler: error.\n ")
                self.set_status(404)
                self.write({'error': "No page by that URL"})
            else:
                self.write(page.serialize())
        except Exception as e:
            logger.error("GetHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})


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


class AdminAllHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            if 'pages' not in user.roles and 'administrator' not in user.roles:
                self.set_status(401)
                self.write({'error': 'insufficient permissions'})
            page = pages_model.Page()
            query = self.request.arguments
            new_tags = []
            new_editors = []
            for key, value in query.items():
                if hasattr(pages_model.Page, key):
                    if key == "tags":
                        tags = ast.literal_eval(value[0])
                        for tag in tags:
                            new_tags.append(tag)
                    elif key == "editors":
                        editors = ast.literal_eval(value[0])
                        for editor in editors:
                            new_editors.append(editor)
                    else:
                        setattr(page, key, value[0])
            page.owner = user.username
            alchemy.add_or_update_page(page)
            for tag in new_tags:
                t = pages_model.PageTag(tag=tag, url=page.url)
                alchemy.add_or_update_page(t)
            for editor in new_editors:
                ed = pages_model.PageEditor(username=editor, url=page.url)
                alchemy.add_or_update_page(ed)
            self.write({"status": "Page Created"})
        except Exception as e:
            logger.error("AdminAllHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class SearchHandler(BaseHandler):
    def get(self):
        try:
            search_criteria = {}
            # Put query into JSON form
            query = self.request.arguments
            for key, value in query.items():
                search_criteria[key] = value
            results = alchemy.search_profiles(search_criteria)
            self.write({'results': [p.serialize_preview() for p in results]})
        except Exception as e:
            logger.error("SearchHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})
