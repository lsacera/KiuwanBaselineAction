import zipfile
import subprocess
import requests
import urllib
import io
import json
import base64
import os
import sys
import stat

#PARAM_KLA_USERNAME = 'luis.garcia@kiuwan.com'
#PARAM_KLA_PASSWORD = 'password.0'
#PARAM_KLA_APPNAME = 'pepe'
#PARAM_KLA_SOURCEDIR = 'D:\D_LGV\_support\Kiuwan\lgv'
#PARAM_KLA_MAXMEMORY = 'memory.max=2048m'

#Params used in the call to the baseline analysis. TODO: check the parameters...
PARAM_KLA_USERNAME = os.environ['INPUT_USERID'] 
PARAM_KLA_PASSWORD = os.environ['INPUT_PASSWORD'] 
PARAM_KLA_APPNAME = os.environ['INPUT_PROJECT'] 
PARAM_KLA_SOURCEDIR = os.environ['GITHUB_WORKSPACE'] 
PARAM_KLA_MAXMEMORY = 'memory.max=' + os.environ['INPUT_MAXMEMORY'] + 'm' 
PARAM_KLA_APPNAME = os.environ['INPUT_PROJECT']

#Remaining params to define and check
PARAM_KLA_INCLUDEPATTERNS = os.environ['INPUT_INCLUDEPATTERNS']
PARAM_KLA_EXCLUDEPATTERNS = os.environ['INPUT_EXCLUDEPATTERNS']
PARAM_KLA_TIMEOUT = os.environ['INPUT_TIMEOUT']
PARAM_KLA_DATABASETYPE = os.environ['INPUT_DATABASETYPE']

#Log parameters
print ('user:',PARAM_KLA_USERNAME, 'appname:',PARAM_KLA_APPNAME,'sourcedir:',PARAM_KLA_SOURCEDIR ,'maxmem:', PARAM_KLA_MAXMEMORY,'includes:',PARAM_KLA_INCLUDEPATTERNS,'excludes:',PARAM_KLA_EXCLUDEPATTERNS ,'timeout:',PARAM_KLA_TIMEOUT,'database:',PARAM_KLA_DATABASETYPE)

KLA_URL = 'https://www.kiuwan.com/pub/analyzer/KiuwanLocalAnalyzer.zip'
TMP_EXTRACTION_DIR = '/kla'
KLA_EXE_DIR = TMP_EXTRACTION_DIR + "/KiuwanLocalAnalyzer/bin"


def GetKLACmd( tmp_dir=TMP_EXTRACTION_DIR,
               appname=PARAM_KLA_APPNAME,
               sourcedir=PARAM_KLA_SOURCEDIR,
               user=PARAM_KLA_USERNAME,
               password=PARAM_KLA_PASSWORD,
               mem='1024m'):

    prefix = tmp_dir + '/KiuwanLocalAnalyzer/bin/'
    agent = prefix + 'agent.sh'
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
    print ('Downloading KLA zip from ', klaurl, ' at [', os.getcwd(), ']', '...')
    resp = urllib.request.urlopen(klaurl)
    zipf = zipfile.ZipFile(io.BytesIO(resp.read()))
    for item in zipf.namelist():
        print("\tFile in zip: ",  item)

    print ('Extracting zip to [' , tmp_dir , ']' , '...')
    zipf.extractall(tmp_dir)


def GetBLAnalysisCodeFromKLAOutput( output ):
    return output.split("Analysis created in Kiuwan with code:",1)[1].split()[0]

def GetBLAnalysisResultsURL(analysis_code, kla_user=PARAM_KLA_USERNAME, kla_password=PARAM_KLA_PASSWORD ): 
    auth_str = '%s:%s' % (kla_user, kla_password)
    b64_auth_str = base64.b64encode(auth_str)
    headers = {'Authorization': 'Basic %s' % b64_auth_str}

    apicall = "https://api.kiuwan.com/apps/analysis/" + analysis_code
    print ('Calling REST API [' , apicall , '] ...')
    response = requests.get(apicall, headers=headers)
    
    print (response)
    print ('Contenido' , response.content)
    jdata = json.loads(response.content)
    #print ('URL del analisis: ' , jdata['analysisURL'])
    return jdata['analysisURL']

def ExecuteKLA(cmd):
    print ('Executing [' , cmd , '] ...')
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

# Extract and download KLA from kiuwan.com (or from on-premise site)
DownloadAndExtractKLA(tmp_dir='/kla')

# Build the KLA CLI command
kla_bl_cmd = GetKLACmd(tmp_dir='/kla', mem=PARAM_KLA_MAXMEMORY)

# Execute CLA KLI
output, rc = ExecuteKLA(kla_bl_cmd)
if rc == 0:
    print ('{}{}'.format('KLA return code: ', rc))
    analysis_code = GetBLAnalysisCodeFromKLAOutput(output)
    print ('Analysis code [' , analysis_code , ']')
    os.environ ['RESULTCODE'] = analysis_code
    url_analysis = GetBLAnalysisResultsURL(analysis_code)
    print ('URL del analisis: ' , url_analysis)
    os.environ ['RESULTURL'] = url_analysis
else:
    print ('{}{}{}'.format('Analysis finished with error code [', rc, ']'))

#print environment, the results should be there
print (os.environ)

