import requests
from settings import keys, testing

POSITION_URL = testing['base_url'] + ':' + str(testing['port']) + '/' + 'elections/position'


def get_position(position=None, election_type=None, active=None):
    optional_parameters = {
        'position': position,
        'election_type': election_type,
        'active': active
    }
    resp = requests.get(POSITION_URL, optional_parameters)
    return resp


def post_position(session, position=None, election_type=None, active=None, order=None, obj_data=None):
    if obj_data:
        post_data = obj_data
        post_data['active'] = obj_data['active'] == 'True'
        post_data['order'] = int(obj_data['order'])
    else:
        post_data = {
          'position': position,
          'election_type': election_type,
          'active': active == 'True',
          'order': int(order)
        }
    resp = session.post(POSITION_URL, json=post_data)
    return resp


def get_specified_position(position_id):
    url = POSITION_URL + '/' + position_id
    resp = requests.get(url)
    return resp


def put_specified_position(session, position_id, position=None, election_type=None, active=None, order=None, obj_data=None):
    url = POSITION_URL + '/' + position_id
    if obj_data:
        put_data = obj_data
    else:
        put_data = {
            'id': position_id,
            'position': position,
            'election_type': election_type,
            'active': str(active) == 'True',
            'order': int(order)
        }
    resp = session.put(url, json=put_data)
    return resp
