#!/usr/bin/python
import glob, httplib, json, os, re, time, urllib2
from bs4 import BeautifulSoup
import sys

APP_ID = str(sys.argv[1])
APP_SECRET = str(sys.argv[2])

DISQUS_ID = str(sys.argv[3])
DISQUS_SECRET = str(sys.argv[4])

def scrapeAddicting(webpage):
    """scrapes important info from an Addicting Info _webpage_"""

    articleJSON, page = createPage(webpage)
    soup = BeautifulSoup(page)

    #the body text is all contained in <p> tags
    raw_text = soup.body.find_all('p')
    text = []
    for para in raw_text:
        if para.get_text():
            if not para.find('em'): #not part of the body text
                text.append(para.get_text())
                links = para.find_all('a')
                if links:
                    for link in links:
                        link_url = link['href']
                        link_text = link.get_text()
                        articleJSON['links'].append([link_url, link_text])
                        if 'https://twitter.com' in link_url:
                            if 'status' in link_url:
                                articleJSON['tweets'].append(link_url)
        #now get the pictures
        pics = para.find_all('img')
        if pics:
            for pic in pics:
                pic_url = pic['src']
                pic_text = pic.get('alt', '')
                articleJSON['pictures'].append([pic_url, pic_text])

    articleJSON['body'] = " ".join(text)
    #no Disqus or FB comments
    """
    There is no robots.txt for the Addicting Info site, and no mention
    of rate limiting. In this case, wait 30 seconds between scrapes,
    just to be safe.
    """
    time.sleep(30)
    return articleJSON

def scrapePolitico(webpage):
    """takes the url of a politi.co article and scrapes important info
    using BeautifulSoup"""
    #pictures key will have a list of tuples of image link and its caption
    #links key will be list of tuples of link and its naming
    articleJSON, page = createPage(webpage)
    soup = BeautifulSoup(page, 'html5lib')

    #first find the figures and their captions
    figures = soup.find_all('figure', class_ = 'art')
    if figures:
        for figure in figures:
            captions = figure.find_all('p', class_ = '')
            if captions:
                caption = captions[0].get_text().strip()
            else:
                caption = ""
            images = figure.find_all('img')
            if images:
                if images[0]['src']:
                    image = images[0]['src']
                else:
                    image = ""
            else:
                image = ""
            articleJSON["pictures"].append((image, caption))

    #now find the links and their text
    links = [x
             for x in soup.body.find_all('a')
             if x.parent.name == 'p']
    #the last one is just an ad
    if links:
        for link in links:
            #get rid of the ad at the bottom for some of the articles
            if not link.parent.get('class'):
                link.parent['class'] = ''
            if link.get_text() != 'POLITICO Playbook':
                if link.parent['class'] != 'category':
                    url = link['href'] if link['href'] else ""
                    text = link.get_text().strip()
                    articleJSON['links'].append((url, text))
    paras = [x
             for x in soup.body.find_all('p', class_ = "")
             if x.parent.name != "figcaption"]
    #these are the <p> tags with the body text, minus those for figs
    #and the blurbs at the bottom
    if paras:
        raw_text = [x.get_text().strip() for x in paras]
        #seems like the last <p> is just going to be an ad, delete it
        article = " ".join(raw_text[:-1])
        articleJSON["body"] = article
    #get tweets
    articleJSON['tweets'] = getTweets(soup)
    #just FB comments
    """
    The robots.txt file and Terms of Service for the Politico site
    makes no mention of rate limiting. So let's just go with the 
    standard.
    """
    time.sleep(30)
    return articleJSON

