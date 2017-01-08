#!/usr/bin/env python

### this is the python script created by Ferris Cheung 2017-01-01
### It is used to get the shared Cache Reuse Distance Distribution which is added up by diff core's RDD-----L2RD
### and then we trans she l2RD to l2R,according to int trans the first element of L2RD
### and it gets the shared Cache Stack Distance Distribution which is collected in the l2 cache port ----L2E,and it's output as name-stack.txt
### This Script is the to get the data from the same thread

import sys
import re
import os
###
### input file and output file define
###
inFilename = sys.argv[1]
inFile2name = sys.argv[2]
threadname = sys.argv[3]
if os.path.isfile(inFilename):
    namelength = inFilename.rfind(".")
    name = inFilename[0:namelength]
    exten = inFilename[namelength:]
    ReuseDH = name+"-reuse-"+threadname+exten
    StackDH = name+"-stack-"+threadname+exten
    RD8 = name+"-reuse8-"+threadname+exten
    SD8 = name+"-stack8-"+threadname+exten
print "inFilename:", inFilename,inFile2name
print "outFilename:", ReuseDH,StackDH,RD8,SD8
print "thread name:",threadname
#the input file stats.txt
fpRead = open(inFilename, "r")
#the input file system.tasks.txt
tkRead = open(inFile2name,"r")
#the output file Reuse Distance Distribution
RDHWrite = open(ReuseDH, "w+")
#the output file Stack Distance Distribution
SDHWrite = open(StackDH,"w+")

RD8Write = open(RD8,"w+")
SD8Write = open(SD8,"w+")
#thread name pattern
threadnamePattern = re.compile(r'.*(next_task=%s).*' % threadname)
#core0ReuseDis pattern
core0ReuseDisPattern = re.compile(r'.*(system.l2.core0ReuseDis::)([0-9]+)\s+([0-9]+)')
core0ReuseSamplePattern = re.compile(r'.*(system.l2.core0ReuseDis::sample).* ([0-9]+)')
#core1ReuseDis pattern
core1ReuseDisPattern = re.compile(r'.*(system.l2.core1ReussDis::)([0-9]+)\s+([0-9]+)')
core1ReuseSamplePattern = re.compile(r'.*(system.l2.core1ReuseDis::sample).* ([0-9]+)')
#l2Stack historgram Pattern
l2StackHisPattern = re.compile(r'.*(system.l2.l2StackHis::)([0-9]+)\s+([0-9]+)')
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

#thread num
threadnum = 1
#stats num
statsnum = 1

# task lines is the line read of system.tasks.txt
tasklines = tkRead.readline()

###
###  func to get the num length list
###
def listget(num):
    ret = []
    for i in range(num):
        ret.append(0)
    return ret
###
###
def addlist(num,a):
    for i in range(num):
        a.append([])
    return a


### rdaddup means reuse distance addup , this list is the sum of reuse distance distribution
rdaddup = listget(2000)

### sdaddup means stack distance addup , this list is the sum of stack distance distribution
sdaddup = listget(30)

###
### func check is mean to check the distribution is continuous or not
###
def check(a,b):
    if b-a==1:
        return 0
    else:
        c = b-a
        return c

###
### func to get the former num a element summary
###
def listsum(a,b):
    ret = 0
    for i in range(a):
        ret =ret + b[i]
    return ret

