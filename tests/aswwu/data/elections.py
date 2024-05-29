_elections = [
    ["aswwu", "Primary", "2", "2028-02-13 12:43:20.000000", "2028-02-13 17:51:20.000000", "2028-02-13 17:51:20.000000"],
    ["aswwu", "General Election 2026", "1", "2026-02-15 08:00:00.000000", "2026-02-15 20:00:00.000000", "2026-02-15 20:00:00.000000"],
    ["senate", "Senate Election 2025", "2", "2025-10-13 12:43:20.000000", "2025-10-13 17:51:20.000000", "2025-10-13 17:51:20.000000"],
    ["senate", "Senate Election 2024", "2", "2024-02-13 12:43:20.000000", "2024-02-13 17:51:20.000000", "2024-02-14 17:51:20.000000"],
    ["senate", "Senate Election 2022", "2", "2022-02-13 12:43:20.000000", "2022-02-13 17:51:20.000000", "2022-02-15 17:51:20.000000"],
    ["aswwu", "ASWWU Election 2027", "2", "2027-06-13 12:43:20.000000", "2027-06-13 17:51:20.000000", "2027-06-12 17:51:20.200000"],
]

ELECTIONS = [
    {
        "election_type": election[0],
        "name": election[1],
        "max_votes": election[2],
        "start": election[3],
        "end": election[4],
        "show_results": election[5],
    }
    for election in _elections
]

POST_ELECTIONS_USER = {
    'wwuid': '1234567',
    'full_name': 'John McJohn',
    'email': 'john.mcjohn@wallawalla.edu',
    'username': 'john.mcjohn',
    'roles': ['elections-admin']
}

ELECTION_INFO = {
    'election_type': 'aswwu',
    'election_name': 'Test Election'
}

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'