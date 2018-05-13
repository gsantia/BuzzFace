import json, datetime
from collections import defaultdict

################################################################################
# given the thread.json file, this script will create a similar json file but
# keyed by user
################################################################################

def getTime(time):
    """parses datetime object from string"""
    formatted = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S+0000")
    return formatted

def spawn():
    """create the JSON, should be easy because we are really just restructuring
    the thread.json data"""
    with open('THREADS.json', 'r') as f:
        THREADS = json.load(f)

    COMMENTS = defaultdict(list)
    for thread in THREADS:
        for comment in THREADS[thread]:
            #easier to take care of the replies first
            if comment['replies']:
                for reply in comment['replies']:
                    reply_user = reply['userID']
                    reply.pop('userID')
                    COMMENTS[reply_user].append(reply)
            userID = comment['userID']
            comment.pop('userID')
            comment.pop('replies')
            COMMENTS[userID].append(comment)
    return COMMENTS


def time_sort(USER):
    """orders the comments made per user in a temporal manner"""

    for user in USER:
        #here we just need to sort each of these lists, there's
        #no additional structure to worry about
        for comment in USER[user]:
            formatted = getTime(comment['time'])
            comment['datetime'] = formatted
        USER[user].sort(key=lambda x: x['datetime'])
        map((lambda y: y.pop('datetime', None)), USER[user])

    with open('USERS.json', 'w') as f2:
        json.dump(USER, f2, indent = 4, sort_keys = True)

def cleanup():
    """
    Remove the unneeded fields from the THREADS.json file.
    """
    
    with open('THREADS.json', 'r') as f:
        THREADS = json.load(f)
    
    for thread in THREADS:
        for comment in THREADS[thread]:
            del comment['rep_index']
            del comment['top_index']
            if comment['replies']:
                for reply in comment['replies']:
                    del reply['rep_index']
                    del reply['top_index']

    with open('THREADS.json', 'w') as f2:
        json.dump(THREADS, f2, sort_keys = True, indent = 4)

if __name__ == '__main__':
    USER = spawn()
    time_sort(USER)
    cleanup()

