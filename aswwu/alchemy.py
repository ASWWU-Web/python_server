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
from aswwu.archive_models import ArchiveBase

Base = base.Base
ElectionBase = base.ElectionBase
PagesBase = base.PagesBase
JobsBase = base.JobsBase

logger = logging.getLogger("aswwu")

# defines the databases URLs relative to "server.py"
engine = create_engine("sqlite:///../databases/people.db")
archive_engine = create_engine("sqlite:///../databases/archives.db")
election_engine = create_engine("sqlite:///../databases/senate_elections.db")
pages_engine = create_engine("sqlite:///../databases/pages.db")
jobs_engine = create_engine("sqlite:///../databases/jobs.db")

# create the model tables if they don't already exist
Base.metadata.create_all(engine)
ElectionBase.metadata.create_all(election_engine)
PagesBase.metadata.create_all(pages_engine)
JobsBase.metadata.create_all(jobs_engine)

# bind instances of the databases to corresponding variables
Base.metadata.bind = engine
dbs = sessionmaker(bind=engine)
people_db = dbs()
# same for archives
ArchiveBase.metadata.bind = archive_engine
archive_dbs = sessionmaker(bind=archive_engine)
archive_db = archive_dbs()
# same for elections
ElectionBase.metadata.bind = election_engine
election_dbs = sessionmaker(bind=election_engine)
election_db = election_dbs()
# same for pages
PagesBase.metadata.bind = pages_engine
pages_dbs = sessionmaker(bind=pages_engine)
page_db = pages_dbs()

# TODO: Figure out the consequences of this mistake
JobsBase.metadata.bind = election_engine
jobs_dbs = sessionmaker(bind=jobs_engine)
jobs_db = jobs_dbs()


# updates a model, or creates it if it doesn't exist
def add_or_update(thing):
    try:
        people_db.add(thing)
        people_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        people_db.rollback()


# finds all rows for a given model
def query_all(model):
    thing = None
    try:
        thing = people_db.query(model).all()
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


def search_all_profiles():
    thing = None
    try:
        # thing = people_db.execute("SELECT username, full_name, photo, email, real_views FROM (profiles LEFT JOIN (SELECT viewed, SUM(num_views) AS real_views FROM profileviews GROUP BY viewed) AS pv ON profiles.username = pv.viewed)")
        thing = people_db.query(mask_model.Profile, label("views", func.sum(mask_model.ProfileView.num_views))). \
            join(mask_model.Profile.views). \
            group_by(mask_model.ProfileView.viewed). \
            order_by(desc("views"))
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


def search_term_generator(search_criteria):
    for key in search_criteria:
        if key == "gender":
            yield mask_model.Profile.gender.ilike(search_criteria["gender"])
        if key == "username" or key == "full_name":
            yield and_(mask_model.Profile.username.ilike("%" + search_criteria[key] + "%") + mask_model.Profile.full_name.ilike("%" + search_criteria[key] + "%"))
        else:
            yield getattr(mask_model.Profile, key).ilike("%" + search_criteria[key] + "%")


def search_profiles(search_criteria):
    thing = None
    try:
        search_statement = and_(search_term_generator(search_criteria))
        thing = people_db.query(mask_model.Profile, label("views", func.sum(mask_model.ProfileView.num_views))). \
            filter(search_statement). \
            join(mask_model.Profile.views). \
            group_by(mask_model.ProfileView.viewed).\
            order_by(desc("views"))
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


def num_views(username):
    thing = None
    try:
        thing = people_db.query(label("views", func.sum(mask_model.ProfileView.num_views))). \
            group_by(mask_model.ProfileView.viewed). \
            filter(mask_model.ProfileView.viewed == username)
        try:
            thing = thing.one().views
        except Exception:
            thing = None
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


# finds all rows for a given model matching the given WWUID
def query_by_wwuid(model, wwuid):
    thing = None
    try:
        thing = people_db.query(model).filter_by(wwuid=str(wwuid)).all()
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


# finds all rows for a given model matching the given ID
def query_by_id(model, aid):
    thing = None
    try:
        thing = people_db.query(model).filter_by(id=aid).first()
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


# finds all rows for a given model matching the given field=value
def query_by_field(model, field, value):
    thing = None
    try:
        thing = people_db.query(model).filter(getattr(model, field).like(value)).all()
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


# finds a user with the given WWUID
def query_user(wwuid):
    thing = query_by_wwuid(mask_model.User, str(wwuid))
    if thing:
        thing = thing[0]
    return thing


# permanently deletes a given model
def delete_thing(thing):
    try:
        people_db.delete(thing)
        people_db.commit()
    except Exception as e:
        logger.info(e)
        people_db.rollback()


def query_all_election(model):
    thing = None
    try:
        thing = election_db.query(model).all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


def add_or_update_election(thing):
    try:
        election_db.add(thing)
        election_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        election_db.rollback()


# finds all rows for a given model matching the given WWUID
def query_by_wwuid_election(model, wwuid):
    thing = None
    try:
        thing = election_db.query(model).filter_by(wwuid=str(wwuid)).all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


# updates a model, or creates it if it doesn't exist
def add_or_update_form(thing):
    try:
        jobs_db.add(thing)
        jobs_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        jobs_db.rollback()


def query_by_job_name(model, name):
    thing = None
    try:
        thing = jobs_db.query(model).options(joinedload('*')).filter_by(job_name=str(name)).all()
    except Exception as e:
        logger.info(e)
        jobs_db.rollback()
    return thing


def query_all_forms(model):
    thing = None
    try:
        thing = jobs_db.query(model).all()
    except Exception as e:
        logger.info(e)
        jobs_db.rollback()
    return thing


# permanently deletes a given model
def delete_thing_forms(thing):
    try:
        jobs_db.delete(thing)
        jobs_db.commit()
    except Exception as e:
        logger.info(e)
        jobs_db.rollback()


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


def get_admin_pages(user):
    thing = None
    try:
        owned_pages = page_db.query(pages_model.Page).options(joinedload('*'))\
            .filter_by(owner=user, current=True).all()
        editables = page_db.query(pages_model.PageEditor)\
            .options(joinedload('*')).filter_by(username=user).all()
        editable_pages = []
        for editable in editables:
            editable_pages.append(admin_query_by_page_url(editable.url))
        thing = owned_pages + editable_pages
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


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


def get_featureds(url):
    thing = None
    try:
        thing = page_db.query(pages_model.Featured).options(joinedload('*'))\
            .filter_by(url=str(url)).all()
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


def get_specifc_page_revision(url, revision_id):
    thing = None
    try:
        thing = page_db.query(pages_model.Page).options(joinedload('*'))\
            .filter_by(id=revision_id, url=url).one()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


# permanently deletes a given model
def delete_pages_thing(thing):
    try:
        page_db.delete(thing)
        page_db.commit()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
