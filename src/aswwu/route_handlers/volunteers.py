import json
import logging

import tornado.web

from src.aswwu.base_handlers import BaseHandler
import src.aswwu.models.mask as mask_model
import src.aswwu.models.volunteers as volunteer_model
import src.aswwu.alchemy as alchemy

logger = logging.getLogger("aswwu")


# fairly straightforward handler to save a TON of volunteer information
class VolunteerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, wwuid):
        user = self.current_user
        if user.wwuid == wwuid or 'volunteer' in user.roles:
            volunteer = alchemy.query_by_wwuid(volunteer_model.Volunteer, wwuid)
            if len(volunteer) == 0:
                volunteer = volunteer_model.Volunteer(wwuid=user.wwuid)
                volunteer = alchemy.add_or_update(volunteer)
            else:
                volunteer = volunteer[0]
            self.write(volunteer.to_json())
        else:
            self.write({'error': 'insufficient permissions'})

    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        volunteer = alchemy.query_by_wwuid(volunteer_model.Volunteer, user.wwuid)[0]
        for role in self.request.arguments:
            if hasattr(volunteer, role):
                volunteer.setattr(role, self.get_argument(role, '') == '1')
        logger.debug(volunteer.only_true())
        alchemy.add_or_update(volunteer)
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
                username = self.get_argument('username', '').replace(' ', '.').lower()
                # .ilike is for case insesitive.
                fuser = alchemy.people_db.query(mask_model.User).filter(mask_model.User.username.ilike(username)).all()
                if not fuser:
                    self.write({'error': 'user does not exist'})
                else:
                    fuser = fuser[0]
                    if fuser.roles is None:
                        fuser.roles = ''
                    roles = fuser.roles.split(',')
                    roles.append('volunteer')
                    roles = set(roles)
                    fuser.roles = ','.join(roles)
                    alchemy.add_or_update(fuser)
                    self.write({'response': 'success'})
            elif cmd == 'search' or cmd == 'viewPrintOut':
                # searcheth away!
                volunteers = alchemy.people_db.query(volunteer_model.Volunteer)
                args = {}
                for role in self.request.arguments:
                    if hasattr(volunteer_model.Volunteer, role) and\
                            self.get_argument(role, '') != '' and\
                            role not in ['music', 'languages']:
                        args[role] = True
                volunteers = volunteers.filter_by(**args)
                if self.get_argument('music', '') != '':
                    volunteers = volunteers.filter(
                        volunteer_model.Volunteer.music.ilike('%'+str(self.get_argument('music', ''))+'%')
                    )
                if self.get_argument('languages', '') != '':
                    volunteers = volunteers.filter(
                        volunteer_model.Volunteer.languages.ilike('%'+str(self.get_argument('languages', ''))+'%')
                    )

                # vusers = [{'profile': query_by_wwuid(Profile, v.wwuid)[0], 'volunteer_data': v} for v in volunteers]
                vusers = []
                for v in volunteers:
                    vol_result = alchemy.query_by_wwuid(mask_model.Profile, v.wwuid)
                    if len(vol_result) > 0:
                        vusers.append({'profile': vol_result[0], 'volunteer_data': v})
                # should we return the results as JSON
                if cmd == 'search':
                    self.write({'results': [{'full_name': v['profile'].full_name, 'email': v['profile'].email,
                                             'photo': v['profile'].photo,
                                             'username': v['profile'].username} for v in vusers]})
                # or as a full fledged webpage
                else:
                    logger.debug(user)
                    self.write('<table border="1"><tr>'
                               '<th>Photo</th><th>Name</th>'
                               '<th>Class Standing</th><th>Major(s)</th>'
                               '<th>Email</th><th>Phone</th>'
                               '<th>Volunteer Data</th></tr>')
                    for v in vusers:
                        self.write('<tr><td>' + ('<img src="https://aswwu.com/media/img-xs/'
                                                 + str(v['profile'].photo)+'">'
                                                 if str(v['profile'].photo).find(str(v['profile'].wwuid)) > -1 else '')
                                   + '</td><td>' + str(v['profile'].full_name) + '</td>''<td>'
                                   + str(v['profile'].class_standing) + '</td><td>' + str(v['profile'].majors)
                                   + '</td><td>' + str(v['profile'].email) + '</td>''<td>' + str(v['profile'].phone)
                                   + '</td><td>' + str(v['volunteer_data'].only_true()) + '</td></tr>')
                    self.write('</table>')
