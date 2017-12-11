#Alyson Rosenberg
#SI 206 Final Project

import json
import sqlite3
import pprint
import requests
import datetime
import sys
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np



#-------------------------------------------------------------------

#load cache from cache file if cache file exists
CACHE_FNAME = "206_finalproject.json"
try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

#-------------------------------------------------------------------
#general function takes any direct API query and implements caching
def performsearch(search_term, api_query_function):
    cachekey = api_query_function.__name__ + "_" + search_term
    if cachekey in CACHE_DICTION:
        #print ("loading from cache")
        toreturn = CACHE_DICTION[cachekey]
    else:
        toreturn = api_query_function(search_term)
        CACHE_DICTION[cachekey] = toreturn
        writefile = open(CACHE_FNAME,"w")
        writefile.write(json.dumps(CACHE_DICTION))
        writefile.close()
    return toreturn

#-------------------------------------------------------------------
#create connection to local SQLite database
conn = sqlite3.connect('206_finalproject.sqlite')
cur = conn.cursor()

#-------------------------------------------------------------------
#this was used for purposes of debugging NoneType key errors
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
#-------------------------------------------------------------------
#instagram API
print ('API #1: Instagram\n')

instagram_access_token = "226042116.1677ed0.d72827a090bd4641a961139b7f04530b"

#this function gets all posts for whichever search term you input 
#returns posts for that instagram handle
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

#this function implements caching on above function
def query_instagram():
    return performsearch("blah", query_instagram_directly)

#-------------------------------------------------------------------
#SQL table for instagram
#Drops table if exists then creates
cur.execute('DROP TABLE IF EXISTS Instagram_Posts')
cur.execute('CREATE TABLE Instagram_Posts(id TEXT PRIMARY KEY, created_at TIMESTAMP, caption_text TEXT, likes INTEGER, lat INTEGER, lng INTEGER)')

#-------------------------------------------------------------------
#load posts into table 
#also load data into local variables for visualizations
Instagram_Posts = query_instagram()
weekdaylist = [0, 0, 0, 0, 0, 0, 0]
weekdaynames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
likeslist = []
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
    actualtimestamp = datetime.date.fromtimestamp( int(post['created_time']) )
    dow = actualtimestamp.weekday()
    weekdaylist[dow] += 1
    likeslist.append(numlikes)
    formatteddatetime = actualtimestamp.strftime('%Y-%m-%d %H:%M:%S')
   # print (post['id'], formatteddatetime, post['caption']['text'], post["likes"]['count'], post["location"]['latitude'], post["location"]['longitude'])
    cur.execute('INSERT INTO Instagram_Posts(id, created_at, caption_text, likes, lat, lng) VALUES (?, ?, ?, ?, ?, ?)', 
                (currentid, formatteddatetime, caption_text, numlikes, lat, long))
    
conn.commit()


#-------------------------------------------------------------------
#github API
print ('\n------------------------------------\n')
print ('API #2: GitHub\n')

#gets public data for inputted github user ID 
#returns events from that user
def query_github_directly(github_user_id = "alyrosenberg"):
    url = 'https://api.github.com/users/{}/events'.format(github_user_id)
    response_string = requests.get(url).text
    github_events = json.loads(response_string)
    return github_events

#implements caching on above function
def query_github(github_user_id = "alyrosenberg"):
    return performsearch(github_user_id, query_github_directly)


#-------------------------------------------------------------------
#create connection to local SQLite database for github
cur.execute('DROP TABLE IF EXISTS GitHub_Events')
#Dropping github table if it exists then initilizing github table
cur.execute('CREATE TABLE GitHub_Events(id INTEGER PRIMARY KEY, created_at TIMESTAMP, type TEXT, repo_name TEXT)')
#load events into table
GitHub_Events = query_github()
for event in GitHub_Events:
    cur.execute('INSERT INTO GitHub_Events(id, created_at, type, repo_name) VALUES (?, ?, ?, ?)', 
                (event['id'], event['created_at'], event['type'], event["repo"]['name']))

conn.commit()

#-------------------------------------------------------------------
#OMDB is my next API
print ('\n------------------------------------\n')
print ('API #3: OMDB\n')



