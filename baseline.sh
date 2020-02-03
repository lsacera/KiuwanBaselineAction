#!/bin/sh -l

# Step 1: Download Kiuwan local analyzer
wget https://www.kiuwan.com/pub/analyzer/KiuwanLocalAnalyzer.zip
# Step 2: Unzip Kiuwan local analyzer
unzip KiuwanLocalAnalyzer.zip -d $HOME/.
# Step 3: Copy the configuration file to the kiuwan local analyzer folder
cp /analyzer.properties $HOME/KiuwanLocalAnalyzer/conf/.
# Step 4:Execute Kiuwan Baseline. 
# TODO: remove the echoes in a later release
echo "Executing analyzer with: "
echo "--user " $INPUT_USERID 
echo "--pass " $INPUT_PASSWORD
echo "--sourcePath" $GITHUB_WORKSPACE 
echo "--softwareName" $INPUT_PROJECT 
echo "--create"
echo "--label " $INPUT_LABEL
$HOME/KiuwanLocalAnalyzer/bin/agent.sh --user $INPUT_USERID --pass $INPUT_PASSWORD --sourcePath \"$GITHUB_WORKSPACE\" --softwareName \"$INPUT_PROJECT\" --create --label \"$INPUT_LABEL\"
