# route_handlers.py

import tornado.web
import logging
import requests
import json
import datetime
import bleach
from tornado.httpclient import HTTPClient
from sqlalchemy import or_

# we'll need almost everything for this file
from aswwu.models import *
from aswwu.archive_models import *
from aswwu.alchemy import *
from aswwu.base_handlers import BaseHandler
from settings import keys

logger = logging.getLogger("aswwu")

# administrative role handler
class AdministratorRoleHandler(BaseHandler):
    # decorator to force them to be logged in to access this information
    # also only accepts post requests right now
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        # check if they have valid permissions
        if 'administrator' not in user.roles:
            self.write({'error': 'insufficient permissions'})
        else:
            cmd = self.get_argument('cmd', None)
            # grant permissions to other users
            # sharing is caring
            if cmd == 'set_role':
                username = self.get_argument('username', '').replace(' ','.').lower()
                fuser = s.query(User).filter_by(username=username).all()
                if not fuser:
                    self.write({'error': 'user does not exist'})
                else:
                    fuser = fuser[0]
                    if fuser.roles is None:
                        fuser.roles = ''
                    # roles are a comma separated list
                    # so we have to do some funkiness to append and then rejoin that list in the database
                    roles = fuser.roles.split(',')
                    roles.append(self.get_argument('newRole', None))
                    roles = set(roles)
                    fuser.roles = (',').join(roles)
                    addOrUpdate(fuser)
                    self.write({'response': 'success'})


# NOTE: this handler is no longer in use, but it is here for posterity
# class CollegianRoleHandler(BaseHandler):
#     @tornado.web.authenticated
#     def post(self):
#         user = self.current_user
#         if 'collegian' not in user.roles and 'collegian_admin' not in user.roles:
#             return self.write({'error': 'insufficient permissions'})
#
#         id = self.get_argument('id',None)
#         volume = self.get_argument('volume',None)
#         issue = self.get_argument('issue',None)
#         title = self.get_argument('title',None)
#         author = self.get_argument('author',None)
#         if 'collegian_admin' not in user.roles:
#             author = user.full_name
#         section = self.get_argument('section',None)
#         content = self.get_argument('content',None)
#
#         if not volume or not issue or not title or not author or not section or not content:
#             return self.write({'error': 'you must provide a volume, issue, title, author, section, and content for an article'})
#
#         logger.debug(id)
#         if id is not None and id != '':
#             collegian_article = query_by_id(CollegianArticle, id)
#             if not collegian_article:
#                 return self.write({'error': 'no Collegian Article with that ID exists'})
#         else:
#             collegian_article = CollegianArticle()
#
#         collegian_article.volume = volume
#         collegian_article.issue = issue
#         collegian_article.title = title
#         collegian_article.author = author
#         collegian_article.section = section
#         collegian_article.content = content
#
#         addOrUpdate(collegian_article)
#         self.write({'response': 'success'})


# NOTE: this handler is no longer in use, but it is here for posterity
# class CollegianSearchHandler(BaseHandler):
#     def get(self, query):
#         collegian_articles = query_all(CollegianArticle)
#
#         id = self.get_argument('id', None)
#         volume = self.get_argument('volume', None)
#         issue = self.get_argument('issue', None)
#         title = self.get_argument('title', None)
#         author = self.get_argument('author', None)
#         section = self.get_argument('section', None)
#
#         if id:
#             collegian_articles = [ca for ca in collegian_articles if str(ca.id) == str(id)]
#         if volume:
#             collegian_articles = [ca for ca in collegian_articles if str(ca.volume) == str(volume)]
#         if issue:
#             collegian_articles = [ca for ca in collegian_articles if str(ca.issue) == str(issue)]
#         if title:
#             collegian_articles = [ca for ca in collegian_articles if str(ca.title) == str(title)]
#         if author:
#             collegian_articles = [ca for ca in collegian_articles if str(ca.author).replace('.',' ').lower() == str(author).replace('.',' ').lower()]
#         if section:
#             collegian_articles = [ca for ca in collegian_articles if str(ca.section) == str(section)]
#
#         return self.write({'articles': [ca.to_json() for ca in collegian_articles]})


