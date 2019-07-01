#!/usr/bin/env python

##################################
# Wrapper around CWBQuery.jar
#
# Author: Aparna Bhaskaran (aparnab@gps.caltech.edu)
##################################

from __future__ import print_function
from argparse import ArgumentParser
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import time
import subprocess
import re
import sys
import os
import glob
import cx_Oracle
import traceback

#debug
debug = 0

def Main():
    global debug
    net = ""
    cwbnet = ""
    sta = ""
    cwbsta = ""
    chan = ""
    loc = ""
    sncl = ""
    cwbhost = ""
    queryjarlines = []
    stationsfromregex = []
    stationsexactmatch = []
    
    parser = ArgumentParser()
    parser.add_argument('sncl', nargs='?', default="",help='SNCL to query for. *** NOTE: It is recommended to put double quotes around the sncl argument ***. Format is NN.SSSSS. Wildcards can be used. Information for DURATION seconds (from chkcwb.cfg) will be returned.')
    parser.add_argument('-s', help="The CWB server to connect to, default is CWBIP from chkcwb.cfg", dest='cwbhost')
    parser.add_argument('-a', help="Display all channels associated with station(s)", action='store_true', dest='allchans')
    parser.add_argument('-gaps', help="Display gaps associated with station(s), for the past hour", action='store_true', dest='gapFlag')
    parser.add_argument('-lat', help="Display latency associated with station(s)", action='store_true', dest='latency')
    parser.add_argument('-debug', action='store_true', dest='debug')
    options = parser.parse_args()

    print ("\n*** NOTE: It is recommended to put double quotes around the sncl argument ***\n")

    if options.debug:
        debug = 1

    if debug:
        print (options)
    
    config = configparser.RawConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chkcwb.cfg'))
    
    if options.sncl == '':
        sncl = ""
    else:    
        sncl = options.sncl

    if re.search('[^_?.*a-zA-Z0-9]',sncl) != None:
        print ("Invalid sncl. Allowed characters are ?, *, ., _, a-z, A-Z and 0-9")
        return
    
        
    cwbsncl = ''    

    if sncl.find('.') != -1:
        splitsncl = sncl.split('.')
        if len(splitsncl) == 1: 
            cwbsncl = '"%s"' %sncl
        if len(splitsncl) >= 2:
            net = sncl.split('.')[0]
            cwbnet = DotPad(net, 2)

            sta = sncl.split('.')[1]            
            #if sta is a wildcard, dotpad it so all stations for the network can be retrieved
            #if sta contains a wildcard, blankpad it for exact station match
            if sta.find('*') >= 0 or sta.find('?') >= 0 or sta.find('?') >= 0:
                cwbsta = DotPad(sta,5)
            else:
                cwbsta = BlankPad(sta, 5)
                        
            cwbsncl += "{0}{1}".format(cwbnet, cwbsta) #len(cwbsncl) should be 7

        if len(splitsncl) >= 3:   
            chan = sncl.split('.')[2]
            chan = DotPad(chan, 3)
            cwbsncl += chan #len(cwbsncl) should be 10
            
        if len(splitsncl) == 4:
            loc = sncl.split('.')[3]
            loc = DotPad(loc, 2)
            cwbsncl += loc #len(cwbsncl) should be 12
                
    if sncl.find('.') == -1: 
        cwbsncl = DotPad(sncl, 7)

    if not options.allchans and len(cwbsncl) < 12:
        cwbsncl = '%s(%s)' %(cwbsncl, config.get('search_defaults','CHANNELS').strip().replace(" ", "").replace(",","|").replace("*",".*").replace("_",".?"))
        cwbsncl += ".*"

    if options.cwbhost:
        cwbhost = options.cwbhost
    else:
        cwbhost =  config.get('cwb','CWBIP')


    if debug:
        print ('cwbsncl = ', cwbsncl)
    
    if options.gapFlag:
        Gaps(cwbsncl, options, config)
        return

    if options.latency:
        Latency(cwbsncl, config, cwbhost)
        return
    
    if sncl.find('*') > 0 or sncl.find('?') >  0 or sncl.find('_') > 0:

        if config.has_section('db'):
            dbuser = config.get('db','USER')
            dbpassword = config.get('db','PASSWORD')
            dbname = config.get('db','NAME')

            if config.has_option('db','SQL'):
                statement = config.get('db','SQL')
                if len(statement.strip()):
                    statement += " where net like '{0}%'".format(net)
                    if sta:
                        statement += " and sta like '{0}' ".format(sta.replace('*','%').replace('?','%').replace('_','%'))
                        statement += "order by 1,2"
                    if debug:
                        print (statement)

                    conn = cx_Oracle.connect(dbuser, dbpassword, dbname)
                    cursor = conn.cursor()                
                    cursor.execute(statement)
                    resultSet = cursor.fetchall()
                    cursor.close()
                    conn.close()
                    stationsfromregex = [BlankPad("{0}{1}".format(result[0],result[1]),7) for result in resultSet]
                
        
    #default behaviour
    now = time.time()
    past = time.gmtime(now - float(config.get('duration','GOBACK')))
    paststr = '"%s"' %time.strftime('%Y/%m/%d %H:%M:%S', past)    
    nowstr = ''
    try:        

        #by default, use the cwbip and port in the query.prop
        cmd = ['java', '-jar','%s/CWBQuery.jar' %config.get('cwb','CWBQUERYPATH'), '-s', '"%s"' %cwbsncl, '-b', paststr,  '-d', '%s' %config.get('duration','DURATION'), '-list']

        #use CWB host has specified via -s or in the config file via CWPIP
        if cwbhost:
            cmd.append('-h')
            cmd.append(cwbhost)

        if debug:
            print (cmd)
        
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        nowstr = time.strftime('%Y/%m/%d %H:%M:%S',time.gmtime(now - float(config.get('duration','DURATION'))))
        queryjarlines =  proc.stdout.readlines()

    except KeyboardInterrupt:
        print ("KeyboardInterrupt")
        return
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        for line in traceback.format_tb(exc_traceback):
            print(line)

    try:

        print ("\nChecking %s at %s UTC\n" %(sncl,nowstr))

        if debug:
            print (queryjarlines)
            print (len(queryjarlines))

        for line in queryjarlines:
            nowstr = time.strftime('%Y/%m/%d %H:%M:%S',time.gmtime(time.time()))        
            line = line.decode().replace('\nRun for  ', 'data for ').strip('\n')

            sncl = re.search("[A-Z0-9]+\s*[A-Z0-9]+", line).group(0)

            if sncl[:7] in stationsfromregex:
                stationsfromregex.remove(sncl[:7])

            dottedsncl = '%s.%s.%s' %(sncl[0:2], sncl[2:7].strip(), sncl[7:10].strip())
            if len(sncl) > 10:
                dottedsncl += '.%s' %(sncl[10:12])
            dottedsncl += ' '
            line = re.sub("[A-Z0-9]+\s*[A-Z0-9]+\s*", dottedsncl, line, count=1)
            print ("Last check at %s, %s" %(nowstr, line.strip('\n')))

        
        if not len(queryjarlines):
            print ("\n{0} might be offline. Checking last packet receive time...\n".format(sncl))
            Latency(cwbsncl, config, cwbhost)
        elif stationsfromregex:            
            for sncl in stationsfromregex:
                print ("\n{0} might be offline. Checking last packet receive time...\n".format(sncl))
                #sncl is NNSSSSS right now, with length = 7
                cwbsncl = sncl.replace(" ",".")                
                if not options.allchans:
                    cwbsncl = '{0}[EH][HN]'.format(cwbsncl)
                Latency(cwbsncl, config, cwbhost)
    except KeyboardInterrupt:
        print ("KeyboardInterrupt")
        return
    except:
        print ("EXCEPTION")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
            print (line)
        return
        



def Latency(cwbsncl, config, cwbhost):
    if cwbsncl.find('*') == -1:
        cwbsncl = cwbsncl.replace(' ','')
        cwbsncl += '.*'
    try:
        cmd = ['java', '-jar','%s/CWBQuery.jar' %config.get('cwb','CWBQUERYPATH'), '-re', cwbsncl, '-lat']

        if cwbhost:
            cmd.append('-h')
            cmd.append(cwbhost)

        if debug:
            print (cmd)

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc.wait()        
        queryjarlines =  proc.stdout.readlines()
        queryjarlines = [line.decode() for line in queryjarlines]
        
        if "".join(queryjarlines).find("No route to host") != -1:
            print ("Latency information unavailable from CWB host, %s \n" %cwbhost)
            return
        
        for line in queryjarlines:
            print (line.strip('\n'))
    except KeyboardInterrupt:
        raise        
    except:
        print ("Latency EXCEPTION")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
            print (line)



def Gaps(cwbsncl, options, config):
    nowstr = ''
    queryjarlines = []
    now = time.time()
    past = time.gmtime(now - (float(config.get('duration','GAPDURATION')) + 60))
    paststr = '"%s"' %time.strftime('%Y/%m/%d %H:%M:%S', past)
    cmd = ['java', '-jar','%s/CWBQuery.jar' %config.get('cwb','CWBQUERYPATH'), '-h', config.get('cwb','CWBIP'), '-p', config.get('cwb','CWBPORT'), '-s', cwbsncl, '-b', paststr,  '-d', '%s' %config.get('duration','GAPDURATION'), '-gaps']
    if debug:
        print (cmd)

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        nowstr = time.strftime('%Y/%m/%d %H:%M:%S',time.gmtime(now - float(config.get('duration','DURATION'))))
        queryjarlines =  proc.stdout.readlines()
        
        print ("\nChecking %s at %s UTC (gaps displayed are from the past hour)\n" %(options.sncl, nowstr))
        for line in queryjarlines:
            print (line.decode().strip('\n'))

    except KeyboardInterrupt:
        raise                
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
            print (line)
        

#utilities
def BlankPad(code, length):
    code = code.replace('*',' ').replace('?',' ').replace('_',' ')
    while len(code) < length:
        code += ' '
    return code

def DotPad(code, length):
    code = code.replace('*','.').replace('?','.').replace('_','.')
    while len(code) < length:
        code += '.'
    return code



if __name__ == "__main__":
    Main()



