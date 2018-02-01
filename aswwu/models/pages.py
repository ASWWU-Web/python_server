import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import aswwu.models.bases as base

PagesBase = declarative_base(cls=base.PagesBase)


class Page(PagesBase):
    url = Column(String(50), unique=True, nullable=False)
    title = Column(String(50), unique=True, nullable=False)
    content = Column(String(5000))
    author = Column(String(7), nullable=False)
    editors = relationship("PageEditor", backref="Page_Editor", lazy="joined")
    is_visible = Column(Boolean, default=False)
    last_update = Column(DateTime, onupdate=datetime.datetime.now)
    tags = Column(String(250))
    category = Column(String(50), default='Other')
    theme_blob = Column(String(150))
    current = Column(Boolean)
    # TODO: Every 24 hours is an editing period for a page. Past that, the previous one is archived and a new one is created

    def serialize(self):
        tag_list = []
        for tag in self.tags:
            tag_list.append(tag.tag)
        editor_list = []
        for editor in self.editors:
            editor_list.append(editor.serialize())
        return {'url': self.url, 'title': self.title, 'content': self.content, 'author': self.author,
                'is_visible': self.is_visible, 'last_update': self.last_update, 'category': self.category,
                'theme_blob': self.theme_blob, 'editors': editor_list, 'tags': tag_list}


class PageEditor(PagesBase):
    editor_name = Column(String(50))
    editor_username = Column(String(50))
    editor_wwuid = Column(String(50))
    pageID = Column(String(50), ForeignKey('pages.id'))

    def serialize(self):
        return {'name': self.editor_name, 'username': self.editor_username}
