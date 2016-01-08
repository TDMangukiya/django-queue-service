It turns out that with many web applications, its fairly common to want to do some longer-running background processing. Maybe that's looking up some data, doing some more intensive database work, or really just anything that you don't want to hold up a connection from the user.

At OSCON 2007, I was hunting around for exactly that sort of thing. Something to use to deal with background processing initiated from my web application. Not finding anything that I could immediately use and implement, I took it as a challenge to knock out something in the time I was there. The result was the beginning of this project: django queue service.

The Queue Service project is made available for your use and/or enjoyment. We welcome your feedback, thoughts, and issues! You can contact me directly, or join our mailing list -http://groups.google.com/group/django-queue-service/topics. If you've identified a bug or issue, please feel free to [put it into our issue tracker](http://code.google.com/p/django-queue-service/issues/entry).

If you'd like to get more deeply involved with this project, please don't hesitate to contact me.

For more general information, please dive into our wiki, starting at DjangoQueueService. If you just want to download and start rolling with it, take a look through HowToUseDjangoQueueService.