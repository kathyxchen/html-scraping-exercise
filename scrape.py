import urllib2
import argparse
import re
from multiprocessing import Pool, Queue
import sqlite3
import time 

BASE_URL = 'http://www.yelp.com/biz/'
DEFAULT_LOCATION = 'new-york'
DEFAULT_BUSINESS = 'saigon-shack'
DEFAULT_SEARCH = ''
DEFAULT_Q = 'pho'
conn = sqlite3.connect('cache.db')
c = conn.cursor()

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', '--business', dest='business', default=DEFAULT_BUSINESS, type=str, help='Search for this Business ID (default: %(default)s)')
	parser.add_argument('-l', '--loc', dest='loc', default=DEFAULT_LOCATION, type=str, help='Search in this location (default: %(default)s)')
	parser.add_argument('-q', '--q', dest='q', default=DEFAULT_Q, type=str, help='Query (default: %(default)s)')
	
	# this currently does not work. urllib does not process JS or CSS changes
	parser.add_argument('-u', '--url', dest='url', default=DEFAULT_SEARCH, type=str, help='Enter in a complete URL for search (default: %(default)s)')
	
	values = parser.parse_args()

	if (len(values.url) == 0):
		single_search(values.business, values.loc, values.q)
	else:
		html = read_html(values.url)
		print html
	conn.close()

def single_search(business, loc, query):
	starting_url = BASE_URL + business + '-' + loc
	query_page = starting_url + '?q=' + query
	print query_page
	num_reviews = get_num_reviews(query_page)
	check_cache(starting_url, business, loc, query, num_reviews)
	
def check_cache(starting_url, business, loc, query, num_reviews):
	data = (business, loc, query, num_reviews)
	c.execute('SELECT result FROM queries WHERE business = ? AND location = ? AND param = ? AND reviews = ?', data)
	result = c.fetchone()
	if result is None:
		pages = (int(num_reviews) / 40) + 1
		stats = calculate_avg_rating(starting_url, pages, query)
		insert_data = (business, loc, query, num_reviews, stats['avg'])
		c.execute('INSERT INTO queries (business, location, param, reviews, result) VALUES (?, ?, ?, ?, ?)', insert_data)
		conn.commit()
		print str(stats['total']) + ' reviews mention ' + query + ' with average rating ' + str(stats['avg'])
	else: 
		print num_reviews + ' reviews mention ' + query + ' with average rating ' + str(result[0]) 

	
def read_html(url):
	page = urllib2.urlopen(url)
	html = page.read()
	page.close()
	return html

def get_num_reviews(fst_page):
	html = read_html(fst_page)
	found = html.find(' reviews mentioning') - 1
	check_num = html[found]
	total_reviews = ''
	while check_num.isdigit():
		total_reviews = check_num + total_reviews
		found -= 1
		check_num = html[found]
	return total_reviews

def calculate_avg_rating(starting_url, pages, query):
	total_ratings = 0
	count = 0
	for i in range(0, pages):
		start = 'start=' + str(i * 40)
		whole_url = starting_url + '?' + start + '&q=' + query
		time.sleep(1)
		whole_html = read_html(whole_url)
		start_here = whole_html.find('Recommended Reviews')
		stop_here = whole_html.find('not currently recommended')
		whole_html = whole_html[start_here:stop_here]
		indices = [w.start() for w in re.finditer('.0 star rating">', whole_html)]
		
		for pos in indices:
			rating = whole_html[pos-1]
			count += 1
			total_ratings += int(rating)
	avg_rating = float(total_ratings) / count
	return {'total': count, 'avg': avg_rating }

if __name__ == '__main__':
	main()