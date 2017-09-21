#! /usr/bin/env python

"""Manages the data persistency.  For each storage, provides a dev and
production storage actions.

The model provide its user and holiday members.
"""


def setDevModel():
    import memorymodel
    global user, holiday
    user = memorymodel.User()
    holiday = memorymodel.Holiday()

user = None
holiday = None