while tasklines:
    ### check if this thread is the thread we want or not
    threadnamematch = threadnamePattern.search(tasklines)
    if threadnamematch:
        # if match means we need to collect the thread info
        while 1:
            if threadnum == statsnum:
                # to arrive the threadinfo in the stats.txt
                # if equal means we alrady arrived
                print threadnum
                # this flag to denote we enter the thread info ,and we should collect the data
                # when we the num equal ,we set it to false
                # when we enter the thread we set it to true
                # and when we collect the data finished, we used it to checn if to break or not
                threadflag = False
                ##du stats data
                while lines:
                    threadbeginmatch = threadbeginPattern.search(lines)
                    if threadbeginmatch:
                        threadflag = True
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
                        ## the l2RD means the l2R dict , it used to get the changed reuse distance
                        ## the l2R means the changed and transed l2 reuse distance
                        ## the l2ES is the l2 expected stack disance distribution
                        l2RD0 = {}
                        l2RD = {}
                        l2R = []
                        l2ES=[]
                        #this three pos is the pointer of the Distribution we are collecting
                        pos0=0
                        pos1=0
                        pos2=0
                        threadlines = fpRead.readline()
                        threadendmatch = threadendPattern.match(threadlines)
                        while threadlines:
                            # enter the thread phase, set the match
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
                            threadendmatch = threadendPattern.search(threadlines)
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
                                # the thread collect had reach the end
                                statsnum = statsnum+1
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
                                    ## to comfirm the l2R's size
                                    l2R = listget(max(int(300*(1+core0coe)),int(300*(1+core1coe)))+1)
                                    ## in this part ,we calc the L2RD,which is the reuse distance just addup
                                    ## notice that the core0coe is the cofficient of core0
                                    ## and the cofficient should be worked at the distance,
                                    ## it cannot be worked at the num of distance
                                    for i in range(300):
                                        pm1 = (i+1)*(1+core0coe)
                                        pm2 = (i+1)*(1+core1coe)
                                        l2RD0[pm1] = core0[i]
                                        l2RD[pm2] = core1[i]
                                elif cpi1==0:
                                    l2R = listget(300)
                                    for j1 in range(300):
                                        l2RD[j1+1]=core0[j1]
                                elif cpi0==0:
                                    l2R = listget(300)
                                    for j2 in range(300):
                                        l2RD[j2+1]=core1[j2]
                                ## merge the two dict
                                for i in l2RD0.items():
                                    if l2RD.has_key(i[0]):
                                        l2RD[i[0]]=l2RD[i[0]]+i[1]
                                    else:
                                        l2RD[i[0]]=i[1]
                                ## in this part we do the int trans for l2RD dict
                                ## to l2R list , the index means the reuse distance, the val means the num of reuse distance
                                for i in l2RD.items():
                                    temp = int(i[0])-1
                                    l2R[temp]=l2R[temp]+i[1]
                                ## add the distribution,get sdaddup and rdaddup
                                for s1 in range(30):
                                    sdaddup[s1]=sdaddup[s1]+l2[s1]
                                for s2 in range(len(l2R)):
                                    if s2 >=2000:
                                        break
                                    rdaddup[s2]=rdaddup[s2]+l2R[s2]
                                ## write the
                                for k in range(len(l2R)):
                                    RDHWrite.write("%d " %l2R[k])
                                for m in range(30):
                                    SDHWrite.write("%d " %l2[m])
                                RDHWrite.write('\n')
                                SDHWrite.write("\n")
                                print "thread ",debug,"done"
                                debug =debug +1
                                break
                            threadlines = fpRead.readline()
                    if threadflag:
                        break
                    else:
                        lines = fpRead.readline()
                break
            else:
                lines = fpRead.readline()
                while lines:
                    threadmatch = threadendPattern.search(lines)
                    samplematch = core0ReuseSamplePattern.search(lines)
                    if threadmatch:
                        statsnum = statsnum+1
                        break
                    lines = fpRead.readline()
        threadnum = threadnum+1
    else:
        threadnum = threadnum+1

    tasklines=tkRead.readline()

##
distance = [1]
distance = addlist(len(rdaddup),distance)
rdsum = sum(rdaddup)
##to trans the l2 reuse distance to the l2 expect stack distance
for i in range(len(rdaddup)):
    pos = i+1
    if(i==len(rdaddup)):
        break
    distance[pos] = distance[i]+((rdsum - listsum(i,rdaddup))/float(rdsum))
## adjust the l2 expect stack distance
adjust = []
adjust = listget(len(distance))
for i in range(len(distance)):
    if(distance[i]>int(distance[i])+0.5):
        adjust[i]=distance[i]+1
    else:
        adjust[i]=int(distance[i])
## according to the adjust stack distance we set up the expect stack distance distribution
esd=[]
esd = listget(max(adjust))
for i in range(len(rdaddup)):
    esd[adjust[i]-1]=esd[adjust[i]-1]+rdaddup[i]

## to calc the hit num according to the esd
num = 0
for i in range(len(adjust)):
    if adjust[i]<=8:
        num = num+1

esdhit = listsum(num,rdaddup)
sdhit = listsum(8,sdaddup)
for d1 in range(30):
    SD8Write.write("%d " %sdaddup[d1])
SD8Write.write("%d " % sdhit)

for d2 in range(len(esd)):
    RD8Write.write("%d " %esd[d2])
RD8Write.write("%d "% esdhit)

tkRead.close()
fpRead.close()
RDHWrite.close()
SDHWrite.close()
RD8Write.close()
SD8Write.close()