def scrapeRightWing(webpage):
    """scrapes important info from RightWingNews articles"""
    articleJSON, page = createPage(webpage)
    soup = BeautifulSoup(page, 'html5lib')
    raw_text = soup.body.find_all('p')
    #get the body text and the links
    text = []
    for para in raw_text:
        if 'main-article' in para.parent.get('class', []):  #just want content
            if para.get_text():
                text.append(para.get_text().strip())
                #get the links here too
                links = para.find_all('a')
                if links:
                    for link in links:
                        link_url = link['href']
                        link_text = link.get_text()
                        articleJSON['links'].append([link_url, link_text])
    body = " ".join(text)
    articleJSON['body'] = body
    #now scrape the pictures
    centered = soup.body.find_all('center')
    photos = soup.find_all('img', class_ = 'article-photo')
    for photo in photos:
        photo_text = photo.get_text().strip()
        photo_url = photo['src']
        articleJSON['pictures'].append([photo_text, photo_url])
    for center in centered:
        images = center.find_all('img')
        for image in images:
            image_text = image.get_text().strip()
            image_url = image['src']
            articleJSON['pictures'].append([image_url, image_text])
    articleJSON['tweets'] = getTweets(soup)
    #just FB comments
    """
    The robots.txt file for Right Wing News says there must be a
    delay of 30 seconds between scrapes, so that's what we'll do.
    There is no mention of restrictions in the Terms of Service.
    """
    time.sleep(30)
    return articleJSON

def scrapeEagle(webpage):
    """scrapes important info from Eagle Rising articles"""
    articleJSON, page = createPage(webpage)
    soup = BeautifulSoup(page)
    text = []
    raw_text = soup.article.find_all('p')
    for para in raw_text:
        if para.get_text():
            text.append(para.get_text().strip())
            #get the links
            links = para.find_all('a')
            if links:
                for link in links:
                    link_url = link['href']
                    link_text = link.get_text().strip()
                    articleJSON['links'].append([link_url, link_text])
        #get the images
        images = para.find_all('img')
        if images:
            for image in images:
                image_url = image.get('src')
                image_caption = image.get('alt').strip()
                articleJSON['pictures'].append([image_url, image_caption])
    articleJSON['body'] = " ".join(text)
    articleJSON['tweets'] = getTweets(soup)
    #has both FB and Disqus comments!
    articleJSON['DisqComm'] = getDisqComments(webpage, forum = 'eaglerising')
    """
    The robots.txt file for Eagle Rising designates the delay time to be
    10 seconds, so that's what we'll use. The Terms of Service make no mention
    of it.
    """
    time.sleep(10)
    return articleJSON

def scrapeOccupy(webpage):
    """scrapes important info from OccupyDemocrats articles"""
    articleJSON, page = createPage(webpage)
    soup = BeautifulSoup(page, 'lxml')

    #get the main article image
    main_pic = soup.find_all('img', class_ = "attachment- size- wp-post-image")
    if main_pic:
        main_url = main_pic[0]['src']
        main_caption = main_pic[0].get_text().strip()
        articleJSON['pictures'].append([main_url, main_caption])
    other_pics = soup.body.find_all('img')
    other_pics = [x
                  for x in other_pics
                  if x.parent.name == 'p']
    if other_pics:
        for other_pic in other_pics:
            other_cap = other_pic.get_text()
            other_url = other_pic['src']
            articleJSON['pictures'].append([other_url, other_cap])

    articles = soup.body.find_all('article')
    raw_text = [x
                for x in articles[0].find_all('p', class_ = '', lang='', dir='')
                if x.get_text() != ''][1:-1]
    #this removes the author blurbs and blank <p>s
    #get the body links and pics
    text = []
    for para in raw_text:
        text.append(para.get_text().strip())
        #links
        if para.find_all('a'):
            for link in para.find_all('a'):
                url = link['href']
                link_text = link.get_text().strip()
                articleJSON['links'].append([url, link_text])
        #pictures
        if para.find_all('img'):
            for pic in para.find_all('img'):
                pic_url = pic['src']
                pic_caption = pic.get_text().strip()
                articleJSON['pictures'].append([pic_url, pic_caption])

    articleJSON['body'] = " ".join(text)
    articleJSON['tweets'] = getTweets(soup)
    #just FB comments
    """
    The Occupy Democrats robot.txt makes no mention of rate-limiting,
    so we'll just use the default.
    """
    time.sleep(30)
    return articleJSON

