import requests

url = "http://127.0.0.1:8000/csirts/"

data = {
    "name": "peter",
    "location": "gisozi",
    "contacts": "peter@gmail.com"
}

response = requests.post(url, json=data)
print(response.status_code)  # Should print 200 if successful
print(response.json())       # Should print the created CSIRT object
