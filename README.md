Installation
-------------------
Prerequisites for Mac OS:
Make sure you have the XCode development environment and the Development Command Line Tools.  They can be downloaded from https://developer.apple.com/downloads/index.action, you need Xcode 4.6 or higher, and "Command Line Tools" for your version of your OS.

Prerequisites for Linux:
Make sure you have python 2.6 or higher installed (it should be).  You can check by running "python" and looking at the first line.  Also make sure you have python-setuptools by seeing if the command "easy_install" is available.  If that command fails to run, try going to http://pypi.python.org/pypi/setuptools

Step 1:
Make sure you have pip and virtualenv installed by doing:

  > sudo easy_install pip virtualenv
  ...
  Finished processing dependencies for virtualenv

Step 2:
In the project root, create a python virtual environment named "env".

  > virtualenv env
  New python executable in env/bin/python
  Installing setuptools............done.
  Installing pip...............done.

Step 3:
If not done already, install libevent library.  If you have homebrew installed on mac, you can do:
> brew install libevent

Step 4:
Install the project requirements.  Make sure you see "Successfully installed ..." at the end.  Otherwise check troubleshooting, below.

  > env/bin/pip install -r requirements.txt
  ...
  Successfully installed Django
  Cleaning up...

Step 5:

  > ./manage.py syncdb
  Ceating tables ...
  ...
  Would you like to create one now? (yes/no):

It will ask you to create a user, go ahead and create one for yourself.  That user will only be local to *your* machine so don't expect it to be anywhere else.  If this fails, or you want to create a user later see "Creating An Admin User Via The Command Line", below.  Also, there is by default a user with email "admin@designforamerica.com" and password "pass".


STEP 6: 
Load testing data, specifically the games and users
> ./manage.py loaddata users
> ./manage.py loaddata games


Step 7:
  
  > ./manage.py runserver
  ...
  Development server is running at http://127.0.0.1:8000/
  Quit the server with CONTROL-C.

This will start up the server, running.  Visit http://127.0.0.1:8000/ in your browser now.
Changes you make should automatically update the server, but if sometimes it needs to be rebooted.


Step 8:
  To run the playpolitics game, you need to run sockets -- on your local development environment, instead of using runserver, you can use:

  > ./manage.py runserver_socketio


Step 9: 
  Sign in on one browser with admin/pass and another browser with matt/pass



Troubleshooting
-----------------------------
Sometimes after step 3 "env/bin/pip install -r requirements.txt"


SETUP State of Nature
-------------------------
Name:         State of Nature
Dir:          playpolitics
Repository:   git@github.com:Dan-org/playpolitics.git

