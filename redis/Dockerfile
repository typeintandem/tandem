FROM ubuntu:16.04

# Install utilities
RUN apt-get update && apt-get install -y \
  build-essential \
  wget

# Create tdm user
RUN useradd --create-home --shell /bin/bash tdm && \
  adduser tdm sudo

# Log in as tdm
USER tdm
WORKDIR /home/tdm

# Download and build redis 3.2.9
RUN wget http://download.redis.io/releases/redis-3.2.9.tar.gz && \
  tar xzf redis-3.2.9.tar.gz && \
  cd redis-3.2.9 && \
  make

# Use our own configuration
COPY redis/redis.conf /home/tdm/redis.conf

# Redis is configured to persist its data here
RUN mkdir /home/tdm/data

# Make sure the data is persisted across container restarts
VOLUME ["/home/tdm/data"]

# Redis uses port 6379
EXPOSE 6379

# Start redis automatically
CMD ["/home/tdm/redis-3.2.9/src/redis-server", "/home/tdm/redis.conf"]
