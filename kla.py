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
print("EDUUUUUUUUUUUUUUUUUUUUUUUUU USERNAME:",PARAM_KLA_USERNAME) 
PARAM_KLA_PASSWORD = os.environ['INPUT_PASSWORD']
print("EDUUUUUUUUUUUUUUUUUUUUUUUUU PASSWORD:",PARAM_KLA_PASSWORD) 
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
def getBLAnalysisResultsURL(a_c, kla_user=PARAM_KLA_USERNAME, kla_password=PARAM_KLA_PASSWORD, advanced=PARAM_KLA_ADVANCEDPARAMS):
    apicall = "https://api.kiuwan.com"
    if not PARAM_KLA_BASEURL:
      apicall = PARAM_KLA_BASEURL + "/saas/rest/v1"
    
    apicall = apicall + "/apps/analysis/" + a_c
    print('Calling REST API [', apicall, '] ...')

    authString = base64.encodebytes(('%s:%s' % (kla_user,kla_password)).encode()).decode().strip()
    
    if "domain-id" in advanced:
      posDomain = advanced.find("domain-id")
      value_domain_id = advanced[posDomain+10:] ##remove domain-id word
      posWhitespace = value_domain_id.find(" ")
      if posWhitespace != -1:
        value_domain_id = value_domain_id[:posWhitespace]
      my_headers = {
          "Authorization": 'Basic {}'.format(authString),
          "X-KW-CORPORATE-DOMAIN-ID": value_domain_id
      }
    else:
      my_headers = {
        "Authorization": 'Basic {}'.format(authString)
      }
    response = requests.get(url=apicall,headers=my_headers)
    #response = requests.get(apicall, auth=requests.auth.HTTPBasicAuth(kla_user, kla_password))

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
kla_bl_cmd = getKLACmd(tmp_dir=TMP_EXTRACTION_DIR)

# Execute CLA KLI and set results as outputs
output, rc = executeKLA(kla_bl_cmd)
print("::set-output name=result::{}".format(rc))
print('{}{}'.format('KLA return code: ', rc))
if rc==0:
  analysis_code = getBLAnalysisCodeFromKLAOutput(output)
  print('Analysis code [', analysis_code, ']')
  url_analysis = getBLAnalysisResultsURL(analysis_code)
  #print traces and set output parameters...
  print('URL del analisis: ', url_analysis)
  print("::set-output name=analysisurl::{}".format(url_analysis))
  print('::set-output name=message::Analysis successful.')
elif rc == 1:
  print('::set-output name=message::Analyzer execution error.')
elif rc == 10:
  print('::set-output name=message::Audit overall result = FAIL.')
elif rc == 11:
  print('::set-output name=message::Invalid analysis configuration.')
elif rc == 12:
  print('::set-output name=message::The downloaded model does not support any of the discovered languages.')
elif rc == 13:
  print('::set-output name=message::Timeout waiting for analysis results.')
elif rc == 14:
  print('::set-output name=message::Analysis finished with an error in Kiuwan.')
elif rc == 15:
  print('::set-output name=message::Timeout: killed the subprocess.')
elif rc == 16:
  print('::set-output name=message::Baseline analysis not permitted for current user.')
elif rc == 17:
  print('::set-output name=message::Delivery analysis not permitted for current user.')
elif rc == 18:
  print('::set-output name=message::No analyzable extensions found.')
elif rc == 19:
  print('::set-output name=message::Error checking license.')
elif rc == 21:
  print('::set-output name=message::Invalid CLI parameter	.')
elif rc == 22:
  print('::set-output name=message::Access denied.')
elif rc == 23:
  print('::set-output name=message::Bad Credentials.')
elif rc == 24:
  print('::set-output name=message::Application Not Found.')
elif rc == 25:
  print('::set-output name=message::Limit Exceeded for Calls to Kiuwan API.')
elif rc == 26:
  print('::set-output name=message::Quota Limit Reached	.')
elif rc == 27:
  print('::set-output name=message::Analysis Not Found.') 
elif rc == 28:
  print('::set-output name=message::Application already exists.')
elif rc == 30:
  #we should not be here, this is a baseline
  print('::set-output name=message::Delivery analysis not permitted: baseline analysis not found.')
elif rc == 31:
  print('::set-output name=message::No engine available.')
elif rc == 32:
  print('::set-output name=message::Unexpected error	.')
elif rc == 33:
  print('::set-output name=message::Out of Memory.')
elif rc == 34:
  print('::set-output name=message::JVM Error	.')
else:
  print('::set-output name=message::No error message found.')

