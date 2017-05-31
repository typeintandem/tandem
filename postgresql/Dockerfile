FROM ubuntu:16.04

# Install PostgreSQL 9.4
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" >> /etc/apt/sources.list.d/pgdg.list
RUN apt-get update && apt-get install -y wget
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update && apt-get install -y postgresql-9.4

# Switch to the postgres user
USER postgres

RUN /etc/init.d/postgresql start && \
  psql --command "CREATE USER tdm WITH SUPERUSER PASSWORD 'tdm';" && \
  createdb -O tdm tdm

# Adjust PostgreSQL configuration so that remote connections to the database are possible
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.4/main/pg_hba.conf && \
  echo "listen_addresses='*'" >> /etc/postgresql/9.4/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

# Make data, config, and logs persistent (kept in docker volumes)
VOLUME ["/var/lib/postgresql", "/etc/postgresql", "/var/log/postgresql"]

# Start PostgreSQL when the container is run
CMD [ \
  "/usr/lib/postgresql/9.4/bin/postgres", \
  "-D", "/var/lib/postgresql/9.4/main", \
  "-c", "config_file=/etc/postgresql/9.4/main/postgresql.conf" \
]
