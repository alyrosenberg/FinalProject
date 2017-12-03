import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline
plt.rcParams['figure.figsize'] = (15,9)
import json
import sqlite3
import pprint
import requests
import facebook
import datetime

#creating a cache
CACHE_FNAME = "206_finalproject.json"
try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}


#general function to put each API into
def performsearch(search_term, api_query_function):
    cachekey = api_query_function.__name__ + "_" + search_term
    if cachekey in CACHE_DICTION:
        toreturn = CACHE_DICTION[cachekey]
    else:
        toreturn = api_query_function(search_term)
        CACHE_DICTION[cachekey] = toreturn
        writefile = open(CACHE_FNAME,"w")
        writefile.write(json.dumps(CACHE_DICTION))
        writefile.close()
    return toreturn



#instagram
print ('API #1: Instagram\n')

instagram_access_token = "226042116.1677ed0.d72827a090bd4641a961139b7f04530b"

def query_instagram_directly(search_term):
    url = 'https://api.instagram.com/v1/users/self/media/recent/?access_token={}'.format(instagram_access_token)
    #response_string = requests.get(url).text
    requests.get(base_url, params = {'apikey': info.IMDBapi_key, 't':title, 'season': '1'})
    posts = json.loads(response_string)['data']
    #user_id = posts[0]['user']['id']
    return posts

def query_instagram():
    return performsearch("blah", query_instagram_directly)

x = query_instagram()
pprint.pprint(x)

#SQL table for instagram
cur.execute('DROP TABLE IF EXISTS Instagram_Posts')
cur.execute('CREATE TABLE Instagram_Posts(id TEXT PRIMARY KEY, created_at TIMESTAMP, caption_text TEXT, likes INTEGER, lat INTEGER, lng INTEGER)')

Instagram_Posts = query_instagram()
for post in Instagram_Posts:
    print (post['id'])
    print (post['created_time'])
    print (post['caption']['text'])
    print (post["likes"]['count'])
    #print (post["location"]['latitude'])
    try:
        lattemp = post["location"]['latitude']
        lngtemp = post["location"]['longitude']
    except:
        lattemp = ""
        lngtemp = ""
    if lattemp == None:
        lattemp = ""
    if lngtemp == None:
        lngtemp = ""
    formatteddatetime = datetime.date.fromtimestamp( int(post['created_time']) ).strftime('%Y-%m-%d %H:%M:%S')
    print (post['id'], formatteddatetime, post['caption']['text'], post["likes"]['count'], post["location"]['latitude'], post["location"]['longitude'])
    cur.execute('INSERT INTO Instagram_Posts(id, created_at, caption_text, likes, lat, lng) VALUES (?, ?, ?, ?, ?, ?)', (post['id'], formatteddatetime, post['caption']['text'], post["likes"]['count'], lattemp, lngtemp))
    
conn.commit()


#github
print ('\n------------------------------------\n')
print ('API #2: GitHub\n')
def query_github_directly(github_user_id = "alyrosenberg"):
    url = 'https://api.github.com/users/{}/events'.format(github_user_id)
    response_string = requests.get(url).text
    github_events = json.loads(response_string)
    return github_events

def query_github(github_user_id = "alyrosenberg"):
    return performsearch(github_user_id, query_github_directly)

#create connection to local SQLite database for github
conn = sqlite3.connect('206_finalproject.sqlite')
cur = conn.cursor()

#Dropping github table if it exists then initilizing github table
cur.execute('DROP TABLE IF EXISTS GitHub_Events')
cur.execute('CREATE TABLE GitHub_Events(id INTEGER PRIMARY KEY, created_at TIMESTAMP, type TEXT, repo_name TEXT)')

GitHub_Events = query_github()
for event in GitHub_Events:
    cur.execute('INSERT INTO GitHub_Events(id, created_at, type, repo_name) VALUES (?, ?, ?, ?)', 
                (event['id'], event['created_at'], event['type'], event["repo"]['name']))