# this is the root of all searches
class SearchHandler(BaseHandler):
    # accepts a year and a query as parameters
    def get(self, year, query):
        # if searching in the current year, access the Profile model
        if year == self.application.options.current_year:
            model = Profile
            results = s.query(model)
        # otherwise we're going old school with the Archives
        else:
            model = globals()['Archive'+str(year)]
            results = archive_s.query(model)

        # break up the query <-- expected to be a standard URIEncodedComponent
        fields = [q.split("=") for q in query.split(";")]
        for f in fields:
            if len(f) == 1:
                # throw %'s around everything to make the search relative
                # e.g. searching for "b" will return anything that has b *somewhere* in it
                v = '%'+f[0].replace(' ','%').replace('.','%')+'%'
                results = results.filter(or_(model.username.ilike(v), model.full_name.ilike(v)))
            else:
                # we want these queries to matche exactly
                # e.g. "%male%" would also return "female"
                if f[0] in ['gender']:
                    results = results.filter(getattr(model,f[0]).ilike(f[1]))
                else:
                    attributeArr = f[1].encode('ascii','ignore').split(",")
                    if len(attributeArr) > 1:
                        results = results.filter(or_(getattr(model,f[0]).ilike("%" + v + "%") for v in attributeArr))
                    else:
                        results = results.filter(getattr(model,f[0]).ilike('%'+f[1]+'%'))
        self.write({'results': [r.base_info() for r in results]})


# get all of the profiles in our database
class SearchAllHandler(BaseHandler):
    def get(self):
        profiles = query_all(Profile)
        code = self.get_argument('code','')
        # pass in this super secret code to get ALL info for ALL profiles
        self.write({'results': [p.base_info() for p in profiles]})


# get user's profile information
class ProfileHandler(BaseHandler):
    def get(self, year, username):
        # check if we're looking at the current year or going old school
        if year == self.application.options.current_year:
            profile = s.query(Profile).filter_by(username=str(username)).all()
        else:
            profile = archive_s.query(globals()['Archive'+str(year)]).filter_by(username=str(username)).all()
        # some quick error checking
        if len(profile) == 0:
            self.write({'error': 'no profile found'})
        elif len(profile) > 1:
            self.write({'error': 'too many profiles found'})
        else:
            profile = profile[0]
            user = self.current_user
            # if the user is logged in and isn't vainly looking at themselves
            # then we assume the searched for user is popular and give them a +1
            if user and str(user.wwuid) != str(profile.wwuid) and year == self.application.options.current_year:
                if profile.views:
                    profile.views = profile.views+1
                else:
                    profile.views = 1
                addOrUpdate(profile)
            # self.write(profile.to_json())
            if not user:
                if profile.privacy == 1:
                    self.write(profile.impers_info())
                else:
                    self.write(profile.no_info())
            else:
                if user.username == profile.username:
                    self.write(profile.to_json())
                else:
                    self.write(profile.view_other())


# queries the server for a user's photos
class ProfilePhotoHandler(BaseHandler):
    def get(self, year, wwuidOrUsername):
        wwuid = None
        username = None
        if len(wwuidOrUsername.split(".")) == 1:
            wwuid = wwuidOrUsername
        else:
            username = wwuidOrUsername
        # check if we're looking at current photos or not
        if year == self.application.options.current_year:
            if wwuid:
                profile = query_by_wwuid(Profile, wwuid)
            else:
                profile = s.query(Profile).filter_by(username=str(username)).all()
        else:
            if wwuid:
                profile = archive_s.query(globals()['Archive'+str(year)]).filter_by(wwuid=str(wwuid)).all()
            else:
                profile = archive_s.query(globals()['Archive'+str(year)]).filter_by(username=str(username)).all()
        if len(profile) == 0:
            self.write({'error': 'no profile found'})
        elif len(profile) > 1:
            self.write({'error': 'too many profiles found'})
        else:
            # now we've got just one profile, return the photo field attached to a known photo URI
            profile = profile[0]
            self.redirect("https://aswwu.com/media/img-sm/"+str(profile.photo))




