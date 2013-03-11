## graphing library and statistical analysis of JS code
## created by alexander<dot>hanel<at>gmail<dot>com
## 2/21/2013
## No license, free game to use
## extended by Bill Smartt <bsmarttATalienvaultDOTcom>
## 3/6/13
## For the original code by alexander, see http://hooked-on-mnemonics.blogspot.com.es/2013/02/detecting-pdf-js-obfuscation-using.html

import sys
from StringIO import StringIO
import jsbeautifier

class GraphMe():
    def __init__(self):
        self.fullData = ''
        self.bjs = False
        self.PS = True
        self.plotData = []
        self.x = []
        self.y = []
        return

    def process(self,data):
        'disneyland'
        #if self.bjs == True:
            #data = self.beautifier(data)
        if type(data) is str:
            data = StringIO(data)
        self.fullData = data.readlines()
        # clean up JS that is all one line 
        #if len(self.fullData) == 1 or self.PS == True:
            #self.PS = False
            #self.bjs = True
            #data.seek(0)
            #self.process(data)
        for t in range(len(self.fullData)): self.x.append(t)
        for t in self.fullData : self.y.append(len(t))

    def calcMedian(self, values):
        if len(values) < 1:
            print "calcMedian() error calculating median of list len < 1."
            print "cowardly returning -1"
            return -1
        sortedValues = sorted(values)
        length = len(sortedValues)
        if not length % 2:
            return (sortedValues[length/2] + sortedValues[length/2-1]) / 2.0
        return sortedValues[length/2]

    def calcMean(self, values):
        if len(values) < 1:
            print "calcMean() error calculating mean of list len < 1."
            print "cowardly returning -1"
            return -1
        else:
            mean = float(sum(values))/len(values)
            return mean

    def calcOutlier(self):
        mean = self.calcMean(self.y)
        median = self.calcMedian(self.y)
        if mean/median > 2:
            s = "Obfuscation detected.\nSuspicious: mean %s median %s" % (mean, median)
            print s
            return s            
        else:
            s = "No obfuscation detected.\nNon-suspicious: mean %s median %s" % (mean, median)
            print s
            return s

    def beautifier(self, buffer):
        'clean up the JS'
        try:
            temp = jsbeautifier.beautify(buffer.read())
        except:
            print "ERROR: jsbeautifier"
            return buffer
        return temp