#mykey = 3a894ff0

#this function querys OMDB for information on a specified movie title
def query_OMDB_directly(movie_title):
    base_url = "http://www.omdbapi.com/?"
    params_dict = {}
    params_dict['t'] = movie_title
    params_dict['apikey'] = "3a894ff0"
    r = requests.get(base_url, params=params_dict)
    responses = r.text
    final = json.loads(responses)
    return final


#query OMDB for movie title with caching
def query_OMDB(movie_title):
    return performsearch(movie_title, query_OMDB_directly)


#create SQL table from OMDB
cur.execute('DROP TABLE IF EXISTS OMDB_Movie')
cur.execute('CREATE TABLE OMDB_Movie (title TEXT PRIMARY KEY, year INTEGER, genre TEXT, director TEXT, imdbrating REAL)')

#this is a list of movies to query OMDB about
mymovies = ['Mean Girls','Wonder Woman', 'Get Out', 'Star Wars', 'The Big Sick', 'Lady Bird', 'La La Land', 'It', 'Titanic', 'The Notebook', 'Love Actually', 'Baby Driver', 'Dunkirk', 'The Fault in Our Stars', 'Endless Love','That Awkward Moment','The Longest Ride', 'Fifty Shades of Grey','Sleeping with Other People','Easy A', 'The Visit', 'The Conjuring', 'Moonlight', 'Jackie', 'Finding Dory', 'Sausage Party']

responses = []

#this adds movie info to SQL table
for movie in mymovies:
    movieinfo = query_OMDB(movie)
    responses.append(movieinfo)
    if movieinfo != None:
        cur.execute('INSERT INTO OMDB_Movie(title, year, genre, director, imdbrating) VALUES (?, ?, ?, ?,?)', 
                (movieinfo['Title'], movieinfo['Year'], movieinfo['Genre'], movieinfo["Director"], movieinfo['imdbRating']))

conn.commit()

#-------------------------------------------------------------------
#next API 4 is iTunes
print ('\n------------------------------------\n')
print ('API #4: iTunes\n')

#this function querys the iTunes API for the song best matching the search term
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

#this function implements the above function with caching
def query_itunes(search_term):
    return performsearch(search_term, query_itunes_directly)

#create a list of songs with their information
Beyonce = query_itunes("Beyonce")
Bieber = query_itunes("Bieber")
Miley_Cyrus = query_itunes("Miley")
songs = Beyonce + Bieber + Miley_Cyrus

#-------------------------------------------------------------------
#creates table for itunes API
cur.execute('DROP TABLE IF EXISTS iTunes')
cur.execute('CREATE TABLE iTunes(artist TEXT, artistId TEXT, trackName TEXT, trackNumber TEXT)')

#loads song data into table
for song in songs:
    cur.execute('INSERT INTO iTunes(artist, artistId, trackName, trackNumber) VALUES (?, ?,?,?)', 
                (song['artistName'], song['artistId'], song['trackName'], song['trackNumber']))

conn.commit()

#-------------------------------------------------------------------
#next API is Pokemon

print ('\n------------------------------------\n')
print ('API #5: Pokemon\n')

#this function returns information about a pokemon when given the pokemon's number
def query_pokemon_directly(pokemon_number):
    baseurl = "https://pokeapi.co/api/v2/pokemon/{}/".format(pokemon_number)
    r = requests.get(baseurl)
    responses = r.text
    final = json.loads(responses)
    return final

#this function implements the above with caching 
def query_pokemon(pokemon_number):
    return performsearch(pokemon_number, query_pokemon_directly)

#get information for the first 250 pokemon
pokemon_response_list = []
for i in range(1,251):
    pokemon_response_list.append(query_pokemon(str(i)))

#create SQL table for pokemon
cur.execute('DROP TABLE IF EXISTS Pokemon')
cur.execute('CREATE TABLE Pokemon(id INTEGER, name TEXT , weight INTEGER, height INTEGER, base_experience INTEGER)')

#adds pokemon information to SQL table
for pokemon in pokemon_response_list:
    if pokemon != None:
        cur.execute('INSERT INTO Pokemon(id, name, weight, height, base_experience) VALUES (?, ?, ?,?,?)', 
                (prep(pokemon['id'], "int"), prep(pokemon['name'], "str"), prep(pokemon['weight'], "int"), prep(pokemon['height'], "int"), prep(pokemon['base_experience'], "int")))


