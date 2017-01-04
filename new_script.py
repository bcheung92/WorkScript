#!/usr/bin/env python

### this is the python script created by Ferris Cheung 2017-01-01
### It is used to get the shared Cache Reuse Distance Distribution which is added up by diff core's RDD-----L2R,and it's output as name-reuse.txt
### and it gets the shared Cache Stack Distance Distribution which is collected in the l2 cache port ----L2E,and it's output as name-stack.txt
import sys
import re
import os
###
### input file and output file define
###
inFilename = sys.argv[1]
if os.path.isfile(inFilename):
    namelength = inFilename.rfind(".")
    name = inFilename[0:namelength]
    exten = inFilename[namelength:]
    ReuseDH = name+"-reuse"+exten
    StackDH = name+"-stack"+exten

print "inFilename:", inFilename
print "outFilename:", ReuseDH,StackDH

#the input file
fpRead = open(inFilename, "r")
#the output file Reuse Distance Distribution
RDHWrite = open(ReuseDH, "w+")
#the output file Stack Distance Distribution
SDHWrite = open(StackDH,"w+")

#core0ReuseDis pattern
core0ReuseDisPattern = re.compile(r'.*(system.l2.core0ReuseDis::)([0-9]+)\s+([0-9]+)')
core0ReuseSamplePattern = re.compile(r'.*(system.l2.core0ReuseDis::sample).* ([0-9]+)')
#core1ReuseDis pattern
core1ReuseDisPattern = re.compile(r'.*(system.l2.core1ReussDis::)([0-9]+)\s+([0-9]+)')
core1ReuseSamplePattern = re.compile(r'.*(system.l2.core1ReuseDis::sample).* ([0-9]+)')
#l2Stack historgram Pattern
l2StackHisPattern = re.compile(r'.*(system.l2.l2StackHis).*([0-9]+)\s+([0-9]+)')
#l2 cachehits Pattern
l2cachehitsPattern = re.compile(r'.*(system.l2.cachehits).*([0-9|\.]+)')
#core memread pattern
core0memreadPattern = re.compile(r'.*(system.switch_cpus0.commit.op_class_0::MemRead).* ([0-9]+)\s+.*')
core1memreadPattern = re.compile(r'.*(system.switch_cpus1.commit.op_class_0::MemRead).* ([0-9]+)\s+.*')
#core memwrite Pattern
core0memwritePattern = re.compile(r'.*(system.switch_cpus0.commit.op_class_0::MemWrite).* ([0-9]+)\s+.*')
core1memwritePattern = re.compile(r'.*(system.switch_cpus1.commit.op_class_0::MemWrite).* ([0-9]+)\s+.*')
#core commit total Pattern
core0commitPattern = re.compile(r'.*(system.switch_cpus0.commit.op_class_0::total).* ([0-9|\.]+)')
core1commitPattern = re.compile(r'.*(system.switch_cpus1.commit.op_class_0::total).* ([0-9|\.]+)')
#core cpi pattern
core0cpiPattern = re.compile(r'.*(system.switch_cpus0.cpi).* (([0-9|\.]+)|(nan))')
core1cpiPattern = re.compile(r'.*(system.switch_cpus1.cpi).* (([0-9|\.]+)|(nan))')
#thread pattern
threadbeginPattern = re.compile(r'.*Begin Simulation Statistics.*')
threadendPattern =re.compile(r'.*End Simulation Statistics.*')
lines = fpRead.readline()
#debug is the flag to denote which thread is working on
debug = 1

###
### func check is mean to check the distribution is continuous or not
###
def check(a,b):
    if b-a==1:
        return 0
    else:
        c = b-a
        return c


while lines:
    threadbeginmatch = threadbeginPattern.search(lines)
#    print "----------------------- reading lines------------------"
    if threadbeginmatch:
        #this three flag is to denote the distribution is first time to work
        #when it is true which means we are collect this thread's first distribution
        #once we collect the thread's first distribution ,we set the flag to false
        core0flag = True
        core1flag = True
        l2flag = True
        #this three list is the container of distrubtion
        core0=[]
        core1=[]
        l2 = []
        #this thres pos is the pointer of the last distribution we collected
        #use it to check the distribution is continuous or not
        core0pos=1
        core1pos=1
        l2pos = 1
        l2R = []
        l2ES=[]
        #this three pos is the pointer of the Distribution we are collecting
        pos0=0
        pos1=0
        pos2=0
