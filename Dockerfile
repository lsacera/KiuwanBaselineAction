# Container image that runs kiuwan, uses the alpine image with openjdk installed
FROM openjdk:8-jre-alpine

#download kiuwan local analyzer to home and unzip it
RUN mkdir /kla && wget https://www.kiuwan.com/pub/analyzer/KiuwanLocalAnalyzer.zip && unzip KiuwanLocalAnalyzer.zip -d /kla/.

#Install python environment
# Ref: https://github.com/micktwomey/docker-python2.7/blob/master/Dockerfile
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    ca-certificates \
    gcc \
    git \
    libpq-dev \
    make \
    python-pip \
    python2.7 \
    python2.7-dev \
    ssh \
    && apt-get autoremove \
    && apt-get clean

RUN pip install -U "setuptools==3.4.1"
RUN pip install -U "pip==1.5.4"
RUN pip install -U "Mercurial==2.9.1"
RUN pip install -U "virtualenv==1.11.4"

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY baseline.sh /baseline.sh

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/baseline.sh"]
