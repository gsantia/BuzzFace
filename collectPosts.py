#!/usr/bin/python

import urllib2
import json
import os, re, csv
import time
import sys

APP_ID = str(sys.argv[1])
APP_SECRET = str(sys.argv[2])

def createFeedUrl(username, APP_ID, APP_SECRET, limit):
    post_args = "/feed?access_token=" + APP_ID + "|" + APP_SECRET + \
                "&fields=attachments,created_time,message&limit=" + str(limit)
    post_url = "https://graph.facebook.com/v3.0/" + username + post_args
    return post_url

def createPostUrl(USER_ID,POST_ID, APP_ID, APP_SECRET):
    post_args = "?access_token=" + APP_ID + "|" + APP_SECRET + \
                    "&fields=link,message,created_time,name,story,caption,description,picture,place,shares,source,updated_time"
    post_url = "https://graph.facebook.com/v3.0/" + USER_ID + "_" + POST_ID + post_args
    return post_url

def createPostCommentsUrl(USER_ID, POST_ID, APP_ID, APP_SECRET):
    comments_args = "/comments?access_token=" + APP_ID + "|" + APP_SECRET + \
                    "&order=chronological&limit=1000"
    comments_url = ("https://graph.facebook.com/v3.0/" + USER_ID + "_" +
                        POST_ID + comments_args)
    return comments_url

def createPostAttachmentsUrl(USER_ID,POST_ID, APP_ID, APP_SECRET):
    attachments_args = "/attachments?access_token=" + APP_ID + "|" + APP_SECRET
    attachments_url = ("https://graph.facebook.com/v3.0/" + USER_ID + "_" +
                        POST_ID + attachments_args)
    return attachments_url

def createPostReactionsUrl(USER_ID,POST_ID, APP_ID, APP_SECRET):
    reactions_args = "/reactions?access_token=" + APP_ID + "|" + APP_SECRET + \
                    "&limit=1000"  
    reactions_url = ("https://graph.facebook.com/v3.0/" + USER_ID + "_" + POST_ID +
                        reactions_args)
    return reactions_url

def new_createPostReactionsUrl(USER_ID, POST_ID, APP_ID, APP_SECRET):
    reactions_args = "/reactions?access_token=" + APP_ID + "|" + APP_SECRET + \
            "&summary=total_count"
    reactions_url = "https://graph.facebook.com/v3.0/" + USER_ID + "_" + POST_ID + \
            reactions_args
    return reactions_url

def getUserFeed(username, limit):
    post_url = createPostUrl(username, APP_ID, APP_SECRET, limit)
    web_response = urllib2.urlopen(post_url)
    readable_page = web_response.read()
    return json.loads(readable_page)

def getPost(USER_ID, POST_ID):
    ## have this build urls for the comments, reactions, and attachments
    post_url = createPostUrl(USER_ID, POST_ID, APP_ID, APP_SECRET)
    web_response = urllib2.urlopen(post_url)
    readable_page = web_response.read()
    return json.loads(readable_page)

def getPostReactions(USER_ID, POST_ID):
    """returns a JSON of a post's reactions"""
    ###############################################
    # This code is deprecated! Facebook changed the
    # API on Feb 5, 2018, so now none of this works.
    ###############################################
    """
    data = []
    post_url = createPostReactionsUrl(USER_ID, POST_ID, APP_ID, APP_SECRET)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib2.install_opener(opener)
    batchnum = 1
    time.sleep(1)

    try:
        web_response = urllib2.urlopen(post_url)
        readable_page = web_response.read()
        thisdata = json.loads(readable_page)
        data.extend(thisdata['data'])
    except:
        print "reacts didn't work at all!"
        #just return an empty dict here
        return {}

    if 'paging' in thisdata.keys():
        while thisdata['paging'].get('next', False):
            time.sleep(1)
            batchnum += 1
            print "reacts batch: ", batchnum
            try:
                web_response = urllib2.urlopen(thisdata['paging']['next'])
                thisdata = json.loads(web_response.read())
                if thisdata['data']:
                    data.extend(thisdata['data'])
            except:
                print "problem getting extra batches"
    reacts = {'data' : data}
    return reacts
    """
    post_url = new_createPostReactionsUrl(USER_ID, POST_ID, APP_ID, APP_SECRET)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib2.install_opener(opener)
    try:
        web_response = urllib2.urlopen(post_url)
        readable_page = web_response.read()
        thisdata = json.loads(readable_page)
    except:
        print "reacts didn't work at all!"
        return None

    return thisdata['summary']['total_count']

