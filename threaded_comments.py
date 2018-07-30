#!/usr/bin/python
import csv, httplib, glob, json, os, re, urllib2, time
from collections import Counter
import sys

APP_ID = str(sys.argv[1])
APP_SECRET = str(sys.argv[2])

def createPostCommentsUrl(COMMENT_ID, APP_ID, APP_SECRET):
    comments_args = "/comments?access_token=" + APP_ID + "|" + APP_SECRET + \
                    "&order=chronological&limit=1000"
    #there's an article with 159047 comments
    comments_url = "https://graph.facebook.com/" + COMMENT_ID + comments_args
    return comments_url

def createAnon(USER_ID, APP_ID, APP_SECRET):
    url = "https://graph.facebook.com/" + USER_ID + "/third_party_id?access_token=" \
            + APP_ID + "|" + APP_SECRET
    return url

def getAnon(USER_ID):
    anon_url = createAnon(USER_ID, APP_ID, APP_SECRET)
    web_response = urllib2.urlopen(anon_url)
    readable_page = web_response.read()
    return json.loads(readable_page)

def openPage(webpage):
    """properly open webpages in Python"""
    web_response = None
    hdr = {'User-agent' : 'Mozilla/5.0'}
    req = urllib2.Request(webpage, headers=hdr)
    try:
        web_response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print e.fp.read()
    except urllib2.URLError, e:
        print "URL ERROR: ", webpage
    except httplib.HTTPException, e:
        print "HTTP EXCEPTION: ", webpage
    except Exception, e:
        print "other exception loading the page: ", webpage

    return web_response


def getPostComments(COMMENT_ID, n):
    """returns a JSON of a comment's comments"""
    data = []
    post_url = createPostCommentsUrl(COMMENT_ID, APP_ID, APP_SECRET)
    batchnum = 1
    
    time.sleep(n)
    try:
        web_response = openPage(post_url)
        readable_page = web_response.read()
        thisdata = json.loads(readable_page)
        data.extend(thisdata['data'])
    except:
        print "comments didn't work at all!"
        #in this case, just return an empty dict
        return {}

    if 'paging' in thisdata.keys():
        while thisdata['paging'].get('next', False):
            batchnum += 1
            time.sleep(n)
            print "comments batch: ", batchnum
            try:
                web_response = openPage(thisdata['paging']['next'])
                thisdata = json.loads(web_response.read())
                if thisdata['data']:
                    data.extend(thisdata['data'])
            except:
                print "problem getting extra batches"
    comments = {"data" : data}
    return comments

def retrieve(outlet):
    """initiate the retrieval of the comment replies for a specific _outlet_"""

    path = './dataset/'
    files = glob.glob(path + outlet + '/*/comments.json')
    for i, filename in enumerate(files[:10]):
        print "working on %s" % str(i)
        #open the old comments file
        try:
            with open(filename, 'r') as f:
                commentsJSON = json.load(f)
        except:
            print "problem opening comments.json"
            continue

        commentsJSON = commentsJSON.get('data', []) #this is just a list
        for j, comment in enumerate(commentsJSON):
            print "          comment #: ", str(j)
            COMMENT_ID = comment['id']
            #add the replies key
            # NOTE: this will take an extremely long time with the new API limit,
            # so this has been commented out. if you'd like to wait and get every single
            # reply, uncomment this and get rid of the dummy replies line following
            #comment['replies'] = getPostComments(COMMENT_ID, n).get('data', [])
            comment['replies'] = []
        #now write the new file to disk
        new_filename = filename[:-13] + 'replies.json' #chop off the 'comments.json'
        os.system('touch ' + new_filename)
        with open(new_filename, 'w') as f2:
            json.dump(commentsJSON, f2, indent = 4, sort_keys = True)

if __name__ == '__main__':
    n = 20
    # This n is again the number of seconds the script sleeps after each API
    # request. Change at your own risk.
    #
    # NOTE: changed from 1 to 20 due to changes in FB API

    outlets = ['ABC_News_Politics',
               'Politico',
               'CNN_Politics',
               'Addicting_Info',
               'Eagle_Rising',
               'Freedom_Daily',
               'Occupy_Democrats',
               'Right_Wing_News',
               'The_Other_98%']

    for outlet in outlets:
        if os.path.isdir('./dataset/' + outlet):
            retrieve(outlet)
