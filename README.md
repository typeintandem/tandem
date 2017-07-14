Tandem
======

Development Environment
-----------------------
We use Docker to manage dependencies in our development environment. Install
[Docker](https://www.docker.com/community-edition) to get started.

**Useful commands:**

| Action                      | Command                                  |
|:----------------------------|:-----------------------------------------|
| Start all services          | `docker-compose up -d`                   |
| Shutdown all services       | `docker-compose down`                    |
| Tail logs (with timestamps) | `docker-compose logs -tf <service-name>` |
| List all containers         | `docker ps`                              |
| Start bash in a container   | `docker exec -it <container> /bin/bash`  |

All images that need to be built will be built automatically when
`docker-compose up` is run for the first time.

To define a new service, add its definition in `docker-compose.yml`.

To add a new Docker image, create a `Dockerfile` in a new directory.
The name of the directory should be the name you want for the image.

**Note:** Containers are removed when you `exit` from them, so don't save
files outside of `~/tandem`.
