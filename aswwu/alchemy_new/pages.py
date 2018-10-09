# alchemy.py

# import and set up the logging
import ast
import logging

from sqlalchemy import create_engine, func, or_, and_, desc
from sqlalchemy.orm import sessionmaker, joinedload, class_mapper
from sqlalchemy.sql import label

import aswwu.models.bases as base
import aswwu.models.mask as mask_model
import aswwu.models.pages as pages_model

PagesBase = base.PagesBase

logger = logging.getLogger("aswwu")

# defines the databases URLs relative to "server.py"
pages_engine = create_engine("sqlite:///../databases/pages.db")

# create the model tables if they don't already exist
PagesBase.metadata.create_all(pages_engine)

# same for pages
PagesBase.metadata.bind = pages_engine
pages_dbs = sessionmaker(bind=pages_engine)
page_db = pages_dbs()

# Section for ASWWU Pages Functions

# updates a model, or creates it if it doesn't exist
def add_or_update_page(thing):
    try:
        page_db.add(thing)
        page_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        page_db.rollback()
        raise Exception(e)


def delete_thing_pages(thing):
    try:
        page_db.delete(thing)
        page_db.commit()
    except Exception as e:
        logger.info(e)
        jobs_db.rollback()


def query_by_page_url(url):
    thing = None
    try:
        thing = page_db.query(pages_model.Page).options(joinedload('*'))\
            .filter_by(url=str(url), is_visible=True, current=True).one()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def admin_query_by_page_url(url):
    thing = None
    try:
        thing = page_db.query(pages_model.Page).options(joinedload('*'))\
            .filter_by(url=str(url), current=True).one()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_all_pages():
    thing = None
    try:
        thing = page_db.query(pages_model.Page).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def pages_general_search_term_generator(search_criteria):
    """Search for a general search term in all fields"""
    # Search in all fields(except tags and editors)
    for prop in class_mapper(pages_model.Page).iterate_properties:
        if str(prop.key) != "editors" and str(prop.key) != "tags":
            yield getattr(pages_model.Page, prop.key)\
                .ilike("%" + search_criteria["general"] + "%")
    # Search all tags
    for x in pages_specific_search_term_generator(
            {"tags": "[\"" + search_criteria["general"] + "\"]"}):
        yield x


def pages_specific_search_term_generator(search_criteria):
    """Search by specific field."""
    for key in search_criteria:
        if hasattr(pages_model.Page, key):
            if key == "tags":
                search_tags = ast.literal_eval(search_criteria[key])
                for tag in search_tags:
                    page_tags = page_db.query(pages_model.PageTag)\
                        .filter_by(tag=tag).all()
                    for db_tag in page_tags:
                        yield getattr(pages_model.Page, "url").\
                            ilike(db_tag.url)
            else:
                yield getattr(pages_model.Page, key).\
                    ilike("%" + search_criteria[key] + "%")
    if not (len(search_criteria) == 1 and "tags" in search_criteria):
        yield getattr(pages_model.Page, "current").ilike(1)
        yield getattr(pages_model.Page, "is_visible").ilike(1)


def search_pages(search_criteria):
    """General search function for ASWWU pages."""
    thing = None
    try:
        if len(search_criteria) == 1 and "general" in search_criteria:
            search_statement = or_(
                pages_general_search_term_generator(search_criteria)
            )
            search_statement = and_(
                search_statement,
                getattr(pages_model.Page, "current").ilike(1),
                getattr(pages_model.Page, "is_visible").ilike(1)
            )
        else:
            search_statement = and_(
                pages_specific_search_term_generator(search_criteria)
            )
        thing = page_db.query(pages_model.Page). \
            filter(search_statement)
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_all_visible_current_pages():
    thing = None
    try:
        thing = page_db.query(pages_model.Page).options(joinedload('*'))\
            .filter_by(is_visible=True, current=True).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_all_current_pages():
    thing = None
    try:
        thing = page_db.query(pages_model.Page).options(joinedload('*')) \
            .filter_by(current=True).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_admin_pages(user):
    thing = None
    try:
        pages = page_db.query(pages_model.Page).outerjoin(pages_model.Page.editors)\
                    .filter(
            and_(
                pages_model.Page.current.ilike(1),
                or_(
                    pages_model.Page.owner.ilike(user),
                    pages_model.PageEditor.username.ilike(user)
                )
            )
        ).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return pages


def get_editors(url):
    thing = None
    try:
        thing = page_db.query(pages_model.PageEditor).options(joinedload('*'))\
            .filter_by(url=str(url)).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def query_page_tags(url):
    thing = None
    try:
        thing = page_db.query(pages_model.PageTag).options(joinedload('*'))\
            .filter_by(url=str(url)).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_all_tags():
    thing = None
    try:
        thing = page_db.query(pages_model.PageTag).options(joinedload('*')).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_tags(url):
    thing = None
    try:
        thing = page_db.query(pages_model.PageTag).options(joinedload('*'))\
            .filter_by(url=str(url)).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def query_page_tag(url, tag):
    thing = None
    try:
        thing = page_db.query(pages_model.PageTag).options(joinedload('*'))\
            .filter_by(url=str(url), tag=tag).one()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_all_featureds():
    thing = None
    try:
        thing = page_db.query(pages_model.Featured).options(joinedload('*')).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_featured(url):
    thing = None
    try:
        thing = page_db.query(pages_model.Featured).options(joinedload('*'))\
            .filter_by(url=str(url)).one()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def query_page_editors(url):
    thing = None
    try:
        thing = page_db.query(pages_model.PageEditor).options(joinedload('*'))\
            .filter_by(url=str(url)).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_categories():
    thing = None
    try:
        thing = page_db.query(pages_model.Category).options(joinedload('*')).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def query_page_editor(url, username):
    thing = None
    try:
        thing = page_db.query(pages_model.PageEditor).options(joinedload('*'))\
            .filter_by(url=str(url), username=username).one()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_departments():
    thing = None
    try:
        thing = page_db.query(pages_model.Department).options(joinedload('*')).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_all_page_revisions(url):
    thing = None
    try:
        thing = page_db.query(pages_model.Page).options(joinedload('*'))\
            .filter_by(url=url).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def get_specific_page_revision(url, revision_id):
    thing = None
    try:
        thing = page_db.query(pages_model.Page).options(joinedload('*'))\
            .filter_by(id=revision_id, url=url).one()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


# TODO: duplicate function
# permanently deletes a given model
def delete_pages_thing(thing):
    try:
        page_db.delete(thing)
        page_db.commit()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