# this updates profile information - not much to it
class ProfileUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, username):
        user = self.current_user
        if user.username == username or 'administrator' in user.roles:
            profile = s.query(Profile).filter_by(username=str(username)).one()
            profile.full_name = bleach.clean(self.get_argument('full_name'))
            profile.photo = bleach.clean(self.get_argument('photo',''))
            profile.gender = bleach.clean(self.get_argument('gender',''))
            profile.birthday = bleach.clean(self.get_argument('birthday',''))
            profile.email = bleach.clean(self.get_argument('email',''))
            profile.phone = bleach.clean(self.get_argument('phone',''))
            profile.majors = bleach.clean(self.get_argument('majors',''))
            profile.minors = bleach.clean(self.get_argument('minors',''))
            profile.graduate = bleach.clean(self.get_argument('graduate',''))
            profile.preprofessional = bleach.clean(self.get_argument('preprofessional',''))
            profile.class_standing = bleach.clean(self.get_argument('class_standing',''))
            profile.high_school = bleach.clean(self.get_argument('high_school',''))
            profile.class_of = bleach.clean(self.get_argument('class_of',''))
            profile.relationship_status = bleach.clean(self.get_argument('relationship_status',''))
            profile.attached_to = bleach.clean(self.get_argument('attached_to',''))
            profile.quote = bleach.clean(self.get_argument('quote',''))
            profile.quote_author = bleach.clean(self.get_argument('quote_author',''))
            profile.hobbies = bleach.clean(self.get_argument('hobbies',''))
            profile.career_goals = bleach.clean(self.get_argument('career_goals',''))
            profile.favorite_books = bleach.clean(self.get_argument('favorite_books',''))
            profile.favorite_food = bleach.clean(self.get_argument('favorite_food',''))
            profile.favorite_movies = bleach.clean(self.get_argument('favorite_movies',''))
            profile.favorite_music = bleach.clean(self.get_argument('favorite_music',''))
            profile.pet_peeves = bleach.clean(self.get_argument('pet_peeves',''))
            profile.personality = bleach.clean(self.get_argument('personality',''))
            profile.privacy = bleach.clean(self.get_argument('privacy',''))
            profile.website = bleach.clean(self.get_argument('website',''))
            if user.status != "Student":
                profile.department = bleach.clean(self.get_argument('department',''))
                profile.office = bleach.clean(self.get_argument('office',''))
                profile.office_hours = bleach.clean(self.get_argument('office_hours',''))

            addOrUpdate(profile)
            self.write(json.dumps('success'))
        else:
            self.write({'error': 'invalid permissions'})


