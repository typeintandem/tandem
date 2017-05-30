FROM ubuntu:16.04

# Install Utilities
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip \
  wget

# Install Chrome Beta (since we need Chrome 59 to use headless Chrome)
RUN \
  wget https://dl.google.com/linux/direct/google-chrome-beta_current_amd64.deb && \
  dpkg -i google-chrome-beta_current_amd64.deb; apt-get -fy install && \
  rm google-chrome-beta_current_amd64.deb

# Create tdm user
RUN useradd --create-home --shell /bin/bash tdm && \
  adduser tdm sudo

# Log in as tdm
USER tdm
WORKDIR /home/tdm
