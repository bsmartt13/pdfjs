import sys, plotter
from peepdf.PDFCore import *

'''---------------------------------------------------------------------------------------------------------+
| pdfjs: A PDF javascript analyzer																			|
| 		- Dump javascript from a PDF to txt file															|
|		- Identify obfuscated functions																		|
|																											|
|		Usage:																								|
|			python pdfjs.py <pdf_file> <prefix_for_js_dumps>												|
|			prefix_for_js_dumps: javascript objects and streams will be dumped to individual files			|
|			If the prefix supplied is abc and the pdf has 4 js objects they will be written to				|
|				abc1.txt abc2.txt abc3.txt abc4.txt															|
|			The file suspicious																				|
|			 																								|
|		Prerequisites:																						|
|			You will need peepdf from http://eternal-todo.com/tools/peepdf-pdf-analysis-tool				|
+---------------------------------------------------------------------------------------------------------'''

class pdfjs():
	
	# init()
	# fromPDF:  True for anaylzing JS code inside a PDF file.
	# 			False for analyzing JS code inside a .js file.
	
	def __init__(self, inFile, outFile, fromPDF):
		self.pdfFileName = inFile
		self.outputFileName = outFile
		if fromPDF == True:
			self.pdfParser = PDFParser()
			self.ret,self.pdf = self.pdfParser.parse(self.pdfFileName, True, True)
			self.statsDict = self.pdf.getStats()
		self.JSObjects = [] # only used if fromPDF.
		self.JSPayloads = []
		return
	
	'''
	getJSObjects: strip from the PDFFile class the values from pdf.body[ver]['Objects with JS code'].
	'''
	def getJSObjects(self):
		for ver in range(len(self.statsDict['Versions'])):
			statsVersion = self.statsDict['Versions'][ver]
			if statsVersion['Objects with JS code'] != None:
				for j in statsVersion['Objects with JS code'][1]:
					if self.pdf.body[ver].getObject(j) == None:
						continue
					self.JSObjects.append(self.pdf.body[ver].getObject(j))
		return
	
	'''
	getJSPayloads: iterate over all objects/streams we found in getJSObjects and get raw/decoded payloads.
	'''
	def getJSPayloads(self):
		count = 0
		for obj in self.JSObjects:
			if isinstance(obj, PDFStream):
				print "[+] found filtered stream with JS code"
				self.JSPayloads.append(obj.decodedStream) # need filter decoded stream, use obj.decodedStream
				count = count + 1
				continue
			keys = obj.elements.keys()
			vals = obj.elements.values()
			for k in obj.elements.iterkeys():
				valueElement = obj.elements[k]
				if valueElement.containsJS():
					print "[+] found object with JS code"
					self.JSPayloads.append(valueElement.rawValue)
					count = count + 1
		print "[*] found " + str(count) + " JS payloads."
		return
			
	'''
	dump(): write all payloads to file
		return number of payloads written to file
	'''	
	def dump(self):
		filenum = 1 # used for generating names.
		suffix = ".txt"
		for payload in self.JSPayloads:
			nextFileName = self.outputFileName + str(filenum) + suffix
			try:
				outputFile = open(nextFileName, 'w')
			except:
				print "[x] couldn't open output file " + nextFileName + " for writing."
			else: # experimental sanitize escaped chars before writing to file.
				payload = self.cleanupPayload(payload)
				outputFile.write(payload)
				print "[+] wrote payload " + str(filenum) + " to file " + self.outputFileName
				outputFile.close()
				filenum += 1
		return (filenum - 1)

	def cleanupPayload(self,payload):
		payload = payload.replace("\\(", "(")
		payload = payload.replace("\\)", ")")
		payload = payload.replace("\\r", "\r")
		payload = payload.replace("\\n", "\n")
		return payload

	'''
	analyzePayload(): runs statistical analysis on a single paylaod.
		return a string about the outliers.
	'''
	def analyzePayload(self, payload):
		print "Running statistical analysis on payloads."
		plot = plotter.GraphMe()
		plot.process(payload)
		s = plot.calcOutlier()
		return s

	'''
	runAnalyis(): runs analyzePayload() on all payloads, write results to file.
	'''
	def runAnalysis(self):
		filenum = 1
		for payload in self.JSPayloads:
			s = self.analyzePayload(self.cleanupPayload(payload))
			if "Non-suspicious" in s:
				filename = "non-suspicious_" + self.outputFileName + ".txt"
			else:
				filename = "suspicious_" + self.outputFileName + ".txt"
			try:
				outputFile = open("testresults/"+filename,'w')
			except:
				print "couln't open output file `" + filename + "` for writing."
				return
			outputFile.write("Results for (output)file_" + str(filenum) + ":\n")
			outputFile.write(s+"\n")
		print "done writing statistical analysis results to file."
		outputFile.close()
		return

''' END class pdfjs '''

'''
	driver function
'''
def main():
	if len(sys.argv) < 2:
		print "Usage: python pdfjs.py <suspicious.pdf> <prefix>"
		print "depending on how many JS Objects the PDF contains, output is written to <prefix>1.txt, <prefix>2.txt, ..., <prefix>N.txt"
		print "Obfuscated functions are identified and the results of this analysis are written to the file suspicious_<prefix>.txt"
		sys.exit(0)
	else:
		dumper = pdfjs(sys.argv[1], sys.argv[2], True)
		dumper.getJSObjects()
		dumper.getJSPayloads()
		payload_count = dumper.dump()
		if payload_count > 0:
			dumper.runAnalysis()
	sys.exit(0)

if __name__ == "__main__":
	main()