def scrapeCNN(webpage):
    """scrapes important info from CNN articles"""
    articleJSON, page = createPage(webpage)
    soup = BeautifulSoup(page, 'lxml')

    raw_text = soup.body.find_all(class_ = 'zn-body__paragraph')
    pictures = []
    metas = soup.find_all('meta')
    for meta in metas:
        if meta:
            if 'content' in meta.attrs.keys():
                try:
                    if (meta['content'][:7] == 'http://'
                            and meta['content'][-4:] == '.jpg'):
                        pictures.append(meta['content'])
                except:
                    print "bad url!"
    #AFAIK cnn doesn't have captions on its vids
    articleJSON['pictures'] = [(pic, '') for pic in set(pictures)]
    #now get the links
    links = []
    text = []
    for para in raw_text:
        if para.get_text():
            text.append(para.get_text().strip())
        if para.find_all('a'):
            for link in para.find_all('a'):
                url = link['href']
                link_text = link.get_text().strip()
                links.append([url, link_text])
    #get the tweets, just the URLS
    articleJSON['tweets'] = getTweets(soup)
    articleJSON['body'] = " ".join(text)
    articleJSON['links'] = links
    #no comments
    """
    The robots.txt for CNN makes no mention of rate-limiting, so 
    let's just use the default value. The Terms of Service make no
    mention of it.
    """
    time.sleep(30)
    return articleJSON

def scrapeFreedom(webpage):
    """scrapes articles on Freedom Daily website"""
    articleJSON, page = createPage(webpage)
    soup = BeautifulSoup(page, 'lxml')
    text = []
    raw_text = soup.body.article.find_all('p')
    if raw_text:
        for para in soup.body.article.find_all('p'):
            #body text
            if para.get_text().strip():
                text.append(para.get_text().strip())
            #links
            if para.find_all('a'):
                for link in para.find_all('a'):
                    url = link['href']
                    link_text = link.get_text().strip()
                    articleJSON['links'].append([url, link_text])
    #get images
    images = soup.body.article.find_all('img')
    if images:
        for image in soup.body.article.find_all('img'):
            image_url = image.get('src', '')
            image_caption = image.get('title', '')
            articleJSON['pictures'].append([image_url, image_caption])

    articleJSON['tweets'] = getTweets(soup)
    articleJSON['body'] = " ".join(text)
    #just FB comments
    """
    The robots.txt for Freedom Daily makes no mention of
    rate-limiting, so let's just use the default.
    """
    time.sleep(30)
    return articleJSON

def scrape98(webpage):
    """scrapes The Other 98% pages"""
    #there are 12 Occupy Democrat articles in here, so we can just use the
    #function we already made. then there are around 75 facebook links,
    #which are just photos or videos. the actual articles are mainly
    #usuncut.com, so should make a scraper for that.

    #first take care of Occupy articles
    if 'http://occupydemocrats.com' in webpage:
        return scrapeOccupy(webpage)
    elif 'http://usuncut.com' in webpage:
        return scrapeUncut(webpage)
    else:   #facebook links, other stuff.
        return {}

def scrapeUncut(webpage):
    """scrapes the US Uncut links found in the 98% articles"""
    # this site is down??
    return {}

def scrapeABC(webpage):
    """scrape ABC News articles"""
    articleJSON, page = createPage(webpage)
    text = []
    if page:
        #check for redirect here
        if page.geturl() != "http://abcnews.go.com":
            soup = BeautifulSoup(page, 'lxml')
            raw_text = soup.body.find_all('p', itemprop = 'articleBody')
            for para in raw_text:
                if para.get_text().strip():
                    text.append(para.get_text().strip())
                #get links
                links = para.find_all('a')
                if links:
                    for link in links:
                        link_url = link.get('href', '')
                        link_text = link.get_text()
                        articleJSON['links'].append([link_url, link_text])
        pics = soup.body.find_all('picture')
        for pic in pics:
            picture = pic.find('img')
            articleJSON['pictures'].append([picture.get('src', '').strip(), picture.get('alt', '').strip()])
        articleJSON['tweets'] = getTweets(soup)
        articleJSON['body'] = " ".join(text)
        #just Disqus comments
        articleJSON['DisqComm'] = getDisqComments(webpage, 'abcnewsdotcom')
    """
    The robots.txt makes no mention of rate-limiting, so we'll use the default.
    Terms of Service makes no mention either.
    """
    time.sleep(30)
    return articleJSON


def getTweets(soup):
    """scrapes the embedded tweets on pages. they seem to be the same format on
    the different websites. takes a soup object in and gives back a list of
    tweet urls"""
    article_tweets = []
    tweets = soup.body.find_all('blockquote', class_ = 'twitter-tweet')
    if tweets:
        for tweet in tweets:
            tweet_urls = tweet.find_all('a')
            temp = [tweet['href'] for tweet in tweet_urls]
            real_urls = filter(lambda x: True if 'status' in x else False,
                                  temp)
            article_tweets.extend(real_urls)

    return article_tweets