#        print "------------------------ thread matched ------------------"
        threadlines = fpRead.readline()
        threadendmatch = threadendPattern.match(threadlines)
    	while threadlines:
            core0Dismatch = core0ReuseDisPattern.search(threadlines)
            core1Dismatch = core1ReuseDisPattern.search(threadlines)
            core0samplematch = core0ReuseSamplePattern.search(threadlines)
            core1samplematch = core1ReuseSamplePattern.search(threadlines)
            l2Hismatch = l2StackHisPattern.search(threadlines)
            l2cachehitsmatch = l2cachehitsPattern.search(threadlines)
            core0readmatch =  core0memreadPattern.search(threadlines)
            core0writematch = core0memwritePattern.search(threadlines)
            core0commitmatch = core0commitPattern.search(threadlines)
            core0cpimatch = core0cpiPattern.search(threadlines)
            core1readmatch =  core1memreadPattern.search(threadlines)
            core1writematch = core1memwritePattern.search(threadlines)
            core1commitmatch = core1commitPattern.search(threadlines)
            core1cpimatch = core1cpiPattern.search(threadlines)
            threadendmatch = threadendPattern.match(threadlines)
            if core0samplematch:
                core0sample = core0samplematch.group(2)
            if core0Dismatch:
                pos0 = int(core0Dismatch.group(2))
                #this part add the 0 to the distribution
                #when our distribtuion begin with the number bigger than 1
                if core0flag:
                    core0flag = False
                    core0pos = pos0
                    dis0 = pos0
                    while(dis0-1) > 0:
                        core0.append(0)
                        dis0 = dis0-1
                val0 = int(core0Dismatch.group(3))
                #this part the add the 0 to the distribution
                #when our distribution is not continous
                dis0 = check(core0pos,pos0)
                if dis0!=0:
                    while (dis0-1) > 0:
                        core0.append(0)
                        dis0 = dis0-1
                core0.append(val0)
                core0pos = pos0
            if core1samplematch:
                core1sample = core1samplematch.group(2)
            if core1Dismatch:
                pos1 = int(core1Dismatch.group(2))
                if core1flag:
                    core1flag = False
                    core1pos = pos1
                    dis1 = pos1
                    while(dis1-1) >0 :
                        core1.append(0)
                        dis1 = dis1-1
                val1 = int(core1Dismatch.group(3))
                dis1 = check(core1pos,pos1)
                if dis1!=0:
                    while (dis1-1) > 0:
                        core1.append(0)
                        dis1 = dis1-1
                core1.append(val1)
                core1pos = pos1
            if l2Hismatch:
                pos2 = int(l2Hismatch.group(2))
                if l2flag:
                    l2flag = False
                    l2pos = pos2
                    dis2 = pos2
                    while(dis2-1) > 0:
                        l2.append(0)
                        dis2 = dis2-1
                val2 = int(l2Hismatch.group(3))
                dis2 = check(l2pos,pos2)
                if dis2!=0:
                    while (dis2-1) > 0:
                        l2.append(0)
                        dis2 = dis2-1
                l2.append(val2)
                l2pos = pos2
            if l2cachehitsmatch:
                cachehits = l2cachehitsmatch.group(2)
            if core0readmatch:
                read0 = int(core0readmatch.group(2))
            if core0writematch:
                write0 = int(core0writematch.group(2))
            if core0commitmatch:
                commit0 = float(core0commitmatch.group(2))
            if core0cpimatch:
                cpi0 = core0cpimatch.group(2)
                if(cpi0!='nan'):
                    cpi0=float(cpi0)
                else:
                    cpi0=0
            if core1readmatch:
                read1 = int(core1readmatch.group(2))
            if core1writematch:
                write1 = int(core1writematch.group(2))
            if core1commitmatch:
                commit1 = float(core1commitmatch.group(2))
            if core1cpimatch:
                cpi1 = core1cpimatch.group(2)
                if(cpi1!='nan'):
                    cpi1=float(cpi1)
                else:
                    cpi1=0
            if threadendmatch:
                #full the histogram
                dis0 = check(pos0,300)
                dis1 = check(pos1,300)
                dis2 = check(pos2,30)
                if (dis0==0):
                    if pos0==299:
                        core0.append(0)
                else:
                    while dis0 > 0 :
                        core0.append(0)
                        dis0 = dis0-1
                if (dis1==0):
                    if pos1 == 299:
                        core1.append(0)
                else:
                    while dis1 > 0:
                        core1.append(0)
                        dis1 = dis1-1
                if (dis2==0):
                    if pos2 == 29:
                        l2.append(0)
                else:
                    while dis2 > 0:
                        l2.append(0)
                        dis2 = dis2-1
                print len(core0)
                assert len(core0)==300, "core0 len error"
                assert len(core1)==300, "core1 len error"
                assert len(l2)==30,"l2 len error"
                ##
                ##this part is to calc the added up reuse distance distribution
                ##when the cpi0 and cpi1 are both exist we do the calc
                ##when it's not ,add the direct
                ##
                if ((cpi1!=0) and (cpi0!=0)):
                    fac0=(read0+write0)/commit0
                    fac1=(read1+write1)/commit1
                    cpic0=cpi0/cpi1
                    cpic1=cpi1/cpi0
                    temp0 = (fac1/fac0)*cpic0
                    temp1 = (fac0/fac1)*cpic1
                    core0coe = float('%.2f'%temp0)
                    core1coe = float('%.2f'%temp1)
                    for i in range(300):
                        core0[i] = core0[i]*(1+core0coe)
                        core1[i] = core1[i]*(1+core1coe)
                        l2R.append(int(core0[i]+core1[i]))
                else:
                    for j in range(300):
                        l2R.append(int(core0[j]+core1[j]))
                assert len(l2R)==300, "l2R error"
                for k in range(300):
                    RDHWrite.write("%d" %l2R[k])
                for m in range(30):
                    SDHWrite.write("%d " %l2[m])
                RDHWrite.write('\n')
                SDHWrite.write("\n")
                print "thread ", debug,"done"
                debug = debug +1
                break
            threadlines = fpRead.readline()
    lines = fpRead.readline()
fpRead.close()
RDHWrite.close()
SDHWrite.close()


