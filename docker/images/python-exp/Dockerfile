FROM ubuntu:16.04

# Install Utilities
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip

# Create tdm user
RUN useradd --create-home --shell /bin/bash tdm
RUN adduser tdm sudo

# Log in as tdm
USER tdm
WORKDIR /home/tdm
