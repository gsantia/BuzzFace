import glob, json
from collections import defaultdict

###############################################################################
# this script will create a dict with keys being thread IDs and values
# being the time the post was made on facebook. for use with the API
###############################################################################

def main():
    """get the post times and write them to disk in a dict"""
    post_times_dict = defaultdict(str)
    files = glob.glob("./dataset/*/*/posts.json")
    for filename in files:
        with open(filename, 'r') as f:  #open the post JSON
            postJSON = json.load(f)
        post_time = ""
        if postJSON:
            post_time = postJSON.get('created_time', "")
        #split up the filepath by / to get the thread ID
        threadID = filename.split("/")[-2]
        post_times_dict[threadID] = post_time

    with open("POST_TIMES.json", "w") as f2:
        json.dump(post_times_dict, f2, indent = 4, sort_keys = True)

if __name__ == '__main__':
    main()



