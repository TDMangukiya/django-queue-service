#!/bin/bash
PROJECTPATH=/Users/$USER/Desktop
PROJECT=qs
export DJANGO_SETTINGS_MODULE="$PROJECT".settings
export PYTHONPATH=$PROJECTPATH:$PYTHONPATH:
cd $PROJECTPATH/$PROJECT
export PATH=$PATH:/opt/local/Library/Frameworks/Python.framework/Versions/2.4/lib/python2.4/site-packages/django/bin/
