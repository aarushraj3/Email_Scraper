import email_crawler
import csv
import os.path
path = []
directory = './'#change directory
for filename in os.listdir(directory):
	if filename.endswith("web_address2.csv"):#enter file name
		x = os.path.join(directory, filename)
		path.append(x)
print path


for file in path:
	with open(file, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		#print enumerate(reader)
		for c,row in enumerate(reader):
			if c > 842:#no. of entries already crawled
				if len(row[0]) <5:
					email_crawler.crawl(row[1][:-13],row[1])
				else:
					email_crawler.crawl(row[0],row[1])
#email_crawler.crawl("NIT wikipedia","PESU")