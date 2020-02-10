from urllib import urlopen
from zipfile import ZipFile
from StringIO import StringIO
import subprocess
import requests
import json
import base64
import os
import sys
import platform
import stat

#PARAM_KLA_USERNAME = 'luis.garcia@kiuwan.com'
#PARAM_KLA_PASSWORD = 'password.0'
#PARAM_KLA_APPNAME = 'pepe'
#PARAM_KLA_SOURCEDIR = 'D:\D_LGV\_support\Kiuwan\lgv'
#PARAM_KLA_MAXMEMORY = 'memory.max=2048m'

#PARAM_KLA_USERNAME = os.environ['INPUT_USERID'] 
#PARAM_KLA_PASSWORD = os.environ['INPUT_PASSWORD'] 
#PARAM_KLA_APPNAME = os.environ['INPUT_PROJECT'] 
#PARAM_KLA_SOURCEDIR = os.environ['HOME'] 
#PARAM_KLA_MAXMEMORY = 'memory.max=2048m' #TODO: esto es tan importante??

print(os.environ)

KLA_URL = 'https://www.kiuwan.com/pub/analyzer/KiuwanLocalAnalyzer.zip'
TMP_EXTRACTION_DIR = 'temp'
KLA_EXE_DIR = TMP_EXTRACTION_DIR + "/KiuwanLocalAnalyzer/bin"


def GetKLACmd( tmp_dir=TMP_EXTRACTION_DIR,
               appname=PARAM_KLA_APPNAME,
               sourcedir=PARAM_KLA_SOURCEDIR,
               user=PARAM_KLA_USERNAME,
               password=PARAM_KLA_PASSWORD,
               mem='1024m'):

    prefix = os.getcwd() + '\\' + tmp_dir + '\\KiuwanLocalAnalyzer\\bin\\'
    if platform.system() == 'Windows':
        #prefix = os.getcwd() + '\\' + tmp_dir + '\\KiuwanLocalAnalyzer\\bin\\'
        agent = prefix + 'agent.cmd'
    else:
        agent = prefix + 'agent.sh'
        agent = r'%s' % agent.replace('\\','/')
        os.chmod(agent, stat.S_IRWXU)

    #osgetcwd = r'%s' % os.getcwd().replace('\\','/')
    #prefix = osgetcwd + '/' + temp + '/KiuwanLocalAnalyzer/bin'
    #agent = prefix + '/' + agent

    klablcmd = '{} -c -n {} -s {} --user {} --pass {} {}'.format(agent,
                                                                 appname,
                                                                 sourcedir,
                                                                 user,
                                                                 password,
                                                                 mem)
    return klablcmd


def DownloadAndExtractKLA(tmp_dir=TMP_EXTRACTION_DIR, klaurl=KLA_URL ):
    print 'Downloading KLA zip from ' + klaurl + ' at [' + os.getcwd() + ']' + '...'
    resp = urlopen(klaurl)
    zipfile = ZipFile(StringIO(resp.read()))
    for item in zipfile.namelist():
        print("\tFile in zip: "+  item)

    print 'Extracting zip to [' + tmp_dir + ']' + '...'
    zipfile.extractall(tmp_dir)


def GetBLAnalysisCodeFromKLAOutput( output ):
    return output.split("Analysis created in Kiuwan with code:",1)[1].split()[0]

def GetBLAnalysisResultsURL(analysis_code, kla_user=PARAM_KLA_USERNAME, kla_password=PARAM_KLA_PASSWORD ): 
    auth_str = '%s:%s' % (kla_user, kla_password)
    b64_auth_str = base64.b64encode(auth_str)
    headers = {'Authorization': 'Basic %s' % b64_auth_str}

    apicall = "https://api.kiuwan.com/apps/analysis/" + analysis_code
    print 'Calling REST API [' + apicall + '] ...'
    response = requests.get(apicall, headers=headers)
    
    print response
    print 'Contenido' + response.content
    jdata = json.loads(response.content)
    #print 'URL del analisis: ' + jdata['analysisURL']
    return jdata['analysisURL']

def ExecuteKLA(cmd):
    print 'Executing [' + cmd + '] ...'
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    #(output, err) = pipe.communicate()
    output = ''
    while True:
        nextline = pipe.stdout.readline()
        if nextline == '' and pipe.poll() is not None:
            break
        output = output + nextline
        sys.stdout.write(nextline)
        sys.stdout.flush()
   
    rc = pipe.wait()
    return output, rc



print(os.getenv('INPUT_PROJECT'))
print('Hola caracola' )

# Extract and download KLA from kiuwan.com (or from on-premise site)
DownloadAndExtractKLA(tmp_dir='kaka')

# Build the KLA CLI command
kla_bl_cmd = GetKLACmd(tmp_dir='kaka', mem=PARAM_KLA_MAXMEMORY)

# Execute CLA KLI
output, rc = ExecuteKLA(kla_bl_cmd)
if rc == 0:
    print '{}{}'.format('KLA return code: ', rc)
    analysis_code = GetBLAnalysisCodeFromKLAOutput(output)
    print 'Analysis code [' + analysis_code + ']'
    url_analysis = GetBLAnalysisResultsURL(analysis_code)
    print 'URL del analisis: ' + url_analysis
else:
    print '{}{}{}'.format('Analysis finished with error code [', rc, ']')



