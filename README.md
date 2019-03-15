# chkcwb

chkcwb is a tool to check for data availability in CWB, typically near real time. Additionally, it can also be used to query for gaps and latency in data acquisition for a sncl.
 
It is consists of chkcwb.py, which is a wrapper script around CWBQuery.jar. It's written in python2.x. chkcwb is a shell script wrapper around chkcwb.py created for ease of use.

chkcwb.py uses a config file named chkcwb.cfg. This config file must be present at the same location as the python script. 


Operation
----------

The default operation of chkcwb.py is to run CWBQuery.jar with -list for a sncl input by the user and the duration mentioned in the config file. If a sncl is offline, the timestamp of the last data packet received is returned. By default, chkcwb only checks for EH, HH and HN channels for input sncl.  

This whole paragraph is *optional*. chkcwb can be setup to run a sql query against an AQMS database to obtain a specific list of net.sta. This is especially useful with wildcard searches for RSNs with large number of channels. The database information and query details can be specified in chkcwb.cfg under section [db]. See sample chkcwb.cfg for more information.

  

Pre-requisites
---------------
- Python 2.6 or 2.7
- Java 1.8
- CWBQuery.jar
- cx_Oracle, if using AQMS database


Usage
------

$ chkcwb --help

NOTE: It is recommended to put double quotes around the sncl argument  
usage: chkcwb.py [-h] [-s CWBHOST] [-a] [-gaps] [-lat] [-debug] [sncl]  

positional arguments:  
  sncl        SNCL to query for. Format is NN.SSSSS.CCC.LL. Wildcards can be
              used. Information for the past minute will be returned.

optional arguments:  
  -h, --help  show this help message and exit  
  -s CWBHOST  The CWB server to connect to, default is CWBIP from chkcwb.cfg  
  -a          Display all channels associated with station(s)  
  -gaps       Display gaps associated with station(s), for the past hour  
  -lat        Display latency associated with station(s)  
  -debug  


Examples
---------

<b>1. Check for status of a station</b>

$ chkcwb "CI.WCS2"

NOTE: It is recommended to put double quotes around the sncl argument

Checking CI.WCS2 at 2018/04/13 23:35:11 UTC

Last check at 2018/04/13 23:36:12, Run for  CI.WCS2.HHE is complete 100%.  
Last check at 2018/04/13 23:36:12, Run for  CI.WCS2.HHN is complete 100%.  
Last check at 2018/04/13 23:36:12, Run for  CI.WCS2.HHZ is complete 100%.  
Last check at 2018/04/13 23:36:12, Run for  CI.WCS2.HNE is complete 100%.  
Last check at 2018/04/13 23:36:12, Run for  CI.WCS2.HNN is complete 100%.  
Last check at 2018/04/13 23:36:12, Run for  CI.WCS2.HNZ is complete 100%.  




<b>2. Check for status of a station (station is currently not acquiring data)</b>

$ chkcwb "CI.EDW2"

NOTE: It is recommended to put double quotes around the sncl argument

Checking CI.EDW2 at 2018/04/13 23:37:47 UTC

CI.EDW2 might be offline. Checking last packet receive time...

23:38:48.855 SSR[2]: Thread-2 gibbes.gps.caltech.edu/7992 ChannelStatus starting maxlen=70  
23:38:48.856 SSR[2]: SSR: Open Port=gibbes.gps.caltech.edu/7992  
23:38:48.883 SSR[2]: run init code  
23:38:48.943 SSR[2]: Expand msgs len=2000 nmsgs=1891  
23:38:48.968 SSR[2]: Expand msgs len=4000 nmsgs=3891  
23:38:48.985 SSR[2]: Expand msgs len=6000 nmsgs=5891  
SSR[2]: tot=6117 nmsg=5972 closed=false class=ChannelStatusrun=true s=gibbes.gps.caltech.edu/131.215.68.61/7992  
Channel           Packet Time               Received time#samp  Rate   Lrcv-min    Latency(s)  
1793 CIEDW2 HHE   2018/04/12 15:38:41.848 rcved at 2018/04/12 15:43:39.855 ns=212 rt=100.000 age=1915.2 ltcy=295.9  
1794 CIEDW2 HHN   2018/04/12 15:38:42.638 rcved at 2018/04/12 15:43:39.855 ns=233 rt=100.000 age=1915.2 ltcy=294.9  
1795 CIEDW2 HHZ   2018/04/12 15:38:44.838 rcved at 2018/04/12 15:43:39.855 ns=13 rt=100.000 age=1915.2 ltcy=294.9  
1796 CIEDW2 HNE   2018/04/12 15:38:41.338 rcved at 2018/04/12 15:43:39.855 ns=263 rt=100.000 age=1915.2 ltcy=295.9  
1797 CIEDW2 HNN   2018/04/12 15:38:39.368 rcved at 2018/04/12 15:43:39.855 ns=460 rt=100.000 age=1915.2 ltcy=295.9  
1798 CIEDW2 HNZ   2018/04/12 15:38:39.868 rcved at 2018/04/12 15:43:39.855 ns=410 rt=100.000 age=1915.2 ltcy=295.9  
End of execution  




<b>3. Check for data gaps in a station</b>

$ chkcwb "CI.COK2" -a -gaps

*** NOTE: It is recommended to put double quotes around the sncl argument ***


Checking CI.COK2 at 2018/08/31 22:43:54 UTC (gaps displayed are from the past hour)

22:44:55.877 -h gibbes.gps.caltech.edu  
22:44:56 Query on CICOK2 EHZ   000391 mini-seed blks 2018 243:21:43:48.2000 2018 243:22:21:58.430  ns=229024 #dups=0  
Gap: 2018,243,22:21:58.000 to 2018,243,22:43:54.000 (1315.56 secs) End-of-interval -s CICOK2-EHZ-- -b 2018,243,22:21:58.000 -d 1316.000  
22:44:56 Query on CICOK2 HNE   000339 mini-seed blks 2018 243:21:43:47.9100 2018 243:22:21:57.100  ns=228920 #dups=0  
Gap: 2018,243,22:21:57.000 to 2018,243,22:43:54.000 (1316.89 secs) End-of-interval -s CICOK2-HNE-- -b 2018,243,22:21:57.000 -d 1317.000  
22:44:56 Query on CICOK2 HNN   000353 mini-seed blks 2018 243:21:43:50.6700 2018 243:22:21:53.070  ns=228241 #dups=0  
Gap: 2018,243,22:21:53.000 to 2018,243,22:43:54.000 (1320.92 secs) End-of-interval -s CICOK2-HNN-- -b 2018,243,22:21:53.000 -d 1321.000  
22:44:56 Query on CICOK2 HNZ   000331 mini-seed blks 2018 243:21:43:52.8000 2018 243:22:21:53.610  ns=228082 #dups=0  
Gap: 2018,243,22:21:53.000 to 2018,243,22:43:54.000 (1320.38 secs) End-of-interval -s CICOK2-HNZ-- -b 2018,243,22:21:53.000 -d 1321.000  
22:44:56 Query on CICOK2 LCE   000003 mini-seed blks 2018 243:21:38:52.0000 2018 243:22:11:33.000  ns=1962 #dups=0  
Gap: 2018,243,22:11:34.000 to 2018,243,22:43:54.000 (1940.0 secs) End-of-interval -s CICOK2-LCE-- -b 2018,243,22:11:34.000 -d 1940.000   
22:44:56 Query on CICOK2 LCQ   000003 mini-seed blks 2018 243:21:36:30.0000 2018 243:22:12:32.000  ns=2163 #dups=0  
Gap: 2018,243,22:12:33.000 to 2018,243,22:43:54.000 (1881.0 secs) End-of-interval -s CICOK2-LCQ-- -b 2018,243,22:12:33.000 -d 1881.000  
22:44:56 Query on CICOK2 LEC   000004 mini-seed blks 2018 243:21:33:39.0000 2018 243:22:18:09.000  ns=2671 #dups=0  
Gap: 2018,243,22:18:10.000 to 2018,243,22:43:54.000 (1544.0 secs) End-of-interval -s CICOK2-LEC-- -b 2018,243,22:18:10.000 -d 1544.000  
22:44:56 Query on CICOK2 LEP   000003 mini-seed blks 2018 243:21:42:34.0000 2018 243:22:17:33.000  ns=2100 #dups=0  
Gap: 2018,243,22:17:34.000 to 2018,243,22:43:54.000 (1580.0 secs) End-of-interval -s CICOK2-LEP-- -b 2018,243,22:17:34.000 -d 1580.000  
22:44:56 Query on CICOK2 LII   000003 mini-seed blks 2018 243:21:36:29.0000 2018 243:22:12:31.000  ns=2163 #dups=0  
Gap: 2018,243,22:12:32.000 to 2018,243,22:43:54.000 (1882.0 secs) End-of-interval -s CICOK2-LII-- -b 2018,243,22:12:32.000 -d 1882.000  
22:44:56 Query on CICOK2 LKI   000003 mini-seed blks 2018 243:21:36:29.0000 2018 243:22:12:31.000  ns=2163 #dups=0  
Gap: 2018,243,22:12:32.000 to 2018,243,22:43:54.000 (1882.0 secs) End-of-interval -s CICOK2-LKI-- -b 2018,243,22:12:32.000 -d 1882.000  
22:44:56 Query on CICOK2 LNE   000003 mini-seed blks 2018 243:21:36:27.0000 2018 243:22:12:29.000  ns=2163 #dups=0  
Gap: 2018,243,22:12:30.000 to 2018,243,22:43:54.000 (1884.0 secs) End-of-interval -s CICOK2-LNE-- -b 2018,243,22:12:30.000 -d 1884.000  
22:44:56 Query on CICOK2 LNN   000003 mini-seed blks 2018 243:21:36:21.0000 2018 243:22:12:16.000  ns=2156 #dups=0  
Gap: 2018,243,22:12:17.000 to 2018,243,22:43:54.000 (1897.0 secs) End-of-interval -s CICOK2-LNN-- -b 2018,243,22:12:17.000 -d 1897.000  
22:44:56 Query on CICOK2 LNZ   000003 mini-seed blks 2018 243:21:36:19.0000 2018 243:22:12:13.000  ns=2155 #dups=0  
Gap: 2018,243,22:12:14.000 to 2018,243,22:43:54.000 (1900.0 secs) End-of-interval -s CICOK2-LNZ-- -b 2018,243,22:12:14.000 -d 1900.000  
1442 Total blocks transferred in 298 ms 4838 b/s 0 #dups=0  




<b>4. Wildcard search</b>
$ chkcwb "CI.C*"

*** NOTE: It is recommended to put double quotes around the sncl argument ***


Checking CI.C* at 2018/08/31 22:49:42 UTC

Last check at 2018/08/31 22:50:43, 22.. :50:43.053 -h gibbes.gps.caltech.edu  
Last check at 2018/08/31 22:50:43, Run for  CI.CAC.EHZ is complete 100%.  
Last check at 2018/08/31 22:50:43, Run for  CI.CAC.HNE is complete 100%.  
Last check at 2018/08/31 22:50:43, Run for  CI.CAC.HNN is complete 100%.  
Last check at 2018/08/31 22:50:43, Run for  CI.CAC.HNZ is complete 100%.  
Last check at 2018/08/31 22:50:43, Run for  CI.CAR.HHE is complete 100%.  
Last check at 2018/08/31 22:50:43, Run for  CI.CAR.HHN is complete 100%.  
Last check at 2018/08/31 22:50:43, Run for  CI.CAR.HHZ is complete 100%.  
Last check at 2018/08/31 22:50:43, Run for  CI.CAR.HNE is complete 100%.  
Last check at 2018/08/31 22:50:43, Run for  CI.CAR.HNN is complete 100%.  
Last check at 2018/08/31 22:50:43, Run for  CI.CAR.HNZ is complete 100%.  
...  
