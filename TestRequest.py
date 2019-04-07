import httplib2
h = httplib2.Http()
response, content = h.request("http://127.0.0.1:8888/verify/", "GET")
print("HTTP GET request")
print("Reponse:", response, "\nContent:", content, "\nCookie:", response['set-cookie'])

## Resending the request with cookie with headers
headers = {"Cookie":response['set-cookie']}
response_2, content_2 = h.request("http://127.0.0.1:8888/user/", "GET", headers = headers)
print("\nResending the request with cookie in headers")
print("Reponse:", response_2, "\nContent:", content_2)
