# UCR-Food
Creates and stores objects based on dining hall menus at UC Riverside.

This project is a bit of a pet project of mine. It has no real purpose
other than for me to work on something.

## Requirements:
Before you install, make sure you have at least `python3.4`, `pip3`, 
`virtualenv`, and `RethinkDB` installed. If you have a Mac, you also 
need [homebrew](brew.sh).

### Linux:
`$ [sudo] apt-get install python3 python3-pip rethinkdb`

`$ [sudo] python3 -m pip install virtualenv`

### Mac OS:
`$ brew install python3 rethinkdb`

`$ python3 -m pip install virtualenv`

## Running the Server:
**WARNING:** Project isn't finished yet. Things *will not* work.

To get setup, simply run the `rethinkdb` database (preferably in the 
same directory) *first* and then run the actual server (shown below). 
Several scripts and a Makefile have been created to facilitate this.

```bash
$ cd UCR-Food/
$ make configure
$ source venv/bin/activate
(venv) $ make install
(venv) $ ./main.py
```