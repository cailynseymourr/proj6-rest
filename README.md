# Project 6: Brevet Time Calculator Service

**Author:** Cailyn Seymour
**Email:** cailyn@uoregon.edu

## Description

A brevet control time calculator (from project 5) with a RESTful service that exposes the stored times from MongoDB. The calculator saves control times to the database with the Submit button, the REST API serves them as JSON or CSV, and a separate consumer page displays them.

## Running the project

From the `DockerRestAPI` folder:

```
docker compose up --build
```

| Service | URL | What it is |
|---|---|---|
| `brevets` | http://localhost:5002 | Calculator with Submit and Display buttons |
| `laptop-service` | http://localhost:5001 | REST API |
| `website` | http://localhost:5000 | Consumer program (PHP) |
| `db` | (internal) | MongoDB |

To use it, open the calculator, enter some control distances, and click Submit. The API and consumer then read what was stored.

## API

JSON is the default format for the three basic APIs.

- `/listAll`: all open and close times
- `/listOpenOnly`: open times only
- `/listCloseOnly`: close times only

Add `/json` or `/csv` to choose a format, for example `/listAll/csv` or `/listOpenOnly/json`.

Add `?top=k` to get only the first k times in ascending order, for example `/listOpenOnly/csv?top=3` or `/listCloseOnly/json?top=4`.

## Consumer

`website/index.php` runs in its own `php:apache` container and calls the REST API in the `laptop-service` container. It displays all times, open times only, and the top 3 close times.

## Project structure

- `DockerRestAPI/brevets/`: calculator app from project 5 (Flask)
- `DockerRestAPI/laptop/`: REST API (Flask-RESTful)
- `DockerRestAPI/website/`: consumer program (PHP)
- `DockerRestAPI/docker-compose.yml`: runs all four containers