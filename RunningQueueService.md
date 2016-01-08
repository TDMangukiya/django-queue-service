# Introduction #

These are instructions for setting up and running an instance Django Queue Service. This shows just the basic setup of a simple queue server, using SQLite and the provided pure-python WSGIServer. More complex setups can certainly be made, and I recommend looking at Chapter 20 of the Django Book ([Deploying Django](http://djangobook.com/en/1.0/chapter20/)).

These instructions presume that you have Python 2.5 and subversion available on the system that you're using to set up the service. Django Queue Service relies on updates to the Django framework beyond the current release (0.96.1 as I write this), so we'll need to use Django from it's source.

# Details #

  * Install Django
    * `svn checkout http://code.djangoproject.com/svn/django/trunk/ django_src`
    * `cd django_src`
    * `python setup.py install`
  * Get a copy of the Django Queue Service
    * make a directory for the service to run within: `mkdir queueservice`
    * `cd queueservice`
    * `svn checkout http://django-queue-service.googlecode.com/svn/trunk .`
  * Set up the database, initialize the service
    * `cd qs`
    * `python manage.py syncdb`
  * Edit the configuration
    * edit the file settings.py using your prefered editor (e.g. `vi settings.py`)
    * set DQS\_HOST to the host name or IP address you wish to have respond to the service.
      * if you want to listen on all interfaces, set it to "0.0.0.0"
    * set DQS\_PORT to the port you wish to have respond (default is port 8000)
  * Run the service
    * `cd ..` (you should be in the queueservice directory)
    * run the script "runserver" `runserver.bash` or `runserver.bat`