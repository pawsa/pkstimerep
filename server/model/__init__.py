#! /usr/bin/env python

"""Manages the data persistency.  For each storage, provides a dev and
production storage actions.

The model provide its user and holiday members.
"""


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
    report = memorymodel.WeeklyReport()
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
    report = datastoremodel.WeeklyReport()
    user = datastoremodel.User()


def setModel(modelName):
    if modelName == 'mem':
        setModelMem()
    elif modelName == 'datastore':
        setModelDatastore()
    else:
        raise Exception('Unknown model name')

day = None
holiday = None
report = None
user = None
