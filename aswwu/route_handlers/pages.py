import logging

import bleach
import datetime
import tornado.web
import json

import aswwu.alchemy as alchemy
import aswwu.models.pages as pages_model
from aswwu.base_handlers import BaseHandler

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
                self.write({'status': 'no page by that URL'})
            else:
                self.write(page.serialize())
        except Exception as e:
            logger.error("GetHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})


class CategoryHandler(BaseHandler):
    def get(self):
        try:
            categories = alchemy.get_categories()
            categories_json = {
                'categories': []
            }
            for category in categories:
                categories_json['categories'].append(category.serialize_full())
            self.write(categories_json)
        except Exception as e:
            logger.error("CategoryHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})


class DepartmentHandler(BaseHandler):
    def get(self):
        try:
            departments = alchemy.get_departments()
            departments_json = {
                'departments': []
            }
            for department in departments:
                departments_json['departments'].append(department.serialize_full())
            self.write(departments_json)
        except Exception as e:
            logger.error("DepartmentHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})


class TagsHandler(BaseHandler):
    def get(self):
        try:
            tags = alchemy.get_all_tags()
            unique_tags = []
            for tag in tags:
                if tag.tag not in unique_tags:
                    unique_tags.append(tag.tag)
            self.write({'tags': unique_tags})
        except Exception as e:
            logger.error("DepartmentHandler: error.\n" + str(e.message))
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
                return
            page = alchemy.query_by_page_url(self.get_argument("url"))
            if page is not None:
                self.set_status(409)
                self.write({'error': 'Page with that url already exists'})
                return
            page = pages_model.Page()
            query = self.request.arguments
            new_tags = []
            new_editors = []
            for key, value in query.items():
                if hasattr(pages_model.Page, key):
                    if key == "tags":
                        tags = json.loads(value[0])['tags']
                        for tag in tags:
                            new_tags.append(tag)
                    elif key == "editors":
                        editors = json.loads(value[0])['editors']
                        for editor in editors:
                            new_editors.append(editor)
                    elif key == "category":
                        categories = alchemy.get_categories()
                        matched = False
                        for category in categories:
                            if category.category == value[0]:
                                setattr(page, key, category.category)
                                matched = True
                                break
                        if not matched:
                            self.set_status(412)
                            self.write({"status": "category does not exist"})
                            return
                    elif key == "department":
                        departments = alchemy.get_departments()
                        matched = False
                        for department in departments:
                            if department.department == value[0]:
                                setattr(page, key, department.department)
                                matched = True
                                break
                        if not matched:
                            self.set_status(412)
                            self.write({"status": "department does not exist"})
                            return
                    else:
                        setattr(page, key, value[0])
            page.owner = user.username
            page.current = True
            alchemy.add_or_update_page(page)
            for tag in new_tags:
                t = pages_model.PageTag(tag=tag, url=page.url)
                alchemy.add_or_update_page(t)
            for editor in new_editors:
                ed = pages_model.PageEditor(username=editor, url=page.url)
                alchemy.add_or_update_page(ed)
            self.write({"status": "page created"})
        except Exception as e:
            logger.error("AdminAllHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class AdminSpecificPageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, url):
        try:
            page = alchemy.admin_query_by_page_url(url)
            user = self.current_user
            if not page:
                self.set_status(404)
                self.write({'status': 'no page by that URL'})
                return
            if page.owner == user.username:
                self.write(page.serialize())
                return
            editors = alchemy.get_editors(url)
            for editor in editors:
                if editor.username == user.username:
                    self.write(page.serialize())
                    return
            self.set_status(403)
            self.write({'status': 'insufficient permissions'})
        except Exception as e:
            logger.error("AdminSpecificPageHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})

    @tornado.web.authenticated
    def post(self, url):
        try:
            user = self.current_user
            query = self.request.arguments
            page = alchemy.admin_query_by_page_url(url)
            today = datetime.datetime.today().date()
            owner = False
            if getattr(page, "updated_at").date() < today:
                setattr(page, "current", False)
                alchemy.add_or_update_page(page)
                page = pages_model.Page(url=url, owner=user.username)
            editors = [editor.username for editor in page.editors]
            if user.username == page.owner:
                owner = True
            elif user.username != page.owner and user.username not in editors:
                self.set_status(401)
                self.write({'error': 'insufficient permissions'})
                return
            new_tags = []
            new_editors = []
            for key, value in query.items():
                if hasattr(pages_model.Page, key):
                    if key == "tags":
                        tags = json.loads(value[0])['tags']
                        for tag in tags:
                            new_tags.append(tag)
                    elif key == "editors" and owner:
                        editors = json.loads(value[0])['editors']
                        for editor in editors:
                            new_editors.append(editor)
                    elif key == "title" or key == "description" or key == "content":
                        setattr(page, key, value[0])
                    # TODO: verify not allowed variables aren't set
                    elif key != "url" and owner:
                        setattr(page, key, value[0])
            page.current = True
            # TODO: set updated time
            alchemy.add_or_update_page(page)

            # Manage deletion or addition of editors
            for editor in alchemy.query_page_editors(url=page.url):
                if editor.username not in new_editors:
                    alchemy.delete_pages_thing(editor)
                else:
                    new_editors.remove(editor.username)
            for editor in new_editors:
                ed = alchemy.query_page_editor(username=editor, url=page.url)
                if ed is None:
                    ed = pages_model.PageEditor(username=editor, url=page.url)
                    alchemy.add_or_update_page(ed)

            # Manage deletion or addition of editors
            for tag in alchemy.query_page_tags(url=page.url):
                if tag.tag not in new_tags:
                    alchemy.delete_pages_thing(tag)
                else:
                    new_tags.remove(tag.tag)
            for tag in new_tags:
                t = alchemy.query_page_tag(tag=tag, url=page.url)
                if t is None:
                    t = pages_model.PageTag(tag=tag, url=page.url)
                    alchemy.add_or_update_page(t)

            self.write({"status": "page updated"})
        except Exception as e:
            logger.error("AdminSpecificPageHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})

    @tornado.web.authenticated
    def delete(self, url):
        try:
            page = alchemy.admin_query_by_page_url(url)
            if not page:
                self.set_status(404)
                self.write({'status': 'no page by that URL'})
                return
            user = self.current_user
            if page.owner == user.username:
                page.current = False
                alchemy.add_or_update_page(page)
                self.write({'status': 'page deleted'})
            else:
                self.set_status(403)
                self.write({'status': 'insufficient permissions'})
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
                search_criteria[key] = value[0].lower()
            results = alchemy.search_pages(search_criteria)
            self.write({'results': [p.serialize_preview() for p in results]})
        except Exception as e:
            logger.error("SearchHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class GetAllRevisionsHandler(BaseHandler):
    def get(self, url):
        try:
            pages = alchemy.get_all_page_revisions(url)
            self.write({"results": [p.serialize_revisions_preview() for p in pages]})
        except Exception as e:
            logger.error("GetAllHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})
