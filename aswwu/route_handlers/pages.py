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
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)
            if 'pages' not in user.roles and 'administrator' not in user.roles:
                self.set_status(401)
                self.write({'error': 'insufficient permissions'})
                return
            page = alchemy.admin_query_by_page_url(body_json['url'])
            if page is not None:
                self.set_status(409)
                self.write({'error': 'Page with that url already exists'})
                return
            page = pages_model.Page()
            new_tags = []
            new_editors = []
            for key in body_json:
                if hasattr(pages_model.Page, key):
                    if key == "tags":
                        tags = body_json["tags"]
                        for tag in tags:
                            new_tags.append(tag)
                    elif key == "editors":
                        editors = body_json["editors"]
                        for editor in editors:
                            new_editors.append(editor)
                    elif key == "category":
                        categories = alchemy.get_categories()
                        if any(body_json["category"] == category.category for category in categories):
                            setattr(page, key, body_json["category"])
                        else:
                            self.set_status(412)
                            self.write({"status": "category does not exist"})
                            return
                    elif key == "department":
                        departments = alchemy.get_departments()
                        if any(body_json["department"] == department.department for department in departments):
                            setattr(page, key, body_json["department"])
                        else:
                            self.set_status(412)
                            self.write({"status": "department does not exist"})
                            return
                    else:
                        setattr(page, key, body_json[key])
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
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)
            page = alchemy.admin_query_by_page_url(url)
            today = datetime.datetime.today().date()
            if getattr(page, "updated_at").date() < today:
                setattr(page, "current", False)
                alchemy.add_or_update_page(page)
                page = pages_model.Page(url=url, owner=user.username, current=True, created=page.created)
            if user.username != page.owner \
                    and user.username not in page.editors:
                self.set_status(401)
                self.write({'error': 'insufficient permissions'})
                return
            new_tags = []
            new_editors = []
            for key in body_json:
                if hasattr(pages_model.Page, key):
                    if key == "tags":
                        tags = body_json[key]
                        for tag in tags:
                            new_tags.append(tag)
                    elif key == "editors":
                        editors = body_json[key]
                        for editor in editors:
                            new_editors.append(editor)
                    elif key != "url":
                        setattr(page, key, body_json[key])
            page.current = True
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

            self.write({"status": "Page Updated"})
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
    @tornado.web.authenticated
    def get(self, url):
        try:
            pages = alchemy.get_all_page_revisions(url)
            self.write({"results": [p.serialize_revisions_preview() for p in pages]})
        except Exception as e:
            logger.error("GetAllHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})


class SpecificRevisionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, url, revision_id):
        try:
            page = alchemy.get_specifc_page_revision(url, revision_id)
            self.write(page.serialize())
        except Exception as e:
            logger.error("GetAllHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})

    @tornado.web.authenticated
    def post(self, url, revision_id):
        try:
            page = alchemy.admin_query_by_page_url(url)
            revision = alchemy.get_specifc_page_revision(url, revision_id)
            setattr(page, "current", False)
            alchemy.add_or_update_page(page)
            page = pages_model.Page()
            for field in revision.serialize():
                setattr(page, field, getattr(revision, field))
            page.current = True
            alchemy.add_or_update_page(page)
            self.write({"status": "Revision Restored"})
        except Exception as e:
            logger.error("GetAllHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({'status': 'error'})
