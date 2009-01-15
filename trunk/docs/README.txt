1. Checkout the trunk to a local directory called `qs`:

svn checkout http://django-queue-service.googlecode.com/svn/trunk/ qs

If you're reading these instructions from an already checked out directory called something other than qs, simply rename it to `qs` or adjust the following instructions to suit your directory name.

2. Change to qs directory:

cd qs

3. Run unit tests to verify installation:

python manage.py test

4. Create SQLite3 database:

python manage.py syncdb

5. Run built-in CherryPy server:

python manage.py runhttp

6. Verify that DQS is running by opening a browser window to:

http://localhost:8000/?format=text

You should see an empty list ("[]") as there are no queues in the system at this point.

7. Hit Ctrl-C to stop the server.

8. Read help on running the server in daemon mode and other options with:

python manage.py runhttp --help

9. Read the documentation in the qs/docs directory for API specs.

Settings:
==========

* To view the web server's configurable parameters, run:

python manage.py help runhttp

* See the bottom of qs/settings.py to view or change default settings.


