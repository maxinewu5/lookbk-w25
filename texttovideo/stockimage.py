import requests
import urllib.parse

API_KEY = 'u_dy0cvol704'

text= 'red roses'

URL = f"https://pixabay.com/api/?key={API_KEY}&q={urllib.parse.quote(text)}"
# must credit pixabay for these images IMPORTANT

response = requests.get(URL)
if response.status_code == 200:
    data = response.json()
    if data.get('totalHits', 0) > 0:
        for hit in data.get('hits', []):
            print(hit.get('pageURL'))
    else:
        print('No hits')
else:
    print('Error:', response.status_code)
