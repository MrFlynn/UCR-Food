# UCR-Food
Creates and stores objects based on dining hall menus at UC Riverside.

This project is a bit of a pet project of mine that. It has no real purpose
other than for me to work on something.

## Requirements:
Before you install, make sure you have at least `python3.4`, `pip`, and 
`virtualenv` installed. If you have a Mac, you also need [homebrew](brew.sh).

### Linux:
`$ [sudo] apt-get install python3 python3-pip`
`$ [sudo] python3 -m pip install virtualenv`

### Mac OS:
`$ brew install python3`
`$ python3 -m pip install virtualenv`

## Install:
**WARNING:** Project isn't finished yet. Things *will not* work.

First, create a virtualenv and enter it:
`$ virtualenv venv && source venv/bin/activate`

Next, install the dependencies:
`$ make install`