def getPostComments(USER_ID, POST_ID, n = 1):
    """returns a JSON of a post's comments"""
    data = []
    post_url = createPostCommentsUrl(USER_ID, POST_ID, APP_ID, APP_SECRET)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib2.install_opener(opener)
    batchnum = 1
    time.sleep(n)

    try:
        web_response = urllib2.urlopen(post_url)
        readable_page = web_response.read()
        thisdata = json.loads(readable_page)
        data.extend(thisdata['data'])
    except:
        print "comments didn't work at all!"
        #in this case, just return an empty dict
        return {}

    if 'paging' in thisdata.keys():
        while thisdata['paging'].get('next', False):
            time.sleep(n)
            batchnum += 1
            print "comments batch: ", batchnum
            try:
                web_response = urllib2.urlopen(thisdata['paging']['next'])
                thisdata = json.loads(web_response.read())
                if thisdata['data']:
                    data.extend(thisdata['data'])
            except:
                print "problem getting extra batches"
    comments = {"data" : data}
    return comments

def getPostAttachments(USER_ID, POST_ID, n = 1):
    """returns a JSON of a post's attachments"""
    post_url = createPostAttachmentsUrl(USER_ID, POST_ID, APP_ID, APP_SECRET)
    time.sleep(n)
    web_response = urllib2.urlopen(post_url)
    readable_page = web_response.read()
    return json.loads(readable_page)


if __name__ == "__main__":
    buzzfeed = []
    # If you like, you can change how long the program waits after
    # each API call here by setting n = (number of seconds). To be
    # safe and follow Facebook's conditions, we set n = 1 by default.
    # Change at your own risk.
    n = 1

    #make a dict to relate outlet names to their url repn's
    outlet_urls = {"ABC_News_Politics" : 'abc',
               "Addicting_Info" : 'addictinginfo',
               "CNN_Politics" : "cnn",
               "Eagle_Rising" : "eaglerising",
               "Freedom_Daily" : "freedomdaily",
               "Occupy_Democrats" : "occupydemocrats",
               "Politico" : "politi.co",
               "Right_Wing_News" : "rightwingnews",
               "The_Other_98%" : "TheOther98" }

    #first load the buzzfeed data
    buzzfeed_file = 'facebook-fact-check.csv'
    with open(buzzfeed_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            buzzfeed.append(row)

    del buzzfeed[0]
    #now go thru each article
    for article in buzzfeed:
        if article:
            USER_ID = article[0]
            POST_ID = article[1]
            url = article[4]
            outlet = article[3].replace(" ", "_")
            article_type = article[6]

            print "working on " + POST_ID
            #get post
            try:
                time.sleep(n)
                postJson = getPost(USER_ID, POST_ID)
                postJson['type'] = article_type
                first_party = True if outlet_urls[outlet] in postJson.get('link') else False
                postJson['first_party'] = first_party
            except:
                print "post error"
                postJson = {}
            #get number of reactions
            postJson['reacts'] = getPostReactions(USER_ID, POST_ID)
            #get comments and reacts
            time.sleep(n)
            commentJson = getPostComments(USER_ID, POST_ID, n)

            #get attachments
            try:
                attachJson = getPostAttachments(USER_ID, POST_ID, n)
            except:
                print "attach"
                attachJson = {}

            wd = 'dataset/'
            if not os.path.isdir('./dataset/'):
                os.system('mkdir dataset')
            postfile = wd + outlet + '/' + POST_ID + '/posts.json'
            commentfile = wd + outlet + '/' + POST_ID + '/comments.json'
            attachfile = wd + outlet + '/' + POST_ID + '/attach.json'
            os.system('mkdir -p ' + wd + outlet + '/' + POST_ID)
            os.system('touch ' + postfile)
            os.system('touch ' + commentfile)
            os.system('touch ' + attachfile)

            with open(postfile, 'w') as f:
                json.dump(postJson, f, indent = 4, sort_keys = True)

            with open(commentfile, 'w') as f2:
                json.dump(commentJson, f2, indent = 4, sort_keys = True)

            with open(attachfile, 'w') as f4:
                json.dump(attachJson, f4, indent = 4, sort_keys = True)
