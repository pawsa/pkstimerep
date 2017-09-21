#! /usr/bin/env python

"""Provides User and Holiday classes with the required methods."""

import collections
import re

class Day:
    """provides getList, add, update methods"""
    def __init__(self):
        self.days = collections.defaultdict(list)
        
    def getList(self, userid, start, end):
        return [d for d in self.days[userid] if start <= d['date'] <= end]

    def update(self, userid, day, dayData):
        userDays = self.days[userid].get(userid, [])
        for d in userDays:
            if d['date'] == day:
                d.update(dayData)
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
        self.users = dict()
        self.lastId = 100000
        
    def getList(self):
        return self.users.values()

    def add(self, data):
        user = self.users[self.lastId] = data
        user['id'] = self.lastId
        self.lastId += 1
        return user

    def update(self, userid, userData):
        if userid in self.users:
            self.users[userid].update(userData)
            return self.users[userid]
        raise Exception('Nonexisting user')


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
        return self.holidays.pop(int(hid), False) != False

