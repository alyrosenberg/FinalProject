import seaborn as sns
# import matplotlib.pyplot as plt
# %matplotlib inline
# plt.rcParams['figure.figsize'] = (15,9)
import json
import sqlite3
import pprint
import requests
import facebook
import datetime

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

instagram_access_token = "226042116.1677ed0.d72827a090bd4641a961139b7f04530b"


#instagram
def query_instagram_directly(search_term):
    url = 'https://api.instagram.com/v1/users/self/media/recent/?access_token={}'.format(instagram_access_token)
    response_string = requests.get(url).text
    posts = json.loads(response_string)['data']
    #user_id = posts[0]['user']['id']
    return posts

def query_instagram():
    return performsearch("blah", query_instagram_directly)

#x = query_instagram()
#pprint.pprint(x)


#github
def query_github_directly(github_user_id = "alyrosenberg"):
    url = 'https://api.github.com/users/{}/events'.format(github_user_id)
    response_string = requests.get(url).text
    github_events = json.loads(response_string)
    return github_events

def query_github(github_user_id = "alyrosenberg"):
    return performsearch(github_user_id, query_github_directly)

#create connection to local SQLite database
conn = sqlite3.connect('206_finalproject.sqlite')
cur = conn.cursor()

#Dropping github table if it exists then initilizing github table
cur.execute('DROP TABLE IF EXISTS GitHub_Events')
cur.execute('CREATE TABLE GitHub_Events(id INTEGER PRIMARY KEY, created_at TIMESTAMP, type TEXT, repo_name TEXT)')

GitHub_Events = query_github()
for event in GitHub_Events:
    cur.execute('INSERT INTO GitHub_Events(id, created_at, type, repo_name) VALUES (?, ?, ?, ?)', 
                (event['id'], event['created_at'], event['type'], event["repo"]['name']))



#Dropping github table if it exists then initilizing github table
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
    formatteddatetime = datetime.datetime.fromtimestamp( int(post['created_time']) ).strftime('%Y-%m-%d %H:%M:%S')
    #formateddatetime = datetime.datetime.fromtimestamp(int(post['created_time'])
    #print (post['id'], formatteddatetime, post['caption']['text'], post["likes"]['count'], post["location"]['latitude'], post["location"]['longitude'])
    cur.execute('INSERT INTO Instagram_Posts(id, created_at, caption_text, likes, lat, lng) VALUES (?, ?, ?, ?, ?, ?)', (post['id'], formatteddatetime, post['caption']['text'], post["likes"]['count'], lattemp, lngtemp))
    
conn.commit()