def createPage(webpage):
    """given a _webpage_ will set up the right environment and then opens and
    returns the page using urllib2"""
    articleJSON = {
                   "body" : "",
                   "pictures" : [],
                   "links" : [],
                   "tweets" : [],
                   "comments" : [],
                   "DisqComm" : []  #keep the Disqus comments separate
                  }
    page = openPage(webpage)
    return articleJSON, page

def openPage(webpage):
    """given a webpage, opens the page in Python and returns it"""
    #to avoid 403 errors, need to make the request as a browser
    web_response = None
    hdr = {'User-agent' : 'Mozilla/5.0'}
    req = urllib2.Request(webpage, headers=hdr)
    #open the page, try to catch all exceptions
    try:
        web_response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print e.fp.read()
    except urllib2.URLError, e:
        #print e.fp.read()
        print "URL ERROR ", wepage
    except httplib.HTTPException, e:
        #print e.fp.read()
        print "HTTP EXCEPTION ", webpage
    except Exception, e:
        print "other exception loading the page: ", webpage

    return web_response

def createCommentsURL(webpage, APP_ID, APP_SECRET):
    """some of the articles have embedded facebook comments. this will create
    the correct URL to grab these comments in JSON form"""
    #to scrape fb comments on other urls first need to find the ID number
    #assigned to the page by fb
    ID_URL = 'https://graph.facebook.com/?ids='
    url = ID_URL + webpage
    web_response = openPage(url)
    if web_response:
        readable_page = web_response.read()
    else:
        return None
    try:
        data = json.loads(readable_page)
    except:
        print "problem loading comment json"
        return None

    try:
        #the graph API requires an ID number to access comments
        ID_NUM = data[webpage]['og_object']['id']

        comments_args = "/comments?access_token=" + APP_ID + "|" + APP_SECRET + \
                            "&filter=stream"
        comments_url = ("https://graph.facebook.com/v2.10/" +
                            ID_NUM + comments_args)
    except:
        print "problem assigning fb comments URL"
        comments_url = ""
    return comments_url

def getComments(webpage, n = 1):
    """fetches the embedded facebook plugin comments for the article at
    _webpage_. returns the data in a JSON. can't use the collectPosts version
    because that only works for facebook posts."""
    comments_url = createCommentsURL(webpage, APP_ID, APP_SECRET)
    data = []

    if comments_url:
        time.sleep(n)
        web_response = openPage(comments_url)
        if web_response:
            readable_page = web_response.read()
        else:
            return {}
        try:
            thisdata = json.loads(readable_page)
            data.extend(thisdata['data'])
        except:
            print "loading comment didn't work"

        if 'paging' in thisdata.keys():
            while thisdata['paging'].get('next', False):
                try:
                    time.sleep(n)
                    web_response = urllib2.urlopen(thisdata['paging']['next'])
                    if web_response:
                        thisdata = json.loads(web_response.read())
                    if thisdata['data']:
                        data.extend(thisdata['data'])
                except:
                    print "problem getting extra batches"
    return data

def createDisqURL(webpage, DISQUS_ID, DISQUS_SECRET, forum):
    """some of the articles have embedded disqus comments. this will create the
    correct URL to make API requests"""
    try:
        if forum == 'abcnewsdotcom':
            _, page = createPage(webpage)   #take care of redirects
            url = page.geturl()
            page = openPage(url)
            soup = BeautifulSoup(page)
            ID = soup.body.find('article')['data-id']   #get the ID of the article

            split = re.split('/', url[7:])   #need to reformat the link
            webpage = 'http://' + split[0] + '/' + split[1] + '/story?id=' + ID


        args = '&thread=link:' + webpage + '&forum=' + forum
        comments_url = ('https://disqus.com/api/3.0/threads/listPosts.json?api_key=' +
                            DISQUS_ID + '&api_secret=' + DISQUS_SECRET + args)
    except:
        print "problem creating Disqus URL"
        comments_url = ""
    return comments_url

