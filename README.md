# SAAO Deployment Server

A simple deployment server for Docker-based projects.

## Deploying Docker based projects

The idea of this server is to provide a simple way of initiating deployment as part of a CI/CD process. You deploy by sending a POST request to the deployment server, which will then

* check that you are allowed to deploy
* initiate a `git pull` for the project
* run a command for the project

Authorisation is checked by means of a token. The command to execute is stored in the server's Sqlite3 database file.

## Running the server

You can run the server by executing

```shell
uvicorn saao_deployment_server.main:app --port 1234
```

where you can replace 1234 with the poret of your choice. The server requires the following environment variable to be set:

Environment variable | Description | Example
--- | ---
DATABASE_FILE | Path of the Sqlite3 database file | /path/to/db.sqlite3

