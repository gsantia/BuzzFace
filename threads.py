import datetime, json
from collections import Counter, defaultdict
import users

###########################################################################
# Allows for the API user to examine a single Thread in the data set and look
# at various features such as the comments, the users involved, the times of
# the comments, etc
###########################################################################

class Thread(object):
    """this will hold the data we'd like for a single thread,
    such as the comments, the times they were made, the users etc.
    not sure about the methods yet."""

    def __init__(self, threadID, THREAD):
        """threadID is the Facebook ID of the thread, and THREAD is a
        list containing all comment JSONs for it."""

        self.THREAD = THREAD
        self.threadID = threadID
        #the time of the original FB post sparking the comment thread
        self.post_time = self.getPostTime()
        #list of the total text of the comments made
        self.all_text = []
        #list of the times of the comments, in datetime format
        self.all_times = []
        #list of comment/time tuples
        self.all_text_time = []
        #list of the userIDs that made comments in the thread
        self.all_users = []

        #it might be useful to split up a thread into top and reply
        #comments like with User. again keep this in a method
        self.top_text = []
        self.top_times = []
        self.top_text_time = []
        self.top_users = []

        #now the same for the replies
        self.reply_text = []
        self.reply_times = []
        self.reply_text_time = []
        self.reply_users = []

        #fill out the parameters with _getStructure_
        self.getStructure()

    def getStructure(self):
        """setup the top-level and reply parameters"""
        for comment in self.THREAD:
            message = comment['message']
            time = Thread.getTime(comment['time'])
            userID = comment['userID']
            #adjust all parameters
            self.all_text_time.append((message, time))
            self.all_users.append(userID)
            #adjust top-level parameters
            self.top_text_time.append((message, time))
            self.top_users.append(userID)

            if comment['replies']:  #there are replies, loop through them
                for reply in comment['replies']:
                    reply_message = reply['message']
                    reply_time = Thread.getTime(reply['time'])
                    #add to all
                    self.all_text_time.append((reply_message, reply_time))
                    #add to replies
                    self.reply_text_time.append((reply_message, reply_time))
                    self.reply_users.append(reply['userID'])
        if self.all_text_time:  #can't unpack null
            self.all_text, self.all_times = zip(*self.all_text_time)
        if self.top_text_time:  #can't unpack null
            self.top_text, self.top_times = zip(*self.top_text_time)
        if self.reply_text_time:
            self.reply_text, self.reply_times = zip(*self.reply_text_time)


    def counterUsers(self, choice = "All"):
        """returns the list of users as a Counter for easier analysis.
        allows for top-level or reply users only using _choice_"""
        user_counter = Counter()
        if choice == "All":
            USERS = self.all_users
        elif choice == "Top":
            USERS = self.top_users
        elif choice == "Reply":
            USERS = self.reply_users
        else:   #bad input
            print "bad input"
            return False
        for user in USERS:
            user_counter[user] += 1
        return user_counter

    def getPostTime(self):
        """gets the post time of the thread and returns it in datetime form"""
        with open('POST_TIMES.json', 'r') as f:
            POST_TIMES = json.load(f)
        post_time = POST_TIMES.get(self.threadID, None)
        if not post_time:
            return None
        else:
            return Thread.getTime(post_time)

    def responseTimes(self, choice = "All"):
        """returns a list of time taken from the previous comment till the
        current comment. allows for structure choice, like before"""
        response_times = []
        if choice == "All":
            for comment in self.THREAD:
                response_times.append(comment['response'])
                if comment['replies']:
                    for reply in comment['replies']:
                        response_times.append(reply['response'])
        elif choice == "Top":
            for comment in self.THREAD:
                response_times.append(comment['response'])
        elif choice == "Reply":
            for comment in self.THREAD:
                if comment['replies']:
                    for reply in comment['replies']:
                        response_times.append(reply['response'])
        return response_times

    @staticmethod
    def getTime(time):
        """produce a datetime object from a time string"""
        formatted = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S+0000")
        return formatted

