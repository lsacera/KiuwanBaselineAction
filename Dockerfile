# Container image that runs kiuwan, uses the alpine image with openjdk installed
#FROM openjdk:8-jre-alpine
FROM openkbs/jre-mvn-py

#download kiuwan local analyzer to home and unzip it
#RUN mkdir /kla && wget https://www.kiuwan.com/pub/analyzer/KiuwanLocalAnalyzer.zip && unzip KiuwanLocalAnalyzer.zip -d /kla/.

# Copies your code file from your action repository to the filesystem path `/` of the container
#COPY baseline.sh /baseline.sh

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY kla.py /kla.py 

# Code file to execute when the docker container starts up (`entrypoint.sh`)
RUN wget https://bootstrap.pypa.io/get-pip.py && chmod +x ./get-pip.py && ./get-pip.py && pip install requests 

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["python", "/kla.py"]