# fairly straightforward handler to save a TON of volunteer information
class VolunteerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, wwuid):
        user = self.current_user
        if user.wwuid == wwuid or 'volunteer' in user.roles:
            volunteer = query_by_wwuid(Volunteer, wwuid)
            if len(volunteer) == 0:
                volunteer = Volunteer(wwuid=user.wwuid)
                volunteer = addOrUpdate(volunteer)
            else:
                volunteer = volunteer[0]
            self.write(volunteer.to_json())
        else:
            self.write({'error': 'insufficient permissions'})

    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        volunteer = query_by_wwuid(Volunteer, user.wwuid)[0]

        volunteer.campus_ministries = (True if self.get_argument('campus_ministries', 0) == '1' else False)
        volunteer.student_missions = (True if self.get_argument('student_missions', 0) == '1' else False)
        volunteer.aswwu = (True if self.get_argument('aswwu', 0) == '1' else False)
        volunteer.circle_church = (True if self.get_argument('circle_church', 0) == '1' else False)
        volunteer.university_church = (True if self.get_argument('university_church', 0) == '1' else False)
        volunteer.buddy_program = (True if self.get_argument('buddy_program', 0) == '1' else False)
        volunteer.assist = (True if self.get_argument('assist', 0) == '1' else False)
        volunteer.lead = (True if self.get_argument('lead', 0) == '1' else False)
        volunteer.audio_slash_visual = (True if self.get_argument('audio_slash_visual', 0) == '1' else False)
        volunteer.health_promotion = (True if self.get_argument('health_promotion', 0) == '1' else False)
        volunteer.construction_experience = (True if self.get_argument('construction_experience', 0) == '1' else False)
        volunteer.outdoor_slash_camping = (True if self.get_argument('outdoor_slash_camping', 0) == '1' else False)
        volunteer.concert_assistance = (True if self.get_argument('concert_assistance', 0) == '1' else False)
        volunteer.event_set_up = (True if self.get_argument('event_set_up', 0) == '1' else False)
        volunteer.children_ministries = (True if self.get_argument('children_ministries', 0) == '1' else False)
        volunteer.children_story = (True if self.get_argument('children_story', 0) == '1' else False)
        volunteer.art_poetry_slash_painting_slash_sculpting = (True if self.get_argument('art_poetry_slash_painting_slash_sculpting', 0) == '1' else False)
        volunteer.organizing_events = (True if self.get_argument('organizing_events', 0) == '1' else False)
        volunteer.organizing_worship_opportunities = (True if self.get_argument('organizing_worship_opportunities', 0) == '1' else False)
        volunteer.organizing_community_outreach = (True if self.get_argument('organizing_community_outreach', 0) == '1' else False)
        volunteer.bible_study = (True if self.get_argument('bible_study', 0) == '1' else False)
        volunteer.wycliffe_bible_translator_representative = (True if self.get_argument('wycliffe_bible_translator_representative', 0) == '1' else False)
        volunteer.food_preparation = (True if self.get_argument('food_preparation', 0) == '1' else False)
        volunteer.graphic_design = (True if self.get_argument('graphic_design', 0) == '1' else False)
        volunteer.poems_slash_spoken_word = (True if self.get_argument('poems_slash_spoken_word', 0) == '1' else False)
        volunteer.prayer_team_slash_prayer_house = (True if self.get_argument('prayer_team_slash_prayer_house', 0) == '1' else False)
        volunteer.dorm_encouragement_and_assisting_chaplains = (True if self.get_argument('dorm_encouragement_and_assisting_chaplains', 0) == '1' else False)
        volunteer.scripture_reading = (True if self.get_argument('scripture_reading', 0) == '1' else False)
        volunteer.speaking = (True if self.get_argument('speaking', 0) == '1' else False)
        volunteer.videography = (True if self.get_argument('videography', 0) == '1' else False)
        volunteer.drama = (True if self.get_argument('drama', 0) == '1' else False)
        volunteer.public_school_outreach = (True if self.get_argument('public_school_outreach', 0) == '1' else False)
        volunteer.retirement_slash_nursing_home_outreach = (True if self.get_argument('retirement_slash_nursing_home_outreach', 0) == '1' else False)
        volunteer.helping_the_homeless_slash_disadvantaged = (True if self.get_argument('helping_the_homeless_slash_disadvantaged', 0) == '1' else False)
        volunteer.working_with_youth = (True if self.get_argument('working_with_youth', 0) == '1' else False)
        volunteer.working_with_children = (True if self.get_argument('working_with_children', 0) == '1' else False)
        volunteer.greeting = (True if self.get_argument('greeting', 0) == '1' else False)
        volunteer.shofar_for_vespers = (True if self.get_argument('shofar_for_vespers', 0) == '1' else False)
        volunteer.music = self.get_argument('music', '')
        volunteer.join_small_groups = (True if self.get_argument('join_small_groups', 0) == '1' else False)
        volunteer.lead_small_groups = (True if self.get_argument('lead_small_groups', 0) == '1' else False)
        volunteer.can_transport_things = (True if self.get_argument('can_transport_things', 0) == '1' else False)
        volunteer.languages = self.get_argument('languages', '')
        volunteer.berean_fellowship = self.get_argument('berean_fellowship', '')
        volunteer.wants_to_be_involved = (True if self.get_argument('wants_to_be_involved', 0) == '1' else False)

        logger.debug(volunteer.only_true())
        addOrUpdate(volunteer)
        self.write(json.dumps('success'))


