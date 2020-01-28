#!/bin/sh -l

time=$(date)
echo ::set-output name=time::$time

#checking if java is installed in the image
echo "Checking the JRE Version"
java -version

#checking some env variables passed to docker run
echo $INPUT_PROJECT
echo $INPUT_LABEL
echo $INPUT_USERID
echo $INPUT_PASSWORD
echo $GITHUB_WORKFLOW
echo $INPUT_REPOSITORY

#checking the passed parameters 
echo $1
echo $2
echo $3
echo $4
