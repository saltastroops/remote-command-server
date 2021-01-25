# An example

The following assumes that the server has been installed as described in the [quickstart quide](quickstart.md#installation)

## Creating the scripts and setting up permissions

Let's assume we want to remotely list all our running Docker containers and (separately) images and store the results in a temporary file. Start by creating a file `list-containers.sh` with the following content.

```shell
#!/bin/bash

/usr/bin/docker container ls > /tmp/running-docker-containers.txt
```

Also create a file `list-images.sh`.

```shell
#!/bin/bash

/usr/bin/docker image ls > /tmp/docker-images.txt
```

Ensure these scripts can be executed by the server user.

```shell
chmod a+x list-containers.sh list-images.sh
```

To keep things neat and tidy we create a group for handling the necessary permissions.

```shell
sudo groupadd remotecommands
```

You have to add the user to this group.

```shell
sudo adduser www-data remotecommands
```


Create the file `/etc/sudoers.d/remotecommands` and open it with `visudo`.

```shell
sudo visudo -s -f /etc/sudoers.d/remotecommands
```

!!! warning
    Errors in sudo files may render `sudo` unusable. Never use a normal text editor to create or update them.

Add the following content to file (with the correct absolute paths for your script files).

```shell
Cmnd_Alias    LIST_CONTAINERS = /path/to/list-containers.sh
Cmnd_Alias    LIST_IMAGES = /path/to/list-images.sh
Cmnd_Alias    REMOTE_COMMANDS_ALL = LIST_CONTAINERS, LIST_IMAGES
%remotecommands ALL=NOPASSWD: REMOTE_COMMANDS_ALL
```

The server user should now be able to run our scripts.

```shell
sudo -u www-data sudo /path/to/list-containers.sh
sudo -u www-data sudo /path/to/list-images.sh
```

!!! tip
    If you are asked for the password of the server user, check that you have used your own path instead of `/path/to` in the sudo file and these commands, and that there are no typos.

## Setting up the server

We can now create our database, the two projects and tokens for them.

```shell
# in the root folder of the server code
poetry shell
rcs initdb commands.sqlite3
rcs project -n list-docker-containers -d /tmp -c "sudo /path/to/list-containers.sh" --db sqlite:///./commands.sqlite3
rcs project -n list-docker-images -d /tmp -c "sudo /path/to/list-images.sh" --db sqlite:///./commands.sqlite3
rcs token -p list-docker-containers --db sqlite:///./commands.sqlite3
```

Note the `sudo` in the commands, and remember to replace `/path/to` with the correct path.

With all this in place we can finally launch the server.

```shell
SQL_ALCHEMY_DATABASE_URL=commands.sqlite3 uvicorn remote_command_server.main:app
```

## Running the commands

Finally we can remotely list our Docker containers and images.

```shell
curl -L -X POST -H "Authorization: Bearer abcd1234" http://localhost:8080/run/list-docker-containers
curl -L -X POST -H "Authorization: Bearer efgh5678" http://localhost:8080/run/list-docker-images
```

Of course you need to replace `abcd1234` and `efgh5678` with the correct token values.
