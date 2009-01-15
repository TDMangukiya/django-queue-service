1. Checkout the unstable branch to a local directory called `qs`:

svn co http://django-queue-service.googlecode.com/svn/branches/unstable/ qs

If you're reading these instructions from an already checked out directory called something other than qs, simply rename it to qs.

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

7. Read the documentation in the qs/docs directory for API information.

Settings:
==========

* To view the web server's configurable parameters, run:

python manage.py help runhttp

* See the bottom of qs/settings.py to view or change default settings.