# handler to search through volunteer information
class VolunteerRoleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        # check permissions
        if 'volunteer' not in user.roles:
            self.write({'error': 'insufficient permissions'})
        else:
            cmd = self.get_argument('cmd', None)
            logger.debug(cmd)
            if cmd == 'set_role':
                # let volunteer admins grant permissions for other volutneer admins
                username = self.get_argument('username', '').replace(' ','.').lower()
                # .ilike is for case insesitive.
                fuser = s.query(User).filter(User.username.ilike(username)).all()
                if not fuser:
                    self.write({'error': 'user does not exist'})
                else:
                    fuser = fuser[0]
                    if fuser.roles is None:
                        fuser.roles = ''
                    roles = fuser.roles.split(',')
                    roles.append('volunteer')
                    roles = set(roles)
                    fuser.roles = (',').join(roles)
                    addOrUpdate(fuser)
                    self.write({'response': 'success'})
            elif cmd == 'search' or cmd == 'viewPrintOut':
                # searcheth away!
                volunteers = s.query(Volunteer)
                if self.get_argument('campus_ministries', '') == 'on':
                    volunteers = volunteers.filter_by(campus_ministries=True)
                if self.get_argument('student_missions', '') == 'on':
                    volunteers = volunteers.filter_by(student_missions=True)
                if self.get_argument('aswwu', '') == 'on':
                    volunteers = volunteers.filter_by(aswwu=True)
                if self.get_argument('circle_church', '') == 'on':
                    volunteers = volunteers.filter_by(circle_church=True)
                if self.get_argument('university_church', '') == 'on':
                    volunteers = volunteers.filter_by(university_church=True)
                if self.get_argument('buddy_program', '') == 'on':
                    volunteers = volunteers.filter_by(buddy_program=True)
                if self.get_argument('assist', '') == 'on':
                    volunteers = volunteers.filter_by(assist=True)
                if self.get_argument('lead', '') == 'on':
                    volunteers = volunteers.filter_by(lead=True)
                if self.get_argument('audio_slash_visual', '') == 'on':
                    volunteers = volunteers.filter_by(audio_slash_visual=True)
                if self.get_argument('health_promotion', '') == 'on':
                    volunteers = volunteers.filter_by(health_promotion=True)
                if self.get_argument('construction_experience', '') == 'on':
                    volunteers = volunteers.filter_by(construction_experience=True)
                if self.get_argument('outdoor_slash_camping', '') == 'on':
                    volunteers = volunteers.filter_by(outdoor_slash_camping=True)
                if self.get_argument('concert_assistance', '') == 'on':
                    volunteers = volunteers.filter_by(concert_assistance=True)
                if self.get_argument('event_set_up', '') == 'on':
                    volunteers = volunteers.filter_by(event_set_up=True)
                if self.get_argument('children_ministries', '') == 'on':
                    volunteers = volunteers.filter_by(children_ministries=True)
                if self.get_argument('children_story', '') == 'on':
                    volunteers = volunteers.filter_by(children_story=True)
                if self.get_argument('art_poetry_slash_painting_slash_sculpting', '') == 'on':
                    volunteers = volunteers.filter_by(art_poetry_slash_painting_slash_sculpting=True)
                if self.get_argument('organizing_events', '') == 'on':
                    volunteers = volunteers.filter_by(organizing_events=True)
                if self.get_argument('organizing_worship_opportunities', '') == 'on':
                    volunteers = volunteers.filter_by(organizing_worship_opportunities=True)
                if self.get_argument('organizing_community_outreach', '') == 'on':
                    volunteers = volunteers.filter_by(organizing_community_outreach=True)
                if self.get_argument('bible_study', '') == 'on':
                    volunteers = volunteers.filter_by(bible_study=True)
                if self.get_argument('wycliffe_bible_translator_representative', '') == 'on':
                    volunteers = volunteers.filter_by(wycliffe_bible_translator_representative=True)
                if self.get_argument('food_preparation', '') == 'on':
                    volunteers = volunteers.filter_by(food_preparation=True)
                if self.get_argument('graphic_design', '') == 'on':
                    volunteers = volunteers.filter_by(graphic_design=True)
                if self.get_argument('poems_slash_spoken_word', '') == 'on':
                    volunteers = volunteers.filter_by(poems_slash_spoken_word=True)
                if self.get_argument('prayer_team_slash_prayer_house', '') == 'on':
                    volunteers = volunteers.filter_by(prayer_team_slash_prayer_house=True)
                if self.get_argument('dorm_encouragement_and_assisting_chaplains', '') == 'on':
                    volunteers = volunteers.filter_by(dorm_encouragement_and_assisting_chaplains=True)
                if self.get_argument('scripture_reading', '') == 'on':
                    volunteers = volunteers.filter_by(scripture_reading=True)
                if self.get_argument('speaking', '') == 'on':
                    volunteers = volunteers.filter_by(speaking=True)
                if self.get_argument('videography', '') == 'on':
                    volunteers = volunteers.filter_by(videography=True)
                if self.get_argument('drama', '') == 'on':
                    volunteers = volunteers.filter_by(drama=True)
                if self.get_argument('public_school_outreach', '') == 'on':
                    volunteers = volunteers.filter_by(public_school_outreach=True)
                if self.get_argument('retirement_slash_nursing_home_outreach', '') == 'on':
                    volunteers = volunteers.filter_by(retirement_slash_nursing_home_outreach=True)
                if self.get_argument('helping_the_homeless_slash_disadvantaged', '') == 'on':
                    volunteers = volunteers.filter_by(helping_the_homeless_slash_disadvantaged=True)
                if self.get_argument('working_with_youth', '') == 'on':
                    volunteers = volunteers.filter_by(working_with_youth=True)
                if self.get_argument('working_with_children', '') == 'on':
                    volunteers = volunteers.filter_by(working_with_children=True)
                if self.get_argument('greeting', '') == 'on':
                    volunteers = volunteers.filter_by(greeting=True)
                if self.get_argument('shofar_for_vespers', '') == 'on':
                    volunteers = volunteers.filter_by(shofar_for_vespers=True)
                if self.get_argument('music', '') != '':
                    volunteers = volunteers.filter(Volunteer.music.ilike('%'+str(self.get_argument('music',''))+'%'))
                if self.get_argument('join_small_groups', '') == 'on':
                    volunteers = volunteers.filter_by(join_small_groups=True)
                if self.get_argument('lead_small_groups', '') == 'on':
                    volunteers = volunteers.filter_by(lead_small_groups=True)
                if self.get_argument('can_transport_things', '') == 'on':
                    volunteers = volunteers.filter_by(can_transport_things=True)
                if self.get_argument('languages', '') != '':
                    volunteers = volunteers.filter(Volunteer.languages.ilike('%'+str(self.get_argument('languages',''))+'%'))
                if self.get_argument('berean_fellowship', '') != '':
                    volunteers = volunteers.filter_by(berean_fellowship=True)
                if self.get_argument('wants_to_be_involved', '') == 'on':
                    volunteers = volunteers.filter_by(wants_to_be_involved=True)

                #vusers = [{'profile': query_by_wwuid(Profile, v.wwuid)[0], 'volunteer_data': v} for v in volunteers]
                vusers = []
                for v in volunteers:
                    volResult = query_by_wwuid(Profile, v.wwuid)
                    if len(volResult) > 0:
                        vusers.append({'profile': volResult[0], 'volunteer_data': v})
                # should we return the results as JSON
                if cmd == 'search':
                    self.write({'results': [{'full_name': v['profile'].full_name, 'email': v['profile'].email, 'photo': v['profile'].photo, 'username': v['profile'].username} for v in vusers]})
                # or as a full fledged webpage
                else:
                    logger.debug(user)
                    self.write('<table border="1"><tr><th>Photo</th><th>Name</th><th>Class Standing</th><th>Major(s)</th><th>Email</th><th>Phone</th><th>Volunteer Data</th></tr>')
                    for v in vusers:
                        self.write('<tr><td>'+('<img src="https://aswwu.com/media/img-xs/'+str(v['profile'].photo)+'">' if str(v['profile'].photo).find(str(v['profile'].wwuid)) > -1 else '')+'</td>'\
                                    '<td>'+str(v['profile'].full_name)+'</td>''<td>'+str(v['profile'].class_standing)+'</td><td>'+str(v['profile'].majors)+'</td>'\
                                    '<td>'+str(v['profile'].email)+'</td>''<td>'+str(v['profile'].phone)+'</td><td>'+str(v['volunteer_data'].only_true())+'</td></tr>')
                    self.write('</table>')

