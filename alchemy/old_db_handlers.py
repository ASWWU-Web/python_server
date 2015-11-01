import logging
from alchemy.base_handlers import BaseHandler
from alchemy.setup import *

logger = logging.getLogger("aswwu")

class LookUpOldHandler(BaseHandler):
    def get(self, table):
        things = query_old_all(table)
        for thing in things:
            self.write(str(thing.id))

    def post(self):
        users = query_old_all('users')
        profiles = query_old_all('profiles')
        volunteers = query_old_all('volunteers')

        for u in users:
            new_user = User(wwuid=u.wwuid, username=u.username, full_name=u.fullname, status=u.status, roles=u.roles)
            addOrUpdate(new_user)

        for p in profiles:
            new_profile = Profile(
                wwuid=p.wwuid,
                username=p.username,
                full_name=p.fullname,
                photo=p.photo,
                gender=p.gender,
                birthday=p.birthday,
                email=p.email,
                phone=p.phone,
                website=p.website,
                majors=p.majors,
                minors=p.minors,
                graduate=p.graduate,
                preprofessional=p.preprofessional,
                class_standing=p.class_standing,
                high_school=p.high_school,
                class_of=p.class_of,
                relationship_status=p.relationship_status,
                attached_to=p.attached_to,
                quote=p.quote,
                quote_author=p.quote_author,
                hobbies=p.hobbies,
                career_goals=p.career_goals,
                favorite_books=p.favorite_books,
                favorite_food=p.favorite_food,
                favorite_movies=p.favorite_movies,
                favorite_music=p.favorite_music,
                pet_peeves=p.pet_peeves,
                personality=p.personality,
                views=p.views,
                privacy=p.privacy,
                department=p.department,
                office=p.office,
                office_hours=p.office_hours
            )
            addOrUpdate(new_profile)

        for v in volunteers:
            new_volunteer = Volunteer(
                wwuid=v.wwuid,
                campus_ministries=v.campus_ministries,
                student_missions=v.student_missions,
                aswwu=v.aswwu,
                circle_church=v.circle_church,
                university_church=v.university_church,
                assist=v.assist,
                lead=v.lead,
                audio_slash_visual=v.audio_slash_visual,
                health_promotion=v.health_promotion,
                construction_experience=v.construction_experience,
                outdoor_slash_camping=v.outdoor_slash_camping,
                concert_assistance=v.concert_assistance,
                event_set_up=v.event_set_up,
                children_ministries=v.children_ministries,
                children_story=v.children_story,
                art_poetry_slash_painting_slash_sculpting=v.art_poetry_slash_painting_slash_sculpting,
                organizing_events=v.organizing_events,
                organizing_worship_opportunities=v.organizing_worship_opportunities,
                organizing_community_outreach=v.organizing_community_outreach,
                bible_study=v.bible_study,
                wycliffe_bible_translator_representative=v.wycliffe_bible_translator_representative,
                food_preparation=v.food_preparation,
                graphic_design=v.graphic_design,
                poems_slash_spoken_word=v.poems_slash_spoken_word,
                prayer_team_slash_prayer_house=v.prayer_team_slash_prayer_house,
                dorm_encouragement_and_assisting_chaplains=v.dorm_encouragement_and_assisting_chaplains,
                scripture_reading=v.scripture_reading,
                speaking=v.speaking,
                videography=v.videography,
                drama=v.drama,
                public_school_outreach=v.public_school_outreach,
                retirement_slash_nursing_home_outreach=v.retirement_slash_nursing_home_outreach,
                helping_the_homeless_slash_disadvantaged=v.helping_the_homeless_slash_disadvantaged,
                working_with_youth=v.working_with_youth,
                working_with_children=v.working_with_children,
                greeting=v.greeting,
                shofar_for_vespers=v.shofar_for_vespers,
                music=v.music,
                join_small_groups=v.join_small_groups,
                lead_small_groups=v.lead_small_groups,
                can_transport_things=v.can_transport_things,
                languages=v.languages,
                wants_to_be_involved=v.wants_to_be_involved
            )
            addOrUpdate(new_volunteer)
