#!/bin/sh -l

echo "Hello $1"
time=$(date)
echo ::set-output name=time::$time

#checking if java is installed in the image
java -version