def getDisqComments(webpage, forum, n = 1):
    """makes the requests to get the Disqus comments for a given _webpage_,
    also requires the _forum_ name for the page as per the API"""
    comments_url = createDisqURL(webpage, DISQUS_ID, DISQUS_SECRET, forum)
    data = []
    if comments_url:
        time.sleep(n)
        web_response = openPage(comments_url)
        if web_response:
            readable_page = web_response.read()
        else:
            return {}
        try:
            thisdata = json.loads(readable_page)
            data.extend(thisdata['response'])
        except:
            print "loading comments didn't work"
            return {}

        if 'cursor' in thisdata.keys():
            while thisdata['cursor']['hasNext']:
                """
                I'm not 100% sure what the rate limit is for the Disqus API,
                can't find it in the documentation. To be safe, just use the
                same rate we've been using for the facebook comments.
                """
                time.sleep(n)
                next_cursor = thisdata['cursor']['next']
                extra_comments_url = comments_url + '&cursor=' + next_cursor
                try:
                    web_response = openPage(extra_comments_url)
                except:
                    print "web response"
                    continue
                try:
                    readable_page = web_response.read()
                except:
                    print "readable page"
                    continue
                try:
                    thisdata = json.loads(readable_page)
                    if thisdata.get('response', False):
                        data.extend(thisdata['response'])
                except:
                    print "json load?"
                    continue

    return data

def outlet_scrape(outlet):
    """given an _outlet_ will scrape all articles contained in that folder"""
    outletDict = {
                  "Politico" : scrapePolitico,
                  "CNN_Politics" : scrapeCNN,
                  "Right_Wing_News" : scrapeRightWing,
                  "Occupy_Democrats" : scrapeOccupy,
                  "Eagle_Rising" : scrapeEagle,
                  "Addicting_Info" : scrapeAddicting,
                  "Freedom_Daily" : scrapeFreedom,
                  "The_Other_98%" : scrape98,
                  "ABC_News_Politics" : scrapeABC
                  }
    path = './dataset/' + outlet + '/'

    files = glob.glob(path + '*/posts.json')
    num = len(files)
    for i, filename in enumerate(files):
        print "working on: " + filename
        print str(i + 1) + " / " + str(num)
        fileJSON = {}
        with open(filename, 'r') as f:
            postJson = json.load(f)

        if "link" not in postJson.keys():
            print "no link!", filename
            continue    #if the link is missing, skip
        if "type" not in postJson.keys():
            print "no type! ", filename
        #for now just skip video and pic posts
        if postJson.get('type') == 'video':
            fileJSON = {
                        "body" : postJson.get('message', ''),
                        "links" : [postJson.get('source', ''), ''],
                        "pictures" : [postJson.get('picture', ''), postJson.get('name', '')]
                       }
        elif postJson.get('type') == 'photo':
            fileJSON = {
                        "body" : '',
                        "links" : [postJson.get('link', ''), postJson.get('story', '')],
                        "pictures" : [postJson.get('picture', ''), postJson.get('name', '')]
                       }
        else:
            #if the post is an article, scrape it
            if 'link' not in postJson.keys():
                print "no link!"
                continue
            webpage = postJson["link"]
            if outlet == "The_Other_98%":
                #The Other 98% seems to have NO first party articles, so handle
                #this case separately
                try:
                    fileJSON = scrape98(webpage)
                except:
                    print "scraping didn't work! ", webpage
                fileJSON['comments'] = getComments(webpage)

            else:
                #these scrapers are only useful for first party articles
                if postJson["first_party"]:
                    try:
                        fileJSON = outletDict[outlet](webpage)
                    except:
                        print "scraping didn't work! ", webpage
                    fileJSON['comments'] = getComments(webpage)


        #chop off the posts.json of the filename and add scraped.json
        new_filename = filename[:-10] + 'scraped.json'
        #now dump the scraped JSONs in the same folder
        with open(new_filename, 'w') as f2:
            json.dump(fileJSON, f2, indent = 4, sort_keys = True)

if __name__ == '__main__':
    outlets = ['ABC_News_Politics',
               'Addicting_Info',
               'CNN_Politics',
               'Eagle_Rising',
               'Freedom_Daily',
               'Occupy_Democrats',
               'Politico',
               'Right_Wing_News',
                'The_Other_98%']
    for outlet in outlets:
        if os.path.isdir('./dataset/' + outlet):
            outlet_scrape(outlet)


