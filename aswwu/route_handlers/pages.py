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
                self.set_status(404)
                self.write({'status': 'No page by that URL'})
            else:
                self.write(page.serialize())
        except Exception as e:
            logger.error("GetHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})


class AdminAllHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        try:
            user = self.current_user
            pages = alchemy.get_admin_pages(user.username)
            self.write({"results": [p.serialize_preview() for p in pages]})
        except Exception as e:
            logger.error("AdminAllHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})

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


class AdminSpecificPageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, url):
        try:
            user = self.current_user
            pages = alchemy.get_admin_pages(user.username)
            for page in pages:
                if page.url == url:
                    self.write(page.serialize())
                    return
            self.set_status(404)
            self.write({'status': 'No page by that URL'})
        except Exception as e:
            logger.error("AdminSpecificPageHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})


class SearchHandler(BaseHandler):
    def get(self):
        try:
            search_criteria = {}
            # Put query into JSON form
            query = self.request.arguments
            for key, value in query.items():
                search_criteria[key] = value[0]
            results = alchemy.search_pages(search_criteria)
            self.write({'results': [p.serialize_preview() for p in results]})
        except Exception as e:
            logger.error("SearchHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})
