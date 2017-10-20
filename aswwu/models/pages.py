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
    tags = relationship("PageTag", backref="Pages", lazy="joined")
    category = Column(String(50), default='Other')
    theme_blob = Column(String(150))

    def serialize(self):
        taggies = []
        for tag in self.tags:
            taggies.append(tag.tag)
        eddies = []
        for editor in self.editors:
            eddies.append(editor.serialize())
        return {'url': self.url, 'title': self.title, 'content': self.content, 'author': self.author,
                'is_visible': self.is_visible, 'last_update': self.last_update, 'category': self.category,
                'theme_blob': self.theme_blob, 'editors': eddies, 'tags': taggies}


class PageTag(PagesBase):
    tag = Column(String(50))
    pageID = Column(String(50), ForeignKey('pages.id'))

    def serialize(self):
        return {'tag': self.tag}


class PageEditor(PagesBase):
    editor_name = Column(String(50))
    editor_username = Column(String(50))
    editor_wwuid = Column(String(50))
    pageID = Column(String(50), ForeignKey('pages.id'))

    def serialize(self):
        return {'name': self.editor_name, 'username': self.editor_username}
