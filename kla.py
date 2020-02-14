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
from pathlib import Path

# print environment, the results should be there
# print("--------------------- ENVIRONMENT ------------------------")
# print (os.environ)
# print("--------------------- ENVIRONMENT ------------------------")

# Params used in the call to the baseline analysis.
# All the parameters set in the action are stored as environment variables with INPUT_ prefix
PARAM_KLA_BASEURL = os.environ['INPUT_KIUWANBASEURL']
PARAM_KLA_USERNAME = os.environ['INPUT_USERID']
PARAM_KLA_PASSWORD = os.environ['INPUT_PASSWORD']
PARAM_KLA_APPNAME = os.environ['INPUT_PROJECT']
PARAM_KLA_SOURCEDIR = os.environ['GITHUB_WORKSPACE']
PARAM_KLA_DATABASETYPE = os.environ['INPUT_DATABASETYPE']
PARAM_KLA_ADVANCEDPARAMS = os.environ['INPUT_ADVANCEDPARAMS']

KLA_URL = PARAM_KLA_BASEURL + '/pub/analyzer/KiuwanLocalAnalyzer.zip'
TMP_EXTRACTION_DIR = os.environ['WORKSPACE'] + '/kla'
KLA_EXE_DIR = TMP_EXTRACTION_DIR + "/KiuwanLocalAnalyzer/bin"

# Function to create the Kiuwan KLA line command.
# It is created with the minimum amount of parameters. Then the advanced parameters are passed in, the User is responsible for a good format
# Note the memory parameter has been already created properly
def getKLACmd(tmp_dir=TMP_EXTRACTION_DIR,
              appname=PARAM_KLA_APPNAME,
              sourcedir=PARAM_KLA_SOURCEDIR,
              user=PARAM_KLA_USERNAME,
              password=PARAM_KLA_PASSWORD,
              dbtype=PARAM_KLA_DATABASETYPE,
              advanced=PARAM_KLA_ADVANCEDPARAMS):
    prefix = tmp_dir + '/KiuwanLocalAnalyzer/bin/'
    agent = prefix + 'agent.sh'
    os.chmod(agent, stat.S_IRWXU)

    klablcmd = '{} -c -n {} -s {} --user {} --pass {} transactsql.parser.valid.list={} {}'.format(agent, appname, sourcedir, user, password, dbtype, advanced)
    return klablcmd

# Function to download and extract the Kiuwan Local Analyzer from kiuwan server
# TODO: parametrize the URL to support Kiuwan on premises installations
def downloadAndExtractKLA(tmp_dir=TMP_EXTRACTION_DIR, klaurl=KLA_URL):
    print('Downloading KLA zip from ', klaurl, ' at [', os.getcwd(), ']', '...')
    resp = urllib.request.urlopen(klaurl)
    zipf = zipfile.ZipFile(io.BytesIO(resp.read()))
    for item in zipf.namelist():
        print("\tFile in zip: ", item)

    print('Extracting zip to [', tmp_dir, ']', '...')
    # Luis: para probar crear dirs
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    zipf.extractall(tmp_dir)

# Parse the output of the analysis resutl to get the analysis code
def getBLAnalysisCodeFromKLAOutput(output_to_parse):
    return output_to_parse.split("Analysis created in Kiuwan with code:", 1)[1].split()[0]


# Function to call the Kiuwan API to get the actual URL
def getBLAnalysisResultsURL(a_c, kla_user=PARAM_KLA_USERNAME, kla_password=PARAM_KLA_PASSWORD):
    apicall = "https://api.kiuwan.com"
    if not PARAM_KLA_BASEURL:
      apicall = PARAM_KLA_BASEURL + "/saas/rest/v1"
    
    apicall = apicall + "/apps/analysis/" + a_c"
    print('Calling REST API [', apicall, '] ...')

    response = requests.get(apicall, auth=requests.auth.HTTPBasicAuth(kla_user, kla_password))

    print(response)
    print('Contenido', response.content)
    jdata = json.loads(response.content)
    # print ('URL del analisis: ' , jdata['analysisURL'])
    return jdata['analysisURL']

# Function to excetute the actual Kiuwan Local Analyzer command line and get the resutls.
def executeKLA(cmd):
    print('Executing [', cmd, '] ...')
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    # (output, err) = pipe.communicate()
    output_text = ''
    try:
      nextline = pipe.stdout.readline()
      while (pipe.poll() == None):
            output_text = output_text + nextline.decode('utf-8')
            sys.stdout.write(nextline.decode('utf-8'))
            sys.stdout.flush()
            nextline = pipe.stdout.readline()
    except KeyboardInterrupt:
        print("Keyboard interrupt... why??")
        return output_text, pipe.returncode
        
    #return_code = pipe.wait()
    return output_text, pipe.returncode

# Actual executing code after defining the functions
# Extract and download KLA from kiuwan.com (or from on-premise site)
downloadAndExtractKLA(tmp_dir=TMP_EXTRACTION_DIR)

# Build the KLA CLI command
kla_bl_cmd = getKLACmd(tmp_dir=TMP_EXTRACTION_DIR, mem=PARAM_KLA_MAXMEMORY)

# Execute CLA KLI and set results as outputs
output, rc = executeKLA(kla_bl_cmd)
print("::set-output name=result::{}".format(rc))
if rc == 0:
    print('{}{}'.format('KLA return code: ', rc))
    analysis_code = getBLAnalysisCodeFromKLAOutput(output)
    print('Analysis code [', analysis_code, ']')
    url_analysis = getBLAnalysisResultsURL(analysis_code)
    print('URL del analisis: ', url_analysis)
    print("::set-output name=analysisurl::{}".format(url_analysis))
else:
    print('{}{}{}'.format('Analysis finished with error code [', rc, ']'))