# get all of the profiles in our database
class AllElectionVoteHandler(BaseHandler):
    def get(self):
        votes = query_all_Election(Election)
        self.write({'results': [v.info() for v in votes]})

# update user's vote
class ElectionVoteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, username):
        self.write({"error": "Elections are now closed."})
        # user = self.current_user
        # if user.username == username or 'administrator' in user.roles:
        #     usrvote = query_by_wwuid_Election(Election, str(user.wwuid))
        #     # Fix this to be more efficient
        #     if len(usrvote) == 0:
        #         new_vote = Election(wwuid=str(user.wwuid))
        #         vote = addOrUpdateElection(new_vote)
        #     else:
        #         vote = election_s.query(Election).filter_by(wwuid=str(user.wwuid)).one()
        #     vote.candidate_one = self.get_argument('candidate_one','')
        #     vote.candidate_two = self.get_argument('candidate_two','')
        #     vote.sm_one = self.get_argument('sm_one','')
        #     vote.sm_two = self.get_argument('sm_two','')
        #     vote.new_department = self.get_argument('new_department','')
        #     vote.district = self.get_argument('district', '')
        #
        #     addOrUpdateElection(vote)
        #
        #     self.write({'vote': 'successfully voted'})
        # else:
        #     self.write({'error': 'invalid voting permissions'})

