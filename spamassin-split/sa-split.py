#!/usr/bin/python
import sys;
import re;
import os;
import csv;
import argparse
from functools import reduce
# Parsing
parser = argparse.ArgumentParser(description="Extract and Simulate SpamAssassin scores")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-e', '--extract', action='store_true',help='Extracts scores from an EML file' )
group.add_argument('-s', '--simulate', action='store_true', help='Compares score from an EML file and a new scoring table') 
group.add_argument('-c', '--chart', action='store_true',help='Add existing scores to a CSV file for modification' )
parser.add_argument('-f', '--file', action='store', help='EML source file',required=True) 
parser.add_argument('-r', '--reference', action='store', help='Reference CSV scores file') 
parser.add_argument('-b', '--bar', action='store', help='Spam limit (>= means spam)') 
parser.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity') 
args = parser.parse_args()
class bcolors:
    FAIL = '\033[31m'
    ENDC = '\033[0m'

# Main class
class Scores:

    def getCompareDicts( self, refsFilename, sourceFilename ):
        tuples = self.getSourcesScores( sourceFilename )
        fileDict = dict((key, value) for (key, value) in tuples)
 
        handle = open(refsFilename, 'a+')
        reader = csv.reader( handle, dialect='excel')
        refDict = dict((key, value) for (key, value) in reader)

        return [ fileDict, refDict ]

    def compare( self, refsFilename, sourceFilename, bar = 7.0):
        fileDict, refDict = self.getCompareDicts( refsFilename, sourceFilename )
        fileSum = self.getSum( fileDict )
        simulSum = 0.0
        for key in fileDict:
            if not( key in refDict ):
                print "woah. No " + key + " in reference..."
                continue
            simulSum += float( refDict[key])
        color = bcolors.FAIL if simulSum >= bar else bcolors.ENDC
        print(color + "{0:.40s}    before:{1:.1f}     after:{2:.1f}".format(sourceFilename,fileSum,simulSum)+bcolors.ENDC)


    def setChartCsv( self, refsFilename, sourceFilename):

        fileDict, refDict = self.getCompareDicts( refsFilename, sourceFilename )
        handle = open(refsFilename, 'a+')
        writer = csv.writer( handle, dialect='excel')
        for key in fileDict:
            if not( key in refDict ):
                refDict[key] = fileDict[key]
                writer.writerow( [ key.strip(), fileDict[key] ]) 

            
    def getSourcesScores( self, sourceFilename ):
        output = []
        if not ( os.path.isfile( sourceFilename ) ) :
                print "Not a file: '"+ sourceFilename +"'"
                exit(1)
        with open( sourceFilename ) as fileHandle :
            result = []
            found = False
            linesList = fileHandle.readlines()
            for line in linesList:
                if found == False:
                    if( re.match( "^X-Spam-Status", line ) ):
                        found = True
                        continue
                else:
                    if not( re.match( "^\s", line ) ):
                        break
                    result.append(line)
        resultString = "".join( result ).replace("\r","").replace("\n","")
        scoresRegExp = re.match("^.*?\[(.*)\].*$",resultString)
        if( '' == resultString ):
            print "No tag in '"+sourceFilename+"'"
            exit(1)
        if( None == scoresRegExp ):
            print "Failed to parse '" + resultString +"' in file '"+ sourceFilename +"'"
            exit(1)
        scoresList = re.split(r',',scoresRegExp.groups()[0])
        for score in scoresList:
            tuples = re.split( r'=',score.replace(' ','') )
	    tuples[0] = tuples[0].strip("\t ")
            output.append( tuples )
        return output


    def getDestFilename( self, sourceFilename ):
        destDir = os.path.abspath(os.path.dirname(sourceFilename) + "/../csv")
        if not( os.path.isdir( destDir ) ):
            os.makedirs( destDir )
        destFilename = destDir + "/" + os.path.basename(sourceFilename) + ".csv"
        return destFilename


    def writeCsv( self, sourceFilename, scoresList ):
        destFilename = self.getDestFilename( sourceFilename )
        handle = open(destFilename, 'wb')
        writer = csv.writer( handle, dialect='excel')
        for tuples in scoresList :
            writer.writerow(tuples)


    def getScoresFromCsv( self, sourceFilename ):
        destFilename = self.getDestFilename( sourceFilename )
        handle = open(destFilename, 'r')
        reader = csv.reader( handle, dialect='excel')
        return reader


    def getSum( self, scoresDict ):
        total = 0
        for name in scoresDict :
            total += float(scoresDict[ name ])
        return total


instance = Scores()
sourceFilename = args.file
if( args.extract ):
    scoresList = instance.getSourcesScores( sourceFilename )
    destFilename = instance.getDestFilename( sourceFilename )
    instance.writeCsv( destFilename, scoresList )
    if args.verbose: print "Wrote to "+destFilename
elif( args.chart ):
    referenceFilename = args.reference
    instance.setChartCsv( referenceFilename, sourceFilename )
else:
    referenceFilename = args.reference
    bar = args.bar if args.bar != None  else 7.0
    instance.compare( referenceFilename, sourceFilename, float(bar))


