#! /usr/bin/env python

"""User data interface implemented by by User class."""

import json
import webapp2

import model

class Day(webapp2.RequestHandler):

    def get(self, userid):
        """return statuses for the range apecified by start and end query 
        parameters."""
        start = self.request.get('start')
        end = self.request.get('end')
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'dl': model.day.getList(userid,
                                                                start, end)}))


    def patch(self, userid, day):
        """Sets day properties: 'start', 'end', 'pause', 'type' or comment"""
        dayData = json.loads(self.request.body)
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'d': model.day.update(userid, day,
                                                               dayData)}))


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

class Report(webapp2.RequestHandler):
    """Handles week locking, unlocking, and getting overtime status"""

    def post(self):
        """Locks given week"""
        self.response.status = 400
        yearMonth = json.loads(self.request.body)
        self.response.write(json.dumps({'error': 'Not implemented'}))

    def delete(self, yyyyWw):
        """Unlocks given week"""
        self.response.status = 400
        self.response.write(json.dumps({'error': 'Not implemented'}))

    def get(self, userid):
        """Returns overtime status and last locked week data"""
        self.response.status = 400
        self.response.write(json.dumps({'error': 'Not implemented'}))
