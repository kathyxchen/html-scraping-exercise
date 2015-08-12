import urllib2
import argparse
import re
BASE_URL = 'http://www.yelp.com/biz/'
DEFAULT_LOCATION = 'new-york'
DEFAULT_BUSINESS = 'saigon-shack'
DEFAULT_Q = 'pho'
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', '--business', dest='business', default=DEFAULT_BUSINESS, type=str, help='Search for this Business ID (default: %(default)s)')
	parser.add_argument('-l', '--loc', dest='loc', default=DEFAULT_LOCATION, type=str, help='Search in this location (default: %(default)s)')
	parser.add_argument('-q', '--q', dest='q', default=DEFAULT_Q, type=str, help='Query (default: %(default)s)')
	values = parser.parse_args()
	q = values.q
	starting_url = BASE_URL + values.business + '-' + values.loc
	fst_page = starting_url + '?q=' + q
	print fst_page
	page = urllib2.urlopen(fst_page)
	html = page.read()
	found = html.find(' reviews mentioning') - 1
	check_num = html[found]
	total_reviews = ""
	while check_num.isdigit():
		total_reviews = check_num + total_reviews
		found -= 1
		check_num = html[found]

	pages = (int(total_reviews) / 40) + 1
	total_ratings = 0
	count = 0
	
	for i in range(0, pages):
		start = 'start=' + str(i * 40)
		whole_url = starting_url + '?' + start + '&q=' + q
		whole_page = urllib2.urlopen(whole_url)
		whole_html = whole_page.read()
		start_here = whole_html.find('Recommended Reviews')
		stop_here = whole_html.find('not currently recommended')
		whole_html = whole_html[start_here:stop_here]
		indices = [w.start() for w in re.finditer('.0 star rating">', whole_html)]
		
		for pos in indices:
			rating = whole_html[pos-1]
			count += 1
			total_ratings += int(rating)
	avg_rating = float(total_ratings) / count
	print str(count) + " reviews mention " + q + " with average rating " + str(avg_rating) 
if __name__ == '__main__':
	main()