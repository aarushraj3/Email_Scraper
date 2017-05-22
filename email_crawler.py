from settings import LOGGING
import logging, logging.config
import urllib, urllib2
import re, urlparse
import traceback
from database import CrawlerDb
import os
import sys

def find_emails_in_html(html):
	if (html == None):
		return set()
	email_set = set()
	for email in email_regex.findall(html):
		email_set.add(email)
	return email_set

def internet_on():
    for timeout in [1,5,10,15]:
        try:
            response=urllib2.urlopen('http://google.com',timeout=timeout)
            return True
        except urllib2.URLError as err: pass
    return False

def retrieve_html(url):
	"""
	Crawl a website, and returns the whole html as an ascii string.

	On any error, return.
	"""

	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Just-Crawling 0.1')
	request = None
	status = 0
	try:
		
		if url.endswith('jpg') or url.endswith('jpeg') or url.endswith('png') or url.endswith('pdf') or 'wikipedia.org' in url:
			return
		request = urllib2.urlopen(req)
	except urllib2.URLError, e:
		logger.error("Exception at url: %s\n%s" % (url, e))
	except urllib2.HTTPError, e:
		status = e.code
	except Exception, e:
		return
	if status == 0:
		status = 200

	try:
		data = request.read()
	except Exception, e:
		return
	logger.info("Crawling %s" % url)
	return str(data)


def write(name,db):

	try:
		# Get all the emails and save in a CSV
		EMAILS_FILENAME='data/output/'+name+'.csv'
		logger.info("="*40)
		logger.info("Processing...")
		emails = db.get_all_emails()
		logger.info("There are %d emails" % len(emails))
		file = open(EMAILS_FILENAME, "w+")
		file.writelines("\n".join(emails))
		file.close()
		logger.info("All emails saved to ./data/output/*.csv")
		logger.info("="*40)
		os.remove("./data/crawler.sqlite")

	except KeyboardInterrupt:
		logger.error("Stopping (KeyboardInterrupt)")
		sys.exit()
	except Exception, e:
		logger.error("EXCEPTION: %s " % e)
		traceback.print_exc()




#***********************************************************
#***********************************************************



# Debugging
# import pdb;pdb.set_trace()

# Logging
logging.config.dictConfig(LOGGING)
logger = logging.getLogger("crawler_logger")

google_adurl_regex = re.compile('adurl=(.*?)"')
google_url_regex = re.compile('url\?q=(.*?)&amp;sa=')
email_regex = re.compile('([A-Z0-9._%+-]+\(?@\)?[A-Z0-9.-]+\(?\.\)?[A-Z]{2,4})', re.IGNORECASE)
url_regex = re.compile('<a\s.*?href=[\'"](.*?)[\'"].*?>')
# Below url_regex will run into 'Castrophic Backtracking'!
# http://stackoverflow.com/questions/8010005/python-re-infinite-execution
# url_regex = re.compile('<a\s(?:.*?\s)*?href=[\'"](.*?)[\'"].*?>')

# Maximum number of search results to start the crawl
MAX_SEARCH_RESULTS = 1

# Set up the database



def crawl(keywords,name):
	"""
	This method will

	1) Google the keywords, and extract MAX_SEARCH_RESULTS
	2) For every result (aka website), crawl the website 2 levels deep.
		That is the homepage (level 1) and all it's links (level 2) and all it's link's links (level 3).
	3) Store the html in /data/html/ and update the database of the crawled emails

	crawl(keywords):
		Extract Google search results and put all in database
		Process each search result, the webpage:
			Crawl webpage level 1, the homepage
			Crawl webpage level 2, a link away from the homepage
			Crawl webpage level 3, a link away from the homepage
			Update all crawled page in database, with has_crawled = True immediately
			Store the HTML
	"""
	if internet_on() == False:
		print "*******************NO INTERNET CONNECTION*******************"
		sys.exit(0)

	db = CrawlerDb()
	db.connect()
	logger.info("-"*40)
	logger.info("Keywords to Google for: %s" % keywords)
	logger.info("-"*40)

	# Step 1: Crawl Google Page
	# eg http://www.google.com/search?q=singapore+web+development&start=0
	# Next page: https://www.google.com/search?q=singapore+web+development&start=10
	# Google search results are paged with 10 urls each. There are also adurls
	for page_index in range(0, MAX_SEARCH_RESULTS, 10):
		query = {'q': keywords}
		url = 'http://www.google.com/search?' + urllib.urlencode(query) + '&start=' + str(page_index)
		data = retrieve_html(url)
		# 	print("data: \n%s" % data)
		for url in google_url_regex.findall(data):
			db.enqueue(url)
			break



	# Step 2: Crawl each of the search result
	# We search till level 2 deep
	while (True):
		# Dequeue an uncrawled webpage from db
		uncrawled = db.dequeue()
		if (uncrawled == False):
			break
		email_set = find_emails_3_level_deep(uncrawled.url,db)
		if (len(email_set) > 0):
			db.crawled(uncrawled, ",".join(list(email_set)))
		else:
			db.crawled(uncrawled, None)
	write(name,db)




def find_emails_3_level_deep(url,db):

	html = retrieve_html(url)
	email_set = find_emails_in_html(html)
	
	link_set = find_links_in_html_with_same_hostname(url, html)
	temp_link_set = find_links_in_html_with_same_hostname(url, html)
	

	#uncomment below for 3 level crawling
	'''for link in temp_link_set:
		html=html = retrieve_html(link)
		link_set.update(find_links_in_html_with_same_hostname(link, html))'''



	for link in link_set:
		# Crawl them right away!
		# Enqueue them too
		html = retrieve_html(link)
		if (html == None):
			continue
		email_set.update(find_emails_in_html(html))
		db.enqueue(link, list(email_set))

	# We return an empty set
	return set()






def find_links_in_html_with_same_hostname(url, html):
	"""
	Find all the links with same hostname as url
	"""
	if (html == None):
		return set()
	url = urlparse.urlparse(url)
	links = url_regex.findall(html)
	link_set = set()
	for link in links:
		if link == None:
			continue
		try:
			link = str(link)
			if link.startswith("/"):
				link_set.add('http://'+url.netloc+link)
			elif link.startswith("http") or link.startswith("https"):
				if (link.find(url.netloc)):
					link_set.add(link)
			elif link.startswith("#"):
				continue
			else:
				link_set.add(urlparse.urljoin(url.geturl(),link))
		except Exception, e:
			pass

	return link_set




