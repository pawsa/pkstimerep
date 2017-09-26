#! /usr/bin/env python

"""User data interface implemented by by User class."""

import datetime
import isoweek
import json
import webapp2

import model


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class Day(webapp2.RequestHandler):

    def get(self, userid):
        """return statuses for the range apecified by start and end query
        parameters. If both are not present at the same time, last
        present week is used. If there is no data at all, current week
        is returned.
        """
        start = self.request.get('start')
        end = self.request.get('end')
        if (start and end):
            start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            end = datetime.datetime.strptime(end, '%Y-%m-%d').date()
        else:
            reports = model.report.getList(userid, 0, 1)
            if len(reports) > 0:
                nextWeek = isoweek(reports[0].year, reports[0].week+1)
                start = nextWeek.monday()
                end = nextWeek.sunday()
        if not (start and end):
            dt = datetime.date.today()
            start = dt - datetime.timedelta(days=dt.weekday())
            end = start + datetime.timedelta(days=6)
        days = model.day.getList(userid, start, end)
        if not days:  # nothing logged yet. FIXME add an unit test for this
            while start <= end:
                days.append({'date': start, 'arrival': '8:00',
                             'break': 15, 'departure': '16:15',
                             'extra': 0})
                start += datetime.timedelta(days=1)
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'dl': days}, cls=DateEncoder))

    def post(self, userid):
        """Sets day properties: 'start', 'end', 'pause', 'type' or comment"""
        dayData = json.loads(self.request.body)
        date = datetime.datetime.strptime(dayData['date'], '%Y-%m-%d').date()
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'d': model.day.update(userid, date,
                                                              dayData)},
                                       cls=DateEncoder))

    def delete(self, userid, day):
        """Clears any prior data pertinent to the day, if allowed."""
        model.day.delete(userid, day)
        self.response.content_type = 'application/json'
        self.response.response_status = 201


class UserCollection(webapp2.RequestHandler):
    """User creation and listing interface"""

    def get(self):
        users = model.user.getList()
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'users': users}))

    def post(self):
        """Permits creating the actual user.
        FIXME add validation.
        FIXME add admin privileges decorator"""
        self.response.content_type = 'application/json'
        user = json.loads(self.request.body)
        try:
            self.response.write(json.dumps({'u': model.user.add(user)}))
        except Exception as e:
            self.response.status = 400
            self.response.write(json.dumps({'error': e}))


class User(webapp2.RequestHandler):
    """Handles PATCH requests to actual user"""

    def patch(self, userid, mode):
        self.response.content_type = 'application/json'
        if mode == 'meta':
            user = json.loads(self.request.body)
            self.response.write(json.dumps(model.user.update(userid, user)))
        elif mode == 'active':
            user = json.loads(self.request.body)
            self.response.write(json.dumps(model.user.update(userid, user)))
        else:
            self.response.status = 404
            self.response.write(json.dumps({'error': 'Not found'}))

    def post(self):
        """Authenticates the user"""
        credentials = json.loads(self.request.body)
        if model.user.auth(credentials['email'], credentials['password']):
            self.response.status = 200
            self.response.write(json.dumps({'token': 'magictoken'}))
        else:
            self.response.status = 401
            self.response.write(json.dumps({'error': 'Unauthorized'}))

    def get(self, userid):
        pass


class Report(webapp2.RequestHandler):
    """Handles week locking, unlocking, and getting overtime status"""

    def post(self, userid):
        """Locks given week"""
        data = json.loads(self.request.body)
        model.report.add(userid, data)
        self.response.write(json.dumps({'status': 'OK'}))

    def delete(self, yyyyWw):
        """Unlocks given week"""
        self.response.status = 400
        self.response.write(json.dumps({'error': 'Not implemented'}))

    def get(self, userid):
        """Returns overtime status and last locked week data"""
        reports = model.report.getList(userid, 0)
        self.response.write(json.dumps({'report': reports}))
