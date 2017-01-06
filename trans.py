#!/usr/bin/env python
import sys
infile = sys.argv[1]
outfile = 'esd.txt'
fpread = open(infile,"r")
fpwrite = open(outfile,"w+")

line = fpread.readline()
line = line.strip(" ")

rd = line.split(" ")

rd.pop()
def listsum(a,b):
    ret = 0
    for i in range(a):
        ret = ret+b[i]
    return ret

for i in range(len(rd)):
    rd[i] = int(rd[i])

rdsum = sum(rd)
def getlist(a,b):
    for i in range(a):
        b.append([])
    return b
sd=[1]
sd = getlist(199,sd)
adjust=[]
adjust=getlist(200,adjust)
esd =[]

for k in range(len(rd)):
    pos = k+1
    if(pos==200):
        break
    sd[pos]=sd[k]+(rdsum-listsum(pos,rd))/float(rdsum)

print sd
for i in range(len(sd)):
    if(sd[i]>int(sd[i])+0.4):
        adjust[i]=int(sd[i])+1
    else:
        adjust[i]=int(sd[i])

esd =[]

for i in range(max(adjust)):
    esd.append(0)

for i in range(len(adjust)):
    esd[adjust[i]-1]=esd[adjust[i]-1]+rd[i]

num = 0
for i in range(len(adjust)):
    if adjust[i]<=8:
        num=num+1

ret = listsum(num,rd)

print ret

for i in range(len(esd)):
    fpwrite.write("%d " % esd[i])

fpwrite.close()
fpread.close()
