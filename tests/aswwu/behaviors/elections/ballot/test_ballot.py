import tests.aswwu.behaviors.elections.ballot.ballot_utils as ballot_utils
import tests.aswwu.behaviors.elections.ballot.ballot_requests as ballot_requests
import tests.aswwu.behaviors.elections.election.election_utils as election_utils
import tests.aswwu.behaviors.elections.position.position_utils as position_utils
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
from tests.aswwu.data.elections import ELECTION_INFO
from tests.aswwu.data.positions import ASWWU_POSITIONS
import tests.utils as utils
import json
import time
from tests.conftest import testing_server
import pytest


pytestmark = pytest.mark.skip("code paths have been deprecated")


def test_post_ballot(testing_server):
    # create admin session
    user_data, admin_session = election_utils.create_elections_admin()
    admin_user_data = user_data['user']

    # create dynamic election
    election = election_utils.assert_post_dynamic_election(session=admin_session,
                                                              election_type=ELECTION_INFO['election_type'],
                                                              election_name=ELECTION_INFO['election_name'])

    # create generic position
    position_resp = position_requests.post_position(admin_session, 'President', 'aswwu', 'True', '1')
    position = json.loads(position_resp.text)

    # wait for election to open
    time.sleep(2)

    # assert post positions
    ballot_utils.assert_create_ballots(admin_session, admin_user_data, election, [position])


def test_get_ballot(testing_server):
    # create admin session
    user_data, admin_session = election_utils.create_elections_admin()
    admin_user_data = user_data['user']

    # create dynamic election
    election = election_utils.assert_post_dynamic_election(session=admin_session,
                                                              election_type=ELECTION_INFO['election_type'],
                                                              election_name=ELECTION_INFO['election_name'])
    election_id = election['id']

    # create generic position
    position_resp = position_requests.post_position(admin_session, 'President', 'aswwu', 'True', '1')
    position = json.loads(position_resp.text)

    # wait for election to open
    time.sleep(2)

    # dictionary to store data from post request
    ballot_data = ballot_utils.assert_create_ballots(admin_session, admin_user_data, election, [position])

    # get ballots
    ballot_get_resp = ballot_requests.get_ballot(admin_session, election_id)
    assert (ballot_get_resp.status_code == 200)
    ballot_get_resp_data = json.loads(ballot_get_resp.text)['ballots']

    for ballot in ballot_get_resp_data:
        utils.assert_is_equal_sub_dict(ballot_data[ballot['id']], ballot)


def test_get_specified_ballot(testing_server):
    # create admin session
    user_data, admin_session = election_utils.create_elections_admin()
    admin_user_data = user_data['user']

    # create dynamic election
    election = election_utils.assert_post_dynamic_election(session=admin_session,
                                                              election_type=ELECTION_INFO['election_type'],
                                                              election_name=ELECTION_INFO['election_name'])
    election_id = election['id']

    # create generic position
    position_resp = position_requests.post_position(admin_session, 'President', 'aswwu', 'True', '1')
    position = json.loads(position_resp.text)

    # wait for election to open
    time.sleep(2)

    # create posts
    ballot_data = ballot_utils.assert_create_ballots(admin_session, admin_user_data, election, [position])

    # verify specified ballot matches ballot data
    for ballot_id, ballot in ballot_data.items():
        spec_get_resp = ballot_requests.get_specified_ballot(admin_session, election_id, ballot_id)
        assert (spec_get_resp.status_code == 200)
        spec_get_resp_data = json.loads(spec_get_resp.text)
        utils.assert_is_equal_sub_dict(ballot, spec_get_resp_data)


def test_delete_specified_ballot(testing_server):
    # create admin session
    user_data, admin_session = election_utils.create_elections_admin()
    admin_user_data = user_data['user']

    # create dynamic election
    election = election_utils.assert_post_dynamic_election(session=admin_session,
                                                              election_type=ELECTION_INFO['election_type'],
                                                              election_name=ELECTION_INFO['election_name'])
    election_id = election['id']

    # create generic position
    positions = position_utils.assert_create_positions(admin_session, ASWWU_POSITIONS)

    # wait for election to open
    time.sleep(2)

    # create ballots
    ballot_data = ballot_utils.assert_create_ballots(admin_session, admin_user_data, election, positions)

    # delete specified ballots
    for ballot_id, ballot in ballot_data.items():
        delete_resp = ballot_requests.delete_specified_ballot(admin_session, election_id, ballot_id)
        assert (delete_resp.status_code == 204)

        # verify specified ballot doesn't exist
        spec_get_resp = ballot_requests.get_specified_ballot(admin_session, election_id, ballot_id)
        assert (spec_get_resp.status_code == 404)
