# Container image that runs kiuwan
FROM alpine:3.10

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY baseline.sh /baseline.sh

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/baseline.sh"]
