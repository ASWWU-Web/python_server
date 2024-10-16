import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from src.aswwu.models.bases import PagesBase


class Page(PagesBase):
    __tablename__ = 'pages'

    url = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    content = Column(String(5000))
    cover_image = Column(String(250))
    owner = Column(String(50))
    editors = relationship("PageEditor", backref="Page_Editor", lazy="joined")
    author = Column(String(50))
    is_visible = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.datetime.now)
    tags = relationship("PageTag", backref="Page_Tag", lazy="joined")
    category = Column(String(50), ForeignKey('categories.category'))
    department = Column(String(100), ForeignKey('departments.department'))
    extra_info = Column(String(500))
    current = Column(Boolean)
    # TODO: Every 24 hours is an editing period for a page.
    # Past that, the previous one is archived and a new one is created

    def serialize(self):
        tag_list = []
        for tag in self.tags:
            tag_list.append(tag.tag)
        editor_list = []
        for editor in self.editors:
            editor_list.append(editor.username)
        return {'url': self.url,
                'title': self.title,
                'description': self.description,
                'content': self.content,
                'owner': self.owner,
                'editors': editor_list,
                'author': self.author,
                'is_visible': self.is_visible,
                'created': self.created.isoformat(),
                'tags': tag_list,
                'category': self.category,
                'department': self.department,
                'current': self.current,
                'extra_info': self.extra_info,
                'cover_image': self.cover_image}

    def serialize_preview(self):
        tag_list = []
        for tag in self.tags:
            tag_list.append(tag.tag)
        return {'url': self.url,
                'title': self.title,
                'description': self.description,
                'owner': self.owner,
                'author': self.author,
                'created': self.created.isoformat(),
                'visible': self.is_visible,
                'tags': tag_list,
                'category': self.category,
                'department': self.department,
                'cover_image': self.cover_image}

    def serialize_revisions_preview(self):
        return {
                'id': self.id,
                'url': self.url,
                'title': self.title,
                'description': self.description,
                'created': self.created.isoformat(),
                'visible': self.is_visible,
                'current': self.current,
                'last_updated': self.updated_at.isoformat()
                }


class PageEditor(PagesBase):
    __tablename__ = 'pageeditors'

    username = Column(String(50))
    url = Column(String(50), ForeignKey('pages.url'))


class PageTag(PagesBase):
    __tablename__ = 'pagetags'

    tag = Column(String(50))
    url = Column(String(50), ForeignKey('pages.url'))


class Category(PagesBase):
    __tablename__ = 'categories'

    category = Column(String(50), unique=True)
    description = Column(String(250))

    def serialize(self):
        return {'category': self.category}

    def serialize_full(self):
        return {
            'category': self.category,
            'description': self.description
        }


class Department(PagesBase):
    __tablename__ = 'departments'

    department = Column(String(50), unique=True)
    description = Column(String(250))
    color = Column(String(50))

    def serialize(self):
        return {'department': self.department}

    def serialize_full(self):
        return {
            'department': self.department,
            'description': self.description,
            'color': self.color
        }

class Featured(PagesBase):
    __tablename__ = 'featureds'

    url = Column(String(50), ForeignKey('pages.url'))
    # TODO: unnecessary column
    featured = Column(Boolean)
