#! /usr/bin/env python

"""Manages the data persistency.  For each storage, provides a dev and
production storage actions.

The model provide its user and holiday members.
"""

import datetime


class ConsistencyError(Exception):
    pass


def setModelMem():
    """Connects very simple memory model used for rapid debugging of other
    parts of the code.  This model servers also as a reference
    implementation.
    """
    import memorymodel
    global day, holiday, report, user
    day = memorymodel.Day()
    holiday = memorymodel.Holiday()
    report = memorymodel.WeeklyReport(day)
    user = memorymodel.User()


def setModelDatastore():
    """Connects gcloud datastore model.  This is the target production
    storage model.  You can debug it locally by starting gcloud
    datastorage emulator first using 'gcloud alpha emulators datastore
    start'"""
    import datastoremodel
    global day, holiday, report, user
    day = datastoremodel.Day()
    holiday = datastoremodel.Holiday()
    report = datastoremodel.WeeklyReport(day)
    user = datastoremodel.User()


def setModel(modelName):
    print "Setting model", modelName
    if modelName == 'mem':
        setModelMem()
    elif modelName == 'datastore':
        setModelDatastore()
    else:
        raise Exception('Unknown model name')


def timeToMin(aTime):
    """Converts expression HH:MM to minutes since day start."""
    tm = datetime.datetime.strptime(aTime, '%H:%M')
    return tm.hour*60 + tm.minute


def getDelta(dayInstance, userid, week):
    start = week.monday()
    end = week.sunday()
    days = dayInstance.getList(userid, start, end)
    vacation = 0
    flex = 0
    WORKDAY_MINUTES = 60*8
    # aggregate week data, consider sharing it with other models
    for day in days:
        flex += day['extra']
        # mirror frontend algorithm
        if day['type'] == 'vacation':
            vacation += 1
        elif day['type'] == 'work':
            flex += (timeToMin(day['departure']) -
                     timeToMin(day['arrival']) -
                     day['break'] - WORKDAY_MINUTES)
        elif day['type'] == 'flex':
            flex -= WORKDAY_MINUTES
    return flex, vacation


day = None
holiday = None
report = None
user = None