conn.commit()    

#-------------------------------------------------------------------
#visualizations
#bar graph of instagram posts by days of week
#https://plot.ly/~alyrosenberg is the link to access the visuals
print ('\n------------------------------------\n')
print ('plotly visualization #1 for Instagram posts by days of the week\n')
instalayout = go.Layout(
    title='Instagram Posts by Days of Week',
    xaxis=dict(
        title='Day of Week',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    ),
    yaxis=dict(
        title='Number of Posts',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#FFBAD2'
        )
    )
)


data = [go.Bar(
            x=weekdaynames,
            y=weekdaylist,
            marker=dict(
                color=['rgb(158,222,225)','rgb(255,140,0)', 'rgb(158,178,225)', 'rgb(247,25,1)', 'rgb(249,129,162)','rgb(118,42,125)','rgb(29,143,177)'],
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5,
                )
            ),
            opacity=0.6,

    )]


instafig = go.Figure(data=data, layout=instalayout)
py.iplot(instafig, filename= "Instagram_Posts")



#-------------------------------------------------------------------
#Visual 2 pie chart of movie genres:
print ('\n------------------------------------\n')
print ('plotly visualization #2 for GitHub Movie Genres\n')

plotly.tools.set_credentials_file(username='alyrosenberg', api_key='KqdFFr008XxE3bq2F6Cz')
labels = ['Drama','Comedy','Action','Horror', 'Biography', 'Animation']
drama = []
comedy = []
action = []
horror = []
biography = []
animation = []
for movie in responses:
    listgenres = movie['Genre'].split(',')
    genre = listgenres[0]
    if genre == 'Drama':
        drama.append(movie['Title'])
    if genre == 'Comedy':
        comedy.append(movie['Title'])
    if genre == 'Action':
        action.append(movie['Title'])
    if genre == 'Horror':
        horror.append(movie['Title'])
    if genre == 'Biography':
        biography.append(movie['Title'])
    if genre == 'Animation':
        animation.append(movie['Title'])


values = [len(drama), len(comedy), len(action),len(horror), len(biography), len(animation)]

trace = go.Pie(labels=labels, values=values)

colors = ['#a18bd2', '#FFBAD2', '#fc2a70', '##f9b152', '#ecf986', '#ddfff7']

trace = go.Pie(labels=labels, values=values,
               hoverinfo='label+percent', textinfo='value', 
               textfont=dict(size=20),
               marker=dict(colors=colors, 
                           line=dict(color='#000000', width=2)))
data = [trace]
annotations = []
annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
                              xanchor='left', yanchor='bottom',
                              text='Movie Genres Breakout',
                              font=dict(family='Arial',
                                        size=30,
                                        color='rgb(37,37,37)'),
                              showarrow=False))
pielayout = go.Layout()
pielayout['annotations'] = annotations
piefig = dict(data = data, layout=pielayout)

py.iplot(piefig, filename='Pie Chart of Movie Genres')


#-------------------------------------------------------------------

#Visual 3:
#scatter plot histogram of likes per post
print ('\n------------------------------------\n')
print ('plotly visualization #3 for Instagram likes per post\n')
likesinterval = 50
breakslist = list(range(0,850,likesinterval))
histo = np.histogram(likeslist, breakslist)[0].tolist()
binedges = breakslist[1:]
trace0 = go.Scatter(
    x=binedges,
    y=histo,
    mode='markers',
    connectgaps=True,
    )

annotations = []
likeslayout = go.Layout(xaxis=dict(title="Number of Likes"), yaxis=dict(title="Number of Posts"))
annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
                              xanchor='left', yanchor='bottom',
                              text='Insta Post Likes Bubble Chart',
                              font=dict(family='Arial',
                                        size=30,
                                        color='rgb(37,37,37)'),
                              showarrow=False))
likeslayout['annotations'] = annotations
data = [trace0]
likesfig = dict(data=data, layout = likeslayout)
py.iplot(likesfig, filename='Instagram Likes')
