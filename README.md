# UCR-Food
Creates and stores objects based on dining hall menus at UC Riverside.

This is a never-ending (seemingly) side project of mine. It mainly 
accomplishes these goals:
1. Gives me something work on when I'm bored.
2. Experience with creating fast data processing pipelines in Python.
3. Experience in creating and maintaining a highly modular Python application.

## Requirements:

### Docker:
Install Docker and Docker Compose.
```bash
# Ubuntu:
$ apt-get install docker
$ sudo pip install docker-compose

# Mac OS:
$ brew install docker

# Finally, create a directory to store RethinkDB data.
$ mkdir /data && chown -R $(whoami) /data
```

### Virtualenv:
Install `python3.6`, `pip`, and `RethinkDB`. Then install virtualenv.

```bash
# Ubuntu:
$ apt-get install python3 python3-pip rethinkdb

# Mac OS:
$ brew install python3 rethinkdb

# Finally, on your system run:
$ python3 -m pip install virtualenv
```

## Running the Server:
**WARNING:** Project isn't finished yet. Things *will not* work.

### Using Docker:

Just run these two simple commands:

```bash
$ docker-compose build
$ docker-compose up -d
```

### Using virtualenv:

To get setup, simply run the `rethinkdb` database (preferably in the 
same directory) *first* and then run the actual server (shown below). 
Several scripts and a Makefile have been created to facilitate this.

```bash
$ cd UCR-Food/virtualenv
$ make configure
$ source ../venv/bin/activate
(venv) $ make install
(venv) $ python3 app.py
```