import datetime, glob, json, re
from collections import defaultdict, Counter
import users, threads

################################################################################
# this is the main implementation of the API, consisting of many
# functions for the user to use in their analysis of the data
################################################################################


#first load the files we need
with open('THREADS.json', 'r') as f:
    COMMENTS_BY_THREAD = json.load(f)

with open('USERS.json', 'r') as f2:
    COMMENTS_BY_USER = json.load(f2)

def badInput():
    """prints out bad input for wrong inputs"""
    print "bad input, try again"

def getThread(threadID):
    """returns a Thread object for the thread with ID _threadID_"""
    thread = None
    THREAD = COMMENTS_BY_THREAD.get(threadID, None)
    if THREAD:
        thread = threads.Thread(threadID, THREAD)
    return thread

def threadResponse(threadID, choice = "All"):
    """returns a list of response times for the thread with ID
    _threadID. allows for the usual choice of structure with
    _choice"""
    thread = getThread(threadID)
    if choice not in ("All", "Top", "Reply"):
        badInput()
    else:
        return thread.responseTimes(choice)

def threadText(threadID, choice = "All"):
    """returns the a list of the text of thread with _threadID_.
    allows the user to choose top-level or replies only, using
    _choice_ = "All" or "Reply"""
    thread = getThread(threadID)
    if choice == "All":
        return thread.all_text
    elif choice == "Top":
        return thread.top_text
    elif choice == "Reply":
        return thread.reply_text
    else:
        badInput()

def threadTimes(threadID, choice = "All"):
    """returns a list of times of the comments on the thread,
    allows for choice of top-level or replies only as before"""
    thread = getThread(threadID)
    if choice == "All":
        return thread.all_times
    elif choice == "Top":
        return thread.top_times
    elif choice == "Reply":
        return thread.reply_times
    else:
        badInput()

def threadUsers(threadID, choice = "All"):
    """returns a list of userIDs for the users that commented
    in thread _threadID_. allows for choice of top-level or
    replies using _choice_"""
    thread = getThread(threadID)
    if choice == "All":
        return thread.all_users
    elif choice == "Reply":
        return thread.reply_users
    elif choice == "Top":
        return thread.top_users
    else:
        badInput()

def threadCommentTime(threadID, choice = "All"):
    """returns list of tuples of _threadID_ thread of
    messages with their times. allows for _choice_ of top
    and reply"""
    thread = getThread(threadID)
    if choice == "All":
        return thread.all_text_time
    elif choice == "Top":
        return thread.top_text_time
    elif choice == "Reply":
        return thread.reply_text_time
    else:
        badInput()

def threadUserCounter(threadID, choice = "All"):
    """returns Counter of most users which commented the
    most in _threadID_ thread. allows for _choice_ of
    only top-level or replies"""
    thread = getThread(threadID)
    return thread.counterUsers(choice)

def getUser(userID):
    """returns a User object for the user with _userID_"""
    COMMENTS = COMMENTS_BY_USER[userID]
    user = users.User(userID, COMMENTS)
    return user

def userResponse(userID, choice = "All"):
    """returns the response times of comments made by User with _userID_,
    allows for top-level or replies with _choice_"""
    user = getUser(userID)
    if choice != "All":     #need to load the additional structure
        user.getStructure()
    return user.responseTimes(choice)

def userText(userID, choice = "All"):
    """returns a list of the text of the messages made by _userID_. allows
    for _choice_ of top or reply only"""
    user = getUser(userID)
    if choice != "All":
        user.getStructure()
    if choice == "All":
        return user.all_text
    elif choice == "Top":
        return user.top_text
    elif choice == "Reply":
        return user.reply_text
    else:
        badInput()

def userTimes(userID, choice = "All"):
    """returns a list of the times of the messages made by _userID_. allows for
    _choice_ of top or reply only"""
    user = getUser(userID)
    if choice != "All":
        user.getStructure()
    if choice == "All":
        return user.all_times
    elif choice == "Top":
        return user.top_times
    elif choice == "Reply":
        return user.reply_times
    else:
        badInput()

def userThreads(userID, choice = "All"):
    """returns a list of threadIDs of the threads _userID_ posted in. allows for
    _choice_ of top or reply only"""
    user = getUser(userID)
    if choice != "All":
        user.getStructure()
    if choice == "All":
        return user.all_threads
    elif choice == "Top":
        return user.top_threads
    elif choice == "Reply":
        return user.reply_threads
    else:
        badInput()

def userTextTimes(userID, choice = "All"):
    """returns list of tuples of messages with their post times for _userID_,
    allows for _choice_ of top or reply"""
    user = getUser(userID)
    if choice != "All":
        user.getStructure()
    if choice == "All":
        return user.all_text_time
    elif choice == "Top":
        return user.top_text_time
    elif choice == "Reply":
        return user.reply_text_time
    else:
        badInput()

def userThreadCounter(userID, choice = "All"):
    """returns a Counter of the threads that _userID_ commented in.
    allows for _choice_ of top or reply"""
    user = getUser(userID)
    if choice != "All":
        user.getStructure()
    return user.counterThreads(choice)

def cutThread(threadID, date_time):
    """allows the user to look at the contents of a thread from the
    start until the given _date_time_. this will be a datetime object,
    datetime(year, month, day, hour, minute, second, microsecond, timezone).
    just returns the slice of the thread as a new Thread object,
    which the user can then apply functions to"""
    THREAD = COMMENTS_BY_THREAD[threadID]
    CUT_THREAD = [] #only want comments before date_time
    for comment in THREAD:
        formatted = threads.Thread.getTime(comment['time'])
        if formatted <= date_time:
            CUT_THREAD.append(comment)
    #now we have the top level comments from t=0 to _datetime_,
    #but we still need to chop off the replies that were made after _datetime_
    for com in CUT_THREAD:
        new_replies = []    #only want the replies up till _datetime_
        if com['replies']:
            for reply in com['replies']:
                form_reply = threads.Thread.getTime(reply['time'])
                if form_reply <= date_time:
                    new_replies.append(reply)
            com['replies'] = new_replies
    thread = threads.Thread(threadID, CUT_THREAD)
    return thread





