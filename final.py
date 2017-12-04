import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline
plt.rcParams['figure.figsize'] = (15,9)
import json
import sqlite3
import pprint
import requests
import datetime
import sys


def skip_lines(num_lines):
   for i in range(num_lines):
       print("\n")

def printsequence(x, skiplines=2):
   print(x)
   skip_lines(skiplines)
   sys.stdout.flush()


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
        print ("loading from cache")
        toreturn = CACHE_DICTION[cachekey]
    else:
        toreturn = api_query_function(search_term)
        CACHE_DICTION[cachekey] = toreturn
        writefile = open(CACHE_FNAME,"w")
        writefile.write(json.dumps(CACHE_DICTION))
        writefile.close()
    return toreturn

#create connection to local SQLite database
conn = sqlite3.connect('206_finalproject.sqlite')
cur = conn.cursor()

def prep(value, typestring):
	if typestring == "str":
		if value == None:
			return "_"
        else:
            return str(value)
    if typestring == "int":
        if value == None:
            return "_"
        else:
            return int(value)

#instagram
print ('API #1: Instagram\n')

instagram_access_token = "226042116.1677ed0.d72827a090bd4641a961139b7f04530b"

def query_instagram_directly(search_term):
    posts = []
    baseurl = 'https://api.instagram.com/v1/users/self/media/recent/'
    payload = {'access_token' : instagram_access_token, 'count': 101}
    #response_string = requests.get(url).text
    r = requests.get(baseurl, params = payload)
    posttemp = r.json()['data']
    posts = posts + posttemp
    payload['max_id'] = r.json()['pagination']['next_max_id']
    r = requests.get(baseurl, params = payload)
    posttemp = r.json()['data']
    posts = posts + posttemp
    payload['max_id'] = r.json()['pagination']['next_max_id']
    r = requests.get(baseurl, params = payload)
    posttemp = r.json()['data']
    posts = posts + posttemp
    payload['max_id'] = r.json()['pagination']['next_max_id']
    r = requests.get(baseurl, params = payload)
    posttemp = r.json()['data']
    posts = posts + posttemp
    #user_id = posts[0]['user']['id']
    return posts

def query_instagram():
    return performsearch("blah", query_instagram_directly)

x = query_instagram()
printsequence(len(x))


#SQL table for instagram
#Dropping Tweets table if it exists then initilizing Tweets table
cur.execute('DROP TABLE IF EXISTS Instagram_Posts')
cur.execute('CREATE TABLE Instagram_Posts(id TEXT PRIMARY KEY, created_at TIMESTAMP, caption_text TEXT, likes INTEGER, lat INTEGER, lng INTEGER)')

Instagram_Posts = query_instagram()
for post in Instagram_Posts:
    if post == None:
        continue    
    currentid = post["id"]
    created_time = post["created_time"]
    caption = post["caption"]
    caption_text = ""
    if caption != None:
        caption_text = caption["text"]
    likes = post["likes"]
    numlikes = 0
    if likes != None:
        numlikes = likes["count"]
    lat = 0
    long = 0
    location = post['location']
    if location != None:
        lat = location['latitude']
        long = location['longitude']
    formatteddatetime = datetime.date.fromtimestamp( int(post['created_time']) ).strftime('%Y-%m-%d %H:%M:%S')
   # print (post['id'], formatteddatetime, post['caption']['text'], post["likes"]['count'], post["location"]['latitude'], post["location"]['longitude'])
    cur.execute('INSERT INTO Instagram_Posts(id, created_at, caption_text, likes, lat, lng) VALUES (?, ?, ?, ?, ?, ?)', 
                (currentid, formatteddatetime, caption_text, numlikes, lat, long))
    
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

#OMDB API

#mykey = 3a894ff0

list_movies = ['Mean Girls','Wonder Woman', 'Get Out', 'Star Wars', 'The Big Sick', 'Lady Bird', 'La La Land', 'It', 'Titanic', 'The Notebook', 'Love Actually']
def query_OMDB_directly(movie_title):
    base_url = "http://www.omdbapi.com/?"
    params_dict = {}
    params_dict['t'] = movie_title
    params_dict['apikey'] = "3a894ff0"
    r = requests.get(base_url, params=params_dict)
    responses = r.text
    final = json.loads(responses)
    printsequence(final)

hi = query_OMDB_directly("star wars")

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


#API 4 iTunes
print ('\n------------------------------------\n')
print ('API #4: iTunes\n')

def query_itunes_directly(search_term):
    base_url = "https://itunes.apple.com/search?"
    params_dict = {}
    params_dict['term'] = search_term
    params_dict['country'] = "US"
    params_dict['media'] = "music"
    params_dict['entity'] = "song"
    r = requests.get(base_url, params=params_dict)
    responses = r.text
    final = json.loads(responses)
    return (final['results'])
    
def query_itunes(search_term):
    return performsearch(search_term, query_itunes_directly)

hi = query_itunes("Beyonce")
printsequence ("aly")

#this is my table for itunes API

Beyonce = query_itunes("Beyonce")
Bieber = query_itunes("Bieber")
Miley_Cyrus = query_itunes("Miley")
songs = Beyonce + Bieber + Miley_Cyrus

#table for itunes API
cur.execute('DROP TABLE IF EXISTS iTunes')
cur.execute('CREATE TABLE iTunes(artist TEXT, artistId TEXT, trackName TEXT, trackNumber TEXT)')

for song in songs:
    cur.execute('INSERT INTO iTunes(artist, artistId, trackName, trackNumber) VALUES (?, ?,?,?)', 
                (song['artistName'], song['artistId'], song['trackName'], song['trackNumber']))

conn.commit()

#API 5 Pokemon
print ('\n------------------------------------\n')
print ('API #4: Pokemon\n')

def query_pokemon_directly(pokemon_number):
    baseurl = "https://pokeapi.co/api/v2/pokemon/{}/".format(pokemon_number)
    r = requests.get(baseurl)
    responses = r.text
    final = json.loads(responses)
    return final
    
def query_pokemon(pokemon_number):
    return performsearch(pokemon_number, query_pokemon_directly)
#SQL table for itunes itunes
pokemon_response_list = []
for i in range(1,251):
    printsequence(i)
    pokemon_response_list.append(query_pokemon(str(i)))

#create SQL table for pokemon
cur.execute('DROP TABLE IF EXISTS Pokemon')
cur.execute('CREATE TABLE Pokemon(id INTEGER, name TEXT , weight INTEGER, height INTEGER, base_experience INTEGER)')

for pokemon in pokemon_response_list:
    if pokemon != None:
        cur.execute('INSERT INTO Pokemon(id, name, weight, height, base_experience) VALUES (?, ?, ?,?,?)', 
                (prep(pokemon['id'], "int"), prep(pokemon['name'], "str"), prep(pokemon['weight'], "int"), prep(pokemon['height'], "int"), prep(pokemon['base_experience'], "int")))

printsequence("hi")
conn.commit()    
printsequence("bye")

#Here I will create the visuals

#Visual 1:

#Visual 2:

#Visual 3: