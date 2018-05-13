import glob, json, datetime
from collections import defaultdict

################################################################################
# create the threaded JSON file we need for the API.  will go through each
# post and take the replies JSON (which is just a list), and put it into a big
# JSON file. then later we can order everything by time, and also calculate
# the reply times
################################################################################

def spawn():
    """this function will create the original JSON file, by looking at all the
    already created reply.json files for each post"""
    files = glob.glob('./dataset/*/*/replies.json')
    threadJSON = defaultdict(list)
    for filename in files:
        post_list = []
        with open(filename, 'r') as f:
            try:
                postJSON = json.load(f) #load the post's replies
            except:
                print "couldn't load " + filename
                continue
        if postJSON:    #some files have empty replies
            threadID = postJSON[0]['id'].split('_')[0]
            for comment in postJSON:    #this is just a list
                #restructure the comment data
                #first need to do the replies
                reply_list = []
                if comment.get('replies', False):   #if replies
                    for reply in comment['replies']:
                        reply_dict = { 'time' : reply['created_time'],
                                       'id' : reply['id'],
                                       'message' : reply['message'] }
                        reply_list.append(reply_dict)


                comment_dict = { 'time' : comment['created_time'],
                                 'id' : comment['id'],
                                 'message' : comment['message'],
                                 'replies' : reply_list }

                post_list.append(comment_dict)
            threadJSON[threadID] = post_list
    return threadJSON


def getTime(time):
    """converts the time strings in the JSON to a datetime object"""
    formatted = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S+0000")
    return formatted

def order_by_time(THREADS):
    """loops through the JSON file we already have and re-orders everything by
    time, including the replies. creates a dummy key/value of datetime to
    make it simpler"""

    for thread in THREADS:
        print thread
        #first we need to sort the top-level comments
        #create the datetime dummy variable
        for comment in THREADS[thread]:
            formatted = getTime(comment['time'])
            comment['datetime'] = formatted
        THREADS[thread].sort(key=lambda x: x['datetime'])   #sort
        map((lambda y: y.pop('datetime', None)), THREADS[thread])
        #^^remove the dummy key/value

        #now for the replies
        for comment in THREADS[thread]:
            if comment['replies']:
                for reply in comment['replies']:
                    format_reply = getTime(reply['time'])
                    reply['datetime'] = format_reply
                comment['replies'].sort(key=lambda z: z['datetime'])    #sort
                map((lambda m: m.pop('datetime', None)), comment['replies'])
                #^^again delete the dummy key/value
    return THREADS

def index(THREADS):
    """further adds to our JSON file by adding an indexing key/value for
    quick access to specific comments. the index will be a tuple
    (top, reply) where top is the index of the comment's parent (or the
    comment itself if it's top level) in the list of top-level in the given
    thread. reply is the index of the reply in the 'replies' list"""

    for thread in THREADS:
        print thread
        for i, comment in enumerate(THREADS[thread]):
            comment['top_index'] = i
            comment['rep_index'] = None
            #the reply index is null for top
            if comment['replies']:
                for j, reply in enumerate(comment['replies']):
                        reply['top_index'] = i
                        reply['rep_index'] = j
    return THREADS

def get_userIDS(THREADS):
    """
    Add our randomized anonymized user IDs to each comment before 
    further processing.
    """
    with open("ANONYMIZED_COMMENTS.json", 'r') as f:
        ANON = json.load(f)

    for thread in THREADS:
        for comment in THREADS[thread]:
            comment['userID'] = str(ANON.get(comment['id'], "NA"))
            if comment['replies']:
                for reply in comment['replies']:
                    reply['userID'] = str(ANON.get(reply['id'], "NA"))
            # Comments that are obtained after our original access
            # won't show up in the ANON json, so give them the "NA"
            # user ID. These should be ignored in the USERS.json.

    return THREADS


def response(THREADS):
    """finalizes the threads.json by going through each comment and finding
    the time difference between it and the previously posted comment. for
    top level comments we'll be looking at previous top-level and for replies
    we'll be looking at replies only. we'll need to load in the times of the
    creations of the threads so that we can create a response time for the first
    comment of each thread. we can't serialize timedelta objects, so just write
    out the number of seconds as an integer."""

    with open('POST_TIMES.json', 'r') as f2:
            POST_TIMES = json.load(f2)

    for thread in THREADS:
        print thread
        #we have to handle the first comment differently
        first_time = getTime(THREADS[thread][0]['time'])
        #get the thread creation time
        if POST_TIMES.get(thread, False):
            post_time = getTime(POST_TIMES[thread])
            first_delta = first_time - post_time
        else:
            first_delta = datetime.timedelta.max

        first_response = first_delta.seconds
        THREADS[thread][0]['response'] = first_response
        #now for the rest of the top-level
        if len(THREADS[thread]) > 1:    #if we have more than 1 comment
            for i, comment in enumerate(THREADS[thread][1:]):
                comment_time = getTime(comment['time'])
                previous_time = getTime(THREADS[thread][i]['time'])
                #^this i here is tricky since we're enumerating on all the elements
                #except the first, so going one to the left gives us back i again!
                delta = comment_time - previous_time
                comment['response'] = delta.seconds

    return THREADS

def replyResponse(THREADS):
    """think it's better to put this part into its own function"""

    for thread in THREADS:
        print thread
        for comment in THREADS[thread]:
            if comment['replies']:
                #need to handle first one differently
                comment_time = getTime(comment['time'])
                first_reply = getTime(comment['replies'][0]['time'])
                first_delta = first_reply - comment_time
                comment['replies'][0]['response'] = first_delta.seconds

                if len(comment['replies']) > 1: #more than 1 reply
                    for i, reply in enumerate(comment['replies'][1:]):
                        reply_time = getTime(reply['time'])
                        prev_time = getTime(comment['replies'][i]['time'])
                        delta = reply_time - prev_time
                        reply['response'] = delta.seconds
    with open('THREADS.json', 'w') as f2:
        json.dump(THREADS, f2, indent = 4, sort_keys = True)

if __name__ == '__main__':
    THREADS = spawn()
    THREADS = order_by_time(THREADS)
    THREADS = index(THREADS)
    THREADS = get_userIDS(THREADS)
    THREADS = response(THREADS)
    replyResponse(THREADS)









