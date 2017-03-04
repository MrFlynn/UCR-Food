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

First, create a virtualenv and enter it:

`$ virtualenv -p $(which python3) venv && source venv/bin/activate`

Next, install the dependencies:

`(venv) $ make install`

Finally, run the actual server:

`(venv) $ ./main.py`