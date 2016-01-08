# History #

At OSCON 2007, I was hunting around for something to use to deal with background processing initiated from my web application. Not finding anything that I could immediately use and implement, I took it as a challenge to knock out something in the time I was there. The result is the django queue service.

The project was released into the wild and [announced](http://www.rhonabwy.com/wp/2007/08/25/django-queue-service/) on August 25th, 2007.

The source also includes a file from the [CherryPy](http://www.cherrypy.org/) project - the [WSGIServer from CherryPy 3.0.1](http://www.cherrypy.org/browser/tags/cherrypy-3.0.1/cherrypy/wsgiserver/__init__.py). [Mark Ramm](http://www.compoundthinking.com/blog/) (from the TurboGears project) had suggested in his OSCON presentation that CherryPy had a nice WSGI Server, and after chatting with him I was curious if I could hook up a Django project into it. This project, being conceived there, was handy...

[Brad Fitzpatrick](http://bradfitz.com/) pointed me towards a project called [TheSchwartz](http://code.sixapart.com/svn/TheSchwartz) (which also had a presentation at OSCON 2007, but I didn't make it to that session), but I'd found out about it after I had already written the code and nailed down the basic functionality.