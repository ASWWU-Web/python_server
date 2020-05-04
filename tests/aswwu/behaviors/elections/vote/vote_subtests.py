def send_post_vote():
    pass
    # votes = load_csv(VOTES_PATH)


def assert_vote_data(resp, vote):
    assert (resp['election'] == vote['election'])
    assert (resp['position'] == vote['position'])
    assert (resp['vote'] == vote['vote'])