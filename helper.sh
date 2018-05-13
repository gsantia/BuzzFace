#!/bin/bash

# Collect the posts, attachments, and top-level comments
sudo python2 collectPosts.py $1 $2

# Go through and query each top-level comment for their replies, sort them
# and add the appropriate fields
sudo python2 threaded_comments.py $1 $2

# Access the news articles themselves and download the relevant data.
# Also collect the Facebook Plugin and Disqus Plugin comments.
sudo python2 scrape.py $1 $2 $3 $4

# Get the post times and store them for getting response times
sudo python2 get_post_times.py

# Create the THREADS.json file, the comments organzied by thread ID
sudo python2 order_by_thread.py

# Create the USERS.json file, the comments organized by anonymized user ID
sudo python2 order_by_user.py

