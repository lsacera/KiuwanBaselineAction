# Container image that runs kiuwan, uses image with Ubuntu + openjdk 8 + python3
FROM openkbs/jdk-mvn-py3

# Copies the python script to perform the Baseline analysis
COPY kla.py /kla.py 

# Code file to execute when the docker container starts up, python script
#ENTRYPOINT ["python3", "/kla.py"]
CMD ["python3","/kla.py"]
