#!/usr/bin/python

version='v0.3.9'

import serial
import string
import time
import argparse

#path and device name
import xsensor_device
#path and file name
import xsensor_path

##set column names
#colnames(t)=c("time","index","battery","temperature","humidity",
#  "TGS4161","TGS2620","MICS2610","TGS2602","MICS2710","TGS2442",
#  "record")

#CLI arguments
serialDev='/dev/ttyUSB0'
fake='test.raw'
module='B12345'+'_'+'A902NNNN'
hostname='raspc2aN'
current_time=time.localtime()
info_file_name=xsensor_path.get_info_file_name(current_time,hostname)
file_name=xsensor_path.get_data_file_name(module,current_time)
raw_file_name=xsensor_path.get_raw_file_name(module,current_time)
parser = argparse.ArgumentParser(
  description='log data from libellium/waspmote sensor.'
  +' At least, 3 files will be written:'
  +' 1. single information file (.info),'
  +' 2. one raw sensor ouput (.raw) file per day,'
  +' 3. one data (.txt) file per day.'
 ,epilog='example: %(prog)s --device '+serialDev
  +'  #will write e.g. module #'+module+' data as 1."'
  +info_file_name+'", 2."'+file_name+'" and 3."'+raw_file_name+'" files.'
  )
parser.add_argument('-d','--device',default=serialDev, help='USB device name or '+fake+' (e.g. '+serialDev+')')
parser.add_argument('-v','--version',action='version',version='%(prog)s '+version)
args = parser.parse_args()

##--device CLI argument
serialDev=args.device
if(serialDev==fake): #test#
  print 'test' #test#
  ser=open(fake, 'r') #test#
else:
  ser=serial.Serial(serialDev, 115200, timeout=67)
print 'pack module lines from ', serialDev

#sensor parameter arrays
nb=13 #12 sensors and others
record=range(nb)
value=range(nb)

#get current time
current_time=time.localtime()
str_time=time.strftime('%Y/%m/%d %H:%M:%S\n',current_time)
print str_time

#set info file name from date
import platform
hostname=platform.node()
info_file_name=xsensor_path.get_info_file_name(current_time,hostname)

#write to information file
fi=open(info_file_name,"a")
fi.write("\n\n"+str_time)
fi.write("datalogger."+version+".py\n")
fi.write("running on "+hostname+"\n")

#get module start-up lines
while(True): #loop on both sensors and time
  #wait and get data
  line=ser.readline()
  #write to information file
  fi.write(line)
  if(line.find('|')>0): #parameter line if containing character '|'
    break
fi.close() #information file

#set module name
values=line.split('|')
moduleId=values[0]
#module=(module.split('_'))[0] #from generic for Help
module=moduleId+'_'+xsensor_device.get_serial_device_name(serialDev)

#set both raw and data file names from both module and date
file_name=xsensor_path.get_data_file_name(module,current_time)
raw_file_name=xsensor_path.get_raw_file_name(module,current_time)

#open raw file
fr=open(raw_file_name,"a")
#copy info in raw file
fi=open(info_file_name, 'r')
for line in fi:
  #write to raw file
  fr.write(line)
fr.close()

iteration=0

if(serialDev==fake): #test#
  mode=fake
else:
  mode='serial'
print 'start reading '+mode+' ...'
while(True): #loop on both sensors and time
  #wait and get data
  line=ser.readline()
  #exit at end of file
  if not line: break
  #show
  ##print line
  #write to raw file
  fr=open(raw_file_name,"a")
  fr.write(line)
  fr.close()
  #skip empty lines
  if(len(line)<6):
    continue
  #get information
  values=line.split('|')
  moduleId=values[0]
  index=int(values[2]) #sensor, see colnames
  if(index==1): #new record start
    #get record time
    current_time=time.localtime()
    #clear module array
    for i in xrange(0,len(record)):
      record[i]=0
    for i in xrange(0,len(value)):
      value[i]=''
  #add sensor parameters in arrays
  record[index]=int(values[1])
  value[index]=values[3].replace("\n","")
  #write to file
  if(index==12): #new record stop
    #generate module line from arrays
    str_time=time.strftime('%Y/%m/%d %H:%M:%S',current_time)
    line=moduleId+";"+str_time+";"+str(iteration)
    line+=";"+str(value[1])
    for i in xrange(5,len(value)):
      line+=";"+value[i]
    line+=";"+str(record[index])
    line+="\n"
    print line
    #setup file name from date
    file_name=xsensor_path.get_data_file_name(module,current_time)
    raw_file_name=xsensor_path.get_raw_file_name(module,current_time)
    #write to file
    fo=open(file_name,"a")
    fo.write(line)
    fo.close()
    #next record index
    iteration+=1

if(serialDev==fake): #test#
  ser.close()
