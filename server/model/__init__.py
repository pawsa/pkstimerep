#! /usr/bin/env python

"""Manages the data persistency.  For each storage, provides a dev and
production storage actions.

The model provide its user and holiday members.
"""


def setDevModel():
    import memorymodel
    global day, holiday, report, user
    day = memorymodel.Day()
    holiday = memorymodel.Holiday()
    report = memorymodel.WeeklyReport()
    user = memorymodel.User()

day = None
holiday = None
report = None
user = None
