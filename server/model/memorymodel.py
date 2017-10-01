#! /usr/bin/env python

"""Provides Day, User, Holiday, and WeeklyReport classes with the required
methods.
"""

from passlib.hash import pbkdf2_sha256

import collections
import datetime
import isoweek
import re

from . import ConsistencyError, getDelta


class Day:
    """provides getList, add, update methods"""
    def __init__(self):
        self.days = collections.defaultdict(list)

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
        return [d for d in self.days[userid] if start <= d['date'] <= end]

    def update(self, userid, day, dayData):
        """Upserts given day data for the given user.
        @type userid: str
        @param userid: id of the user for which to list the data.
        @type day: datetime.date
        @param day: the day for which update the day
        @type dayData: dict
        @param dayData: the data to be inserted for given day,
        replacing any former daya
        """
        assert type(day) == datetime.date
        userDays = self.days[userid]
        for d in userDays:
            if d['date'] == day:
                d.update(dayData, date=day)
                return d
        self.days[userid].append(dict(dayData, date=day))
        return self.days[userid][-1]

    def delete(self, userid, day):
        for d in self.days[userid]:
            if d['date'] == day:
                del d['date']
                return True
        return False


class User:
    """provides getList, add, update methods"""
    def __init__(self):
        self.users = {'admin@example.com': {
            'email': 'admin@example.com',
            'name': 'Admin',
            'pwhashed': pbkdf2_sha256.hash('admin'),
            'status': 'active'}
        }

    def getList(self):
        return [{'email': u['email'], 'name': u['name'], 'status': u['status']}
                for u in self.users.values()]

    def add(self, data):
        if data['email'] in self.users:
            raise Exception("User already exists")
        data['pwhashed'] = pbkdf2_sha256.hash(data.pop('password')
                                              .encode('UTF-8'))
        self.users[data['email']] = data
        return data

    def update(self, userid, userData):
        if userid in self.users:
            user = self.users[userid]
            user.update(userData)
            if 'password' in user:
                user['pwhashed'] = pbkdf2_sha256.hash(user.pop('password')
                                                      .encode('UTF-8'))
            return user
        raise Exception('Nonexisting user')

    def auth(self, userid, password):
        user = self.users.get(userid)
        return user and pbkdf2_sha256.verify(password.encode('UTF-8'),
                                             user['pwhashed'])


class Holiday:
    """provides getList, add, update, delete methods"""
    def __init__(self):
        self.holidays = {1: {'date': '2017-12-25', 'name': 'Christmas'}}
        self.lastId = 1

    def getList(self, year):
        retlist = []
        for hid, h in self.holidays.iteritems():
            hyear = re.match('\d+', h['date']).group(0)
            if hyear == year:
                retlist.append(dict(h, id=hid))
        return retlist

    def add(self, data):
        holiday = self.holidays[self.lastId] = data
        self.holidays[self.lastId]['id'] = self.lastId
        self.lastId += 1
        return holiday

    def update(self, hid, data):
        hid = int(hid)
        if hid in self.holidays:
            self.holidays[hid].update(data)
            return self.holidays[hid]
        else:
            raise Exception('holiday not found')

    def delete(self, hid):
        """Returns true if the id was found
        @type hid: int
        @param hid: integer id of the holiday
        """
        return self.holidays.pop(int(hid), False) is not False


class WeeklyReport:
    """provides a list of weekly reports for the user. Weekly report is
    essentially just an overtime status measured in minutes."""

    def __init__(self, dayInstance):
        self.dayInstance = dayInstance
        self.reports = collections.defaultdict(dict)

    def getList(self, userid, start, count=None):
        """returns list segment [start:start+count], sorted by time in a
        descending order."""
        userReport = self.reports[userid]
        keys = sorted(userReport.keys(), reverse=True)
        end = len(keys) if count is None else start+count
        return [userReport[k] for k in keys[start:end]]

    def add(self, userid, isoYear, isoWeek):
        """@note: This is the place to execute the consistency checks to the
        best of the capabilites provided by the storage."""
        week = isoweek.Week(isoYear, isoWeek)
        # compute delta.
        flex, vacation = getDelta(self.dayInstance, userid, week)
        # accumulate with former week, if any.
        userReport = self.reports[userid]
        if len(userReport) > 0:
            lastReport = userReport[sorted(userReport.keys())[-1]]
            prevWeek = week-1
            if not (lastReport['week'] == prevWeek.week and
                    lastReport['year'] == prevWeek.year):
                raise ConsistencyError('locked weeks must be continouos')
            vacation += lastReport['vacation']
            flex += lastReport['flex']
        key = week.isoformat()
        data = {'year': week.year, 'week': week.week,
                'vacation': vacation, 'flex': flex}
        self.reports[userid][key] = data
        return data

    def delete(self, userid, year, week):
        key = isoweek.Week(year, week).isoformat()
        del self.reports[userid][key]
