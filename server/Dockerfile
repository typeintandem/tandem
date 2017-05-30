# Build image on top of Ubuntu 16.04 LTS
FROM ubuntu:16.04

# Install utilities
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip

# Install python dependencies
# NOTE: Path to input file needs to be relative to the tandem repository root
#       because images are built with the entire repository as "context" to
#       allow us to share files between different containers
COPY server/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN rm requirements.txt

# Create tdm user
RUN useradd --create-home --shell /bin/bash tdm && \
  adduser tdm sudo

# Log in as tdm
USER tdm
WORKDIR /home/tdm

# Expose port 8080 for HTTP requests
EXPOSE 8080
