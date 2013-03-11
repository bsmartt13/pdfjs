import sys
import urllib2
from bs4 import BeautifulSoup as bs



def main():
	links = readURLList()
	for resource in links:
		print "next resource: %s" % resource
		try:
			response = urllib2.urlopen(resource)
		except urllib2.URLError as e:
			print e
			continue
		html = response.read()
		try:
			soup = bs(html)
		except:
			print "\nsoup error."
			continue
		for scriptTag in soup.findAll("script"):
			nexturl = scriptTag.get("src")
			if nexturl is None:
				continue
			if "http" in nexturl and nexturl.endswith(".js"):
				print "found a javascript file (external resource): " + str(nexturl)
				nextfilename = nexturl.replace("/", "_")
				try:
					nextresponse = urllib2.urlopen(nexturl)
					nextsourcecode = nextresponse.read()
				except:
					print "unable to open url: " + nexturl + "."
				try:
					nextf = open("store/"+nextfilename,'w')
					nextf.write(nextsourcecode)
					nextf.close()
					print "done writing file " + nextfilename + " to disk."
				except:
					print "unable to write js to file on disk (" + nextfilename + ")"
	return
		
def readURLList():
	if len(sys.argv < 2):
		print "Usage: `python getJS.py <input_file>"
		print "\t<input_file> should be a list of urls to parse, one per line."
		print "\tthe format of the urls should be `example.com`.\n\tNot `http://example.com`."
	links = []
	try:
		with open(sys.argv[1],'r') as f:
			content = f.readlines()
	except:
		print "unable to open resource: top10000.txt"
	for line in content:
		fullyqualified = "http://%s/" % (line.strip())
		print fullyqualified
		links.append(fullyqualified)
	return links
				
if __name__ == "__main__":
	main()