conn.commit()

#API 3 is OMDB

print ('\n------------------------------------\n')
print ('API #3: OMDB\n')

movie_title = input("Enter your movie title: ")
def query_OMDB_directly():
    base_url = "http://www.omdbapi.com/?"
    params_dict = {}
    params_dict['t'] = movie_title
    params_dict['apikey'] = "3a894ff0"
    r = requests.get(base_url, params=params_dict)
    responses = r.text
    final = json.loads(responses)
    print(final)

hi = query_OMDB_directly()

#create SQL table from OMDB

#fix this to be for movie
def query_OMDB(movie_title):
    return performsearch(movie_title, query_OMDB_directly)

cur.execute('DROP TABLE IF EXISTS OMDB_Movie')
cur.execute('CREATE TABLE OMDB_Movie (title TEXT PRIMARY KEY, year INTEGER, genre TEXT, director TEXT, imdbrating REAL)')

OMBD_Movie = query_OMDB(movie_title)
for movie in OMDB_Movie:
    cur.execute('INSERT INTO OMDB_Movie(title, year, genre, director, imdbrating) VALUES (?, ?, ?, ?,?)', 
                (movie['Title'], movie['Year'], movie['Genre'], movie["Director"], movie['imdbRating']))

conn.commit()


#API 4 google maps
print ('\n------------------------------------\n')
print ('API #4: Google Maps\n')

origin = input("Enter your starting address: ")
destination = input("Enter your destination address: ")

def query_googlemaps_directly():
    base_url = "https://maps.googleapis.com/maps/api/directions/json?"
    params_dict = {}
    params_dict['origin'] = origin
    params_dict['key'] = "AIzaSyCTFY6AuSgxOcKsajYe7KFM6CIw20h-5Gc"
    params_dict['destination'] = destination
    r = requests.get(base_url, params=params_dict)
    responses = r.text
    final = json.loads(responses)
    #distance = final['routes'][0]['legs'][0]['distance']['text']
    #duration = final['routes'][0]['legs'][0]['duration']['text']
    #print(distance)
    #print(duration)
    #pprint.pprint(final)
    
hi = query_googlemaps_directly()

#this is my table for Google Maps API

#fix this for maps
def query_GoogleMaps(movie_title):
    return performsearch(movie_title, query_OMDB_directly)

cur.execute('DROP TABLE IF EXISTS GoogleMaps')
cur.execute('CREATE TABLE GoogleMaps (distance TEXT , duration TEXT)')

GoogleMaps = query_GoogleMaps()
for trip in GoogleMaps:
    cur.execute('INSERT INTO GoogleMaps(distance, duration) VALUES (?, ?)', 
                (final['routes'][0]['legs'][0]['distance']['text'], final['routes'][0]['legs'][0]['duration']['text']))

conn.commit()

#API 4 iTunes
print ('\n------------------------------------\n')
print ('API #4: iTunes\n')

term = input("Enter your artist: ")

def query_itunes_directly():
    base_url = "https://itunes.apple.com/search?"
    params_dict = {}
    params_dict['term'] = term
    params_dict['country'] = "US"
    r = requests.get(base_url, params=params_dict)
    responses = r.text
    final = json.loads(responses)
    pprint.pprint(final)
    
hi = query_itunes_directly()

#SQL table for itunes API
#change values
cur.execute('DROP TABLE IF EXISTS iTunes')
cur.execute('CREATE TABLE iTunes(distance TEXT , duration TEXT)')


itunes = query_itunes()
for search in itunes:
    cur.execute('INSERT INTO itunes(distance, duration) VALUES (?, ?)', 
                (final['routes'][0]['legs'][0]['distance']['text'], final['routes'][0]['legs'][0]['duration']['text']))

conn.commit()

#Here I will create the visuals

#Visual 1:

#Visual 2:

#Visual 3: