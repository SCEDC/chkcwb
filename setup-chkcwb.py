import os
import sys
import shutil
import traceback

#pythonversion = "python2.7"
#pythonexe = "/opt/python27/bin/%s" %pythonversion
virtualenvexe = "/bin/env virtualenv"
venvpath = "chkcwb-venv"

if len(sys.argv) > 1:
    venvpath = os.path.join(sys.argv[1], venvpath)

cmd = ""
#print ("Found Python %s.%s.%s" %(sys.version_info[0], sys.version_info[1],sys.version_info[2]))
if sys.version_info[0] == 3: #sys.version_info[0] is python major version
#if pythonversion.find("python3") != -1:
    cmd = "python3 -m venv " 
else:
    cmd = "%s " %virtualenvexe

cmd += venvpath + " && . %s/bin/activate"
if os.path.exists('requirements.txt'):
    cmd += " &&  pip install -r requirements.txt" %venvpath
print(cmd)

try:
    os.system(cmd)
except:
    print ("ERROR")
    etype,evalue,etraceback = sys.exc_info()
    print (etype)
    print (evalue)
    for line in traceback.format_tb(etraceback):
        print (line)
    sys.exit()


print (
"""
virtual environment for chkcwb was successfully setup at %s.
To configure chkcwb, cd to chkcwb-venv and edit chkcwb.cfg. 
To activate the virtual env, run "source %s/bin/activate"
""" %(venvpath, venvpath)
)



