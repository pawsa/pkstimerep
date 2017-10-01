#! /usr/bin/env python

"""Provides User and Holiday classes with the required methods. The
objects are persisted in GCP datastore."""

from passlib.hash import pbkdf2_sha256
import datetime
import isoweek

from google.appengine.api import users
from google.appengine.ext import ndb

from . import ConsistencyError, getDelta


def timeToMin(aTime):
    """Converts expression HH:MM to minutes since day start."""
    tm = datetime.datetime.strptime(aTime, '%H:%M')
    return tm.hour*60 + tm.minute


def pkstr_key(userid):
    """Constructs a Datastore key for a Time report entity
    """
    return ndb.Key('UserTimeReport', userid)


class DbDay(ndb.Model):
    date = ndb.DateProperty(indexed=True, required=True)
    data = ndb.JsonProperty(indexed=False, required=True)


class DbUser(ndb.Model):
    """Stores email as id"""
    pwhashed = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    # status is usually just active or disabled
    status = ndb.StringProperty(indexed=True)


class DbWeeklyReport(ndb.Model):
    year = ndb.IntegerProperty(indexed=False)
    week = ndb.IntegerProperty(indexed=False)
    vacation = ndb.IntegerProperty(indexed=False)
    flex = ndb.IntegerProperty(indexed=False)  # in minutes


class Day:
    """provides getList, add, update methods"""

    def getList(self, userid, start, end):
        """Lists days for given user, withing given date interval.
        @type userid: str
        @param userid: id of the user for which to list the data.
        @type start: datetime.date
        @param start: starting day (inclusive)
        @type end: datetime.date
        @param end: ending day (inclusive)
        """
        assert type(start) == datetime.date
        assert type(end) == datetime.date
        days_query = (DbDay.query(ancestor=pkstr_key(userid))
                      .filter(DbDay.date >= start, DbDay.date <= end)
                      .order(DbDay.date))
        days = days_query.fetch(31)
        retlist = []
        for day in days:
            data = {'date': day.date}
            data.update(day.data)
            retlist.append(data)
        return retlist

    def update(self, userid, day, dayData):
        """Upserts given day data for the given user.
        @type userid: str
        @param userid: id of the user for which to list the data.
        @type day: datetime.date
        @param day: the day for which update the day
        @type dayData: dict
        @param dayData: the data to be inserted for given day,
        replacing any former data
        """
        assert type(day) == datetime.date
        newDay = DbDay(parent=pkstr_key(userid),
                       id=str(day), date=day, data=dayData)
        del newDay.data['date']
        newDay.put()
        return dayData

    def delete(self, userid, day):
        key = (DbDay.query(ancestor=pkstr_key(userid), keys_only=True)
               .filter(DbDay.date == day)).get()
        key.delete()


class User(ndb.Model):
    """provides getList, add, update methods"""
    def __init__(self):
        self.users = {'admin@example.com': {
            'email': 'admin@example.com',
            'pwhashed': pbkdf2_sha256.hash('admin'),
            'status': 'active'}
        }

    def getList(self):
        user_query = DbUser.query()
        users = user_query.fetch(31)  # fixme
        retlist = []
        for user in users:
            data = {'email': user.key.id(), 'name': user.name,
                    'status': user.status}
            retlist.append(data)
        return retlist

    def add(self, data):
        newUser = DbUser(id=data['email'])
        newUser.name = data['name']
        newUser.status = data['status']
        newUser.pwhashed = pbkdf2_sha256.hash(data['password'])
        newUser.put()
        return {'email': data['email'], 'name': data['name'],
                'status': data['status']}

    def update(self, userid, userData):
        user_query = ndb.Key('DbUser', userid)
        user = DbUser.get()
        if 'name' in userData:
            user.name = userData['name']
        if 'status' in userData:
            user.status = userData['status']
        if 'password' in userData:
            user.pwhashed = pbkdf2_sha256.hash(userData['password'])
        user.put()

    def auth(self, userid, password):
        user = ndb.Key('DbUser', userid).get()
        return pbkdf2_sha256.verify(password, user.pwhashed)


class Holiday:
    """provides getList, add, update, delete methods"""
    def __init__(self):
        pass

    def getList(self, year):
        retlist = []
        return retlist

    def add(self, data):
        pass

    def update(self, hid, data):
        raise Exception('holiday not found')

    def delete(self, hid):
        """Returns true if the id was found
        @type hid: int
        @param hid: integer id of the holiday
        """
        return False


class WeeklyReport:
    """provides a list of weekly reports for the user. Weekly report is
    essentially just an overtime status measured in minutes."""

    def __init__(self, dayInstance):
        self.dayInstance = dayInstance

    def getList(self, userid, start, count=None):
        """returns list segment [start:start+count], sorted by time in a
        descending order."""
        report_query = (DbWeeklyReport.query(ancestor=pkstr_key(userid))
                        .order(-DbWeeklyReport.key))
        reports = report_query.fetch(31 if count is None else count)  # fixme
        retlist = []
        for r in reports:
            data = {'year': r.year, 'week': r.week, 'flex': r.flex,
                    'vacation': r.vacation}
            retlist.append(data)
        return retlist

    def add(self, userid, isoYear, isoWeek):
        """@note: This is the place to execute the consistency checks to the
        best of the capabilites provided by the storage."""
        week = isoweek.Week(isoYear, isoWeek)
        key = week.isoformat()
        flex, vacation = getDelta(self.dayInstance, userid, week)
        prevInDb = (DbWeeklyReport.query(ancestor=pkstr_key(userid))
                    .order(-DbWeeklyReport.key).get())
        prevWeek = week-1
        if prevInDb:
            if not (prevInDb.year == prevWeek.year and
                    prevInDb.week == prevWeek.week):
                raise ConsistencyError('locked weeks must be continouos')
            flex += prevInDb.flex
            vacation += prevInDb.vacation
        report = DbWeeklyReport(parent=pkstr_key(userid), id=key,
                                year=isoYear, week=isoWeek,
                                flex=flex, vacation=vacation)
        report.put()
        return {}

    def delete(self, userid, year, week):
        pass
