import requests
import json
from tests.conftest import testing_server


def test_search_all(testing_server):
    expected_data = {
        "results": []
    }

    url = 'http://127.0.0.1:8888/search/all'
    resp = requests.get(url)

    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)
