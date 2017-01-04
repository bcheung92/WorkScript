#!/usr/bin/env python
import sys
import re
import os
inFilename = sys.argv[1]
if os.path.isfile(inFilename):
	namelength = inFilename.rfind(".")
	name = inFilename[0:namelength]
	exten = inFilename[namelength:]
	outFilename = name+"-cachecmp3"+exten

print "inFilename:", inFilename
print "outFilename:", outFilename

fpRead = open(inFilename, "r")
fpWrite = open(outFilename, "w+")

dtbwalker1Pattern = re.compile(r'.*(l2.overall_hits::switch_cpus0.dtb.walker).* ([0-9]+)')
dtbwalker2Pattern = re.compile(r'.*(l2.overall_hits::switch_cpus1.dtb.walker).* ([0-9]+)')
itbwalker1Pattern = re.compile(r'.*(l2.overall_hits::switch_cpus0.itb.walker).* ([0-9]+)')
itbwalker2Pattern = re.compile(r'.*(l2.overall_hits::switch_cpus1.itb.walker).* ([0-9]+)')
overallhitsPattern = re.compile(r'.*(l2.overall_hits::total).* ([0-9]+)')
cachehitsPattern = re.compile(r'.*(l2.cachehits).* ([0-9]+)')
threadbeginPattern = re.compile(r'.*Begin Simulation Statistics.*')
threadendPattern =re.compile(r'.*End Simulation Statistics.*')
lines = fpRead.readline()

while lines:
	threadbeginmatch = threadbeginPattern.match(lines)
	if threadbeginmatch:
		dtbwalker1=0
		itbwalker1=0
		dtbwalker2=0
		itbwalker2=0
		overallhits=0
		cachehits=0
		gem5hits=0
                ratio0 = 0
                ratio1 = 0
		threadlines = fpRead.readline()
		while threadlines:
	                dtbwalker1match = dtbwalker1Pattern.search(threadlines)
	                itbwalker1match = itbwalker1Pattern.search(threadlines)
	                dtbwalker2match = dtbwalker2Pattern.search(threadlines)
	                itbwalker2match = itbwalker2Pattern.search(threadlines)
	                overallhitsmatch = overallhitsPattern.search(threadlines)
        	        cachehitsmatch = cachehitsPattern.search(threadlines)
	                threadendmatch = threadendPattern.match(threadlines)
			if dtbwalker1match:
				dtbwalker1=int(dtbwalker1match.group(2))
			if itbwalker1match:
				itbwalker1=int(itbwalker1match.group(2))
			if dtbwalker2match:
				dtbwalker2=int(dtbwalker2match.group(2))
			if itbwalker2match:
				itbwalker2=int(itbwalker2match.group(2))
			if overallhitsmatch:
				overallhits=int(overallhitsmatch.group(2))
			if cachehitsmatch:
				cachehits=int(cachehitsmatch.group(2))
			if threadendmatch:
				gem5hits=overallhits-(dtbwalker1+dtbwalker2+itbwalker1+itbwalker2)
                                absval0 = abs(overallhits-cachehits)
                                absval1 = abs(gem5hits-cachehits)
                                if overallhits!=0:
                                    ratio0=(absval0/float(overallhits))*100
                                else:
                                    ratio0=float(0)
                                if gem5hits!=0:
                                    ratio1=(absval1/float(gem5hits))*100
                                else:
                                    ratio=float(0)
				fpWrite.write("overallhits  %d   " % overallhits)
				fpWrite.write("cachehits  %d   " % cachehits)
                                fpWrite.write("ratio0 %.2f%%   " % ratio0)
                                fpWrite.write("ratio1 %.2f%%" % ratio1)
				fpWrite.write("\n")
				break
                        threadlines = fpRead.readline()
        lines = fpRead.readline()
fpRead.close()
fpWrite.close()