class ElectionLiveFeedHandler(BaseHandler):
    def get(self):
        votes=query_all_Election(Election)
        self.write({'size': len(votes)})

class SamlHandler(BaseHandler):
    def post(self):
        try:
            secret_key = self.get_argument('secret_key', None)
            if(secret_key == keys["samlEndpointKey"]):
                employee_id = self.get_argument('employee_id', None)
                full_name = self.get_argument('full_name', None)
                email_address = self.get_argument('email_address', None)
                if employee_id:
                    user = query_user(employee_id)
                    if not user:
                        user = User(wwuid=employee_id, username=email_address.split('@',1)[0], full_name=full_name, status='Student')
                        addOrUpdate(user)
                    self.write({'status':'success'})
                else:
                    logger.info("AccountHandler: error")
                    self.write({'error':'invalid parameters'})
            else:
                logger.info("Unauthorized Access Attempted")
                self.write({'error':'Unauthorized Access Attempted'})
        except Exception as e:
            logger.error("LoginHandler: error"+str(e.message))
            self.write({'error': str(e.message)})
    def get(self):
        self.write({'error':'You really should not be here'})

class PagesHandler(BaseHandler):
    def get(self):
        page_id = '12345'
        page = None
        try:
            page = query_by_page_id(Page, page_id)
            if len(page) == 0:
                self.write({'error': 'no page found'})
            elif len(page) > 1:
                self.write({'error': 'too many pages found'})
            else:
                 logger.info(page[0].serialize())
                 self.write(page[0].serialize())
        except Exception as e:
            logger.error("PagesHandler: error.\n" + str(e.message))
            self.write({'error': str(e.message)})


class PagesUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, page_id):
        try:
            user = self.current_user
            page = query_by_page_id(Page, page_id)
            editors = []
            for dict in page[0].serialize()['editors']:
                temp = dict['name']
                editors.append(temp)
            print(editors)
            if(user.username in editors or user.username == page.author):
                if not len(page):
                    page = [Page()]
                elif len(page) > 1:
                    raise ValueError('Too many pages found')
                else:
                    page[0].url = bleach.clean(self.get_argument('url'))
                    page[0].title = bleach.clean(self.get_argument('title'))
                    page[0].content = bleach.clean(self.get_argument('content'))
                    page[0].author = bleach.clean(self.get_argument('author'))
                    page[0].editors = bleach.clean(self.get_argument('editors'))
                    page[0].is_visible = bleach.clean(self.get_argument('is_visible'))
                    page[0].tags = bleach.clean(self.get_argument('tags'))
                    page[0].category = bleach.clean(self.get_argument('category'))
                    page[0].theme_blob = bleach.clean(self.get_argument('theme_blob'))
                    addOrUpdatePage(page[0])

        except Exception as e:
            logger.error("PagesUpdateHandler: error.\n" + str(e.message))

class NewFormHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            if('forms' in user.roles):
                form = JobForm()
                form.job_name = bleach.clean(self.get_argument('job_name'))
                form.job_description = bleach.clean(self.get_argument('job_description'))
                form.visibility = bleach.clean(self.get_argument('visibility'))
                form.owner = bleach.clean(self.get_argument('owner'))
                form.image = bleach.clean(self.get_argument('image'))
                addOrUpdateForm(form)
                form = jobs_s.query(JobForm).filter_by(job_name=str(form.job_name)).one()
                questions = self.get_argument('questions')
                for q in questions:
                    question = JobQuestion()
                    question.question = q.question
                    question.jobID = form.id
                    addOrUpdate(question)
                self.set_status(401)
                self.write({"status": "submitted"})
        except Exception as e:
            logger.error("NewFormHandler: error.\n" + str(e.message))


class ViewFormHandler(BaseHandler):
    def get(self, jobID):
        try:
            if(jobID.jobID == "all"):
                forms = query_all_Forms(JobForm)
                self.write({'forms': [f.min() for f in forms]})
            else:
                form = jobs_s.query(JobForm).filter_by(id=str(jobID.jobID)).one()
                self.write({'form': form.serialize()})
        except Exception as e:
            logger.error("ViewFormHandler: error.\n" + str(e.message))


class SubmitApplicationHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, form_json):
        self.write({"status": "submitted"})


class UpdateApplicationHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, form_json):
        self.write("")


class ViewApplicationHandler(BaseHandler):
    def get(self, jobID, username):
        self.write("")


class ApplicationStatusHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, status_json):
        self.write("")


# This is the instagram handler for the atlas (I did this to hide the access token).
class FeedHandler(BaseHandler):
    def get(self):
        name = self.get_argument('name','')
        if(name == "atlas"):
            with open("/var/www/atlas/access.token", 'r') as f:
                token = f.read()
                f.close()
                token = token.rstrip('\n')
                # TODO: Make this asynchronous and move access.token to aswwu/databases git repo
                http_client = HTTPClient()
                try:
                    response = http_client.fetch("https://api.instagram.com/v1/users/self/media/recent/?access_token=" + token)
                    self.write(response.body)
                except Exception as e:
                    self.write("{error: '" + str(e) + "'}")
                http_client.close()
        elif(name == "issuu"):
            http_client = HTTPClient()
            try:
                response = http_client.fetch("http://search.issuu.com/api/2_0/document?username=aswwucollegian&pageSize=1&responseParams=title,description&sortBy=epoch")
                self.write(response.body)
            except Exception as e:
                self.write("{error: '" + str(e) + "'}")
            http_client.close()
        else:
            self.write("Something went wrong.")


class MatcherHandler(BaseHandler):
    def get(self):
        user = self.current_user

        if hasattr(user, "username"):
            profiles = query_all(Profile)
            self.write({'database': [p.view_other() for p in profiles]})
        else:
            self.write("{'error': 'Insufficient Permissions :('}")
