# Quickstart

Let's set up the server for a simple "Hello World" command. See the more extensive [example](example.md) for a more real-world case which involves setting up permissions to execute commands like `docker`.

## Requirements

You need to have Python 3.7 (or higher) and a recent version of [Poetry](https://python-poetry.org) on your machine.

## Installation

Download or clone the repository, go to the project's root folder and install all requirements. For example:

```shell
git clone https://github.com/saltastroops/remote-command-server.git
cd remote-command-server
poetry install
```

## Creating the database

The server needs a Sqlite database with a projects and a tokens table. Conveniently, there is a command line tool `rcs` for creating it.

```shell
poetry shell
rcs initdb commands.sqlite3
```

The first line spawns a shell with the virtual environment activated, which we'll use in the following. If you don't want a new shell, you may use the following commands with `poetry run` instead. For example:

```shell
poetry run rcs initdb commands.sqlite3
```

Of course you can choose a file name other than `commands.sqlite3` or store the file in a different folder. As empty databases are a bit boring, let's add a project. We want to echo the string `Hello World`.

```shell
rcs project --database commands.sqlite3 --name hello-world --directory . --command "echo Hello World" 
```

You need a token to run a command with the server, so let's create one.

```shell
rcs token --database commands.sqlite3 --project hello-world 
```

The value of the database option must be the path of our database file, and the value of the project must be the name of the project we created in the previous step.

Make sure you copy the token - you won't be able to see it again, as only its hashed value is stored in the database.

## Setting up the server

Before starting the server you need to define an environment variable for its database file.

Environment variable | Description | Example value
--- | --- | ---
SQL_ALCHEMY_DATABASE_URL | DSN for the database file | sqlite:///./commands.sqlite3

!!! note
    The colon in the DSN is followed by three slashes for a relative file path and by four slashes for an absolute path. Forgetting a slash may lead to cryptic errors.

Sticking to the database we created above, we can set the environment variable as follows.

```shell
export SQL_ALCHEMY_DATABASE_URL=sqlite:///./commands.sqlite3
```

You can now launch the server with `uvicorn`.

```shell
uvicorn --port 8080 remote_command_server.main:app
```

## Running a command remotely

With the server up and running, you can now run the command by sending a POST request to the `/run` endpoint. The project name is passed as a path parameter, and the token is passed in the Authorization HTTP header (with the Bearer keyword). So to run the command we added above, we could use curl as follows.

```shell
curl -L -X POST -H "Authorization: Bearer token_value" http://localhost:8080/run/hello-world
```

The status of this request will be 200 if the remote command succeeds (i.e. returns with 0), and 500 otherwise.

## A word on security and permissions

Remember that the user running a web server should have minimal permissions to avoid security loopholes. For example, you would not want the server user to run arbitrary Docker commands. On the the other hand, the commands run by this server almost undoubtedly require more permissions, such as for building and running a Docker container.

A solution to this conundrum is to create a shell script and to give the server user sudo rights for this particular script. See the more extensive [example](example.md).
