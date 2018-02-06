import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import aswwu.models.bases as base

PagesBase = declarative_base(cls=base.PagesBase)


class Page(PagesBase):
    url = Column(String(50), unique=True, nullable=False)
    title = Column(String(100), unique=True, nullable=False)
    content = Column(String(5000))
    owner = Column(String(50))
    editors = relationship("PageEditor", backref="Page_Editor", lazy="joined")
    is_visible = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.datetime.now())
    tags = relationship("PageTag", backref="Page_Tag", lazy="joined")
    category = Column(String(50), ForeignKey('categories.category_title'))
    department = Column(String(100), ForeignKey('departments.name'))
    current = Column(Boolean)
    # TODO: Every 24 hours is an editing period for a page.
    # Past that, the previous one is archived and a new one is created

    def serialize(self):
        tag_list = []
        for tag in self.tags:
            tag_list.append(tag.tag)
        editor_list = []
        for editor in self.editors:
            editor_list.append(editor.serialize())
        return {'url': self.url, 'title': self.title, 'content': self.content,
                'author': self.author, 'is_visible': self.is_visible,
                'last_update': self.last_update, 'category': self.category,
                'theme_blob': self.theme_blob, 'editors': editor_list,
                'tags': tag_list}


class PageEditor(PagesBase):
    editor_username = Column(String(50))
    pageID = Column(String(50), ForeignKey('pages.id'))


class PageTag(PagesBase):
    tag = Column(String(50))
    pageID = Column(String(50), ForeignKey('pages.id'))


class Category(PagesBase):
    category_title = Column(String(50), unique=True)
    category_description = Column(String(250))

    def serialize(self):
        return {'category': self.category_title}


class Featured(PagesBase):
    page = Column(String(50), ForeignKey('pages.url'))
    featured = Column(Boolean)
