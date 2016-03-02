import urllib2
import json
from datetime import datetime
from time import sleep

#opening log file
feedcsv = open('feed.csv', 'w')

feeds = dict(huffingtonpost = 'http://www.huffingtonpost.com/feeds/verticals/politics/news.xml',
        washingtonpost = 'http://feeds.washingtonpost.com/rss/politics',
        nytimes = 'http://rss.nytimes.com/services/xml/rss/nyt/Politics.xml',
        politico = 'http://www.politico.com/rss/politicopicks.xml',
        cnn = 'http://rss.cnn.com/rss/cnn_allpolitics.rss',
        npr = 'http://www.npr.org/rss/rss.php',
        csmonitor = 'http://rss.csmonitor.com/feeds/csm',
        wsj = 'http://online.wsj.com/xml/rss/3_7085.xml',
        fox ='http://feeds.foxnews.com/foxnews/latest',
        washingtontimes = 'http://www.washingtontimes.com/rss/headlines/news/national/',
        theblaze = 'http://www.theblaze.com/stories/feed/',
        newsmax = 'http://www.newsmax.com/rss/Newsfront/16.xml')

baseurl = 'https://ajax.googleapis.com/ajax/services/feed/load?v=1.0&q='

for f in feeds:
	csv = open(f+'.csv', 'w')
	u = urllib2.urlopen(baseurl+feeds[f])
	b = u.read()
	j = json.loads(b)
	csv.write(json.dumps(j, sort_keys = True, indent = 4))
	csv.close
