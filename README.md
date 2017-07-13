# Tandem

## Development Environment

We use Docker to manage dependencies in our development environment. Install
[Docker](https://www.docker.com/community-edition) to get started.

### Useful Commands

| Action                      | Command                                  |
|:----------------------------|:-----------------------------------------|
| Start all services          | `docker-compose up -d`                   |
| Shutdown all services       | `docker-compose down`                    |
| Tail logs (with timestamps) | `docker-compose logs -tf <service-name>` |

All images that need to be built will be built automatically when
`docker-compose up` is run for the first time.

To define a new service, add its definition in `docker-compose.yml`.

To add a new Docker image, create a `Dockerfile` in a new directory.
The name of the directory should be the name you want for the image.

**Note:** Containers are removed when you `exit` from them, so don't save
files outside of `~/tandem`.

## Frontend Client and Flow Recorder

### NPM Commands

Run the following commands within the `client/` folder.

* `npm install`: Install dependencies
* `npm run build-electron`: Build electron app
* `npm run watch-electron`: Build & watch electron app
* `npm run electron`: Run electron app
* `npm run build-web`: Build web app
* `npm start`: Build, watch, and serve web app on dev server
* `npm test`: Run tests
* `npm run clean`: Clean build folder
