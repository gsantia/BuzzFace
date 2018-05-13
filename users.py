import datetime, glob, json, re
from collections import Counter, defaultdict
import threads, main

###########################################################################
# Allows for the API user to examine a single User in the data set and look
# at various features of their comments
###########################################################################

class User(object):
    """this will hold the data we'd like for a single user,
    such as the comments, the times they were made, threads the
    user commented in, etc."""

    def __init__(self, userID, COMMENTS):
        """userID is the Facebook ID of the user, and COMMENTS is a
        list containing all scraped comments for them."""

        #all the data
        self.COMMENTS = COMMENTS
        #user ID
        self.userID = userID
        #list of the total text of the comments made
        self.all_text = [comment['message'] for comment in COMMENTS]
        #list of the times of the comments
        self.all_times = [threads.Thread.getTime(x['time'])
                          for x in COMMENTS]
        #list of comment/time tuples
        self.all_text_time = zip(self.all_text, self.all_times)
        #list of the threads commented in
        self.all_threads = [User.getThread(comment)
                            for comment in COMMENTS]
        #same things but of the replies made. this won't always be necessary,
        #so just make it a method
        self.reply_text = []
        self.reply_times = []
        self.reply_text_time = []
        self.reply_threads = []

        #now the same categories but for the top-level comments only.
        #again this won't always be needed, so put the initialization in a
        #method
        self.top_text = []
        self.top_times = []
        self.top_text_time = []
        self.top_threads = []

    def getStructure(self):
        """setup the top-level and reply parameters"""
        for comment in self.COMMENTS:
            message = comment['message']
            time = threads.Thread.getTime(comment['time'])
            thread = User.getThread(comment)
            if comment['rep_index']:    #this is a reply
                self.reply_text_time.append((message, time))
                self.reply_threads.append(thread)
            else:   #top-level
                self.top_text_time.append((message, time))
                self.top_threads.append(thread)

        if self.reply_text_time:    #can't unpack null
            self.reply_text, self.reply_times = zip(*self.reply_text_time)
        if self.top_text_time:
            self.top_text, self.top_times = zip(*self.top_text_time)

    def counterThreads(self, choice = "All"):
        """returns the list of threads as a Counter for easier analysis. user
        may choose between all, top-level, and replies using _choice_"""
        if choice == 'All':
            THREADS = self.all_threads
        elif choice == 'Top':
            THREADS = self.top_threads
        elif choice == 'Reply':
            THREADS = self.reply_threads

        thread_counter = Counter()
        for thread in THREADS:
            thread_counter[thread] += 1
        return thread_counter

    def responseTimes(self, choice = "All"):
        """return a list of time taken from the previous comment in the thread
        till the comment was made."""
        response_times = []
        if choice == "All":
            for comment in self.COMMENTS:
                response_times.append(comment['response'])
        elif choice == "Top":
            for comment in self.COMMENTS:
                if not comment['rep_index']:
                    response_times.append(comment['response'])
        elif choice == "Reply":
            for comment in self.COMMENTS:
                if comment['rep_index']:
                    response_times.append(comment['response'])
        return response_times

    @staticmethod
    def getThread(comment):
        """given a _comment_ dict will return the thread ID"""
        return comment['id'].split('_')[0]











