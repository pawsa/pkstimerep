#! /usr/bin/env python

"""Manages holiday/red day defaults"""

import json
import webapp2

import model

class CalendarList(webapp2.RequestHandler):

    def get(self):
        """"returns a list of holidays for given year"""
        year = self.request.get('year')
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'rdl': model.holiday.getList(year)}))

    def post(self):
        """Adds given holiday. FIXME add validation"""
        holiday = json.loads(self.request.body)
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'rd': model.holiday.add(holiday)}))


class CalendarDay(webapp2.RequestHandler):

    def patch(self, holidayid):
        """change the name or data for given holiday"""
        holiday = json.loads(self.request.body)
        self.response.content_type = 'application/json'
        try:
            self.response.write(json.dumps({'rd': model.holiday.update(holidayid,
                                                                       holiday)}))
        except Exception as e:
            self.response.status_int = 404

    def delete(self, holidayid):
        """Delete given holiday"""
        self.response.content_type = 'application/json'
        if model.holiday.delete(holidayid):
            self.response.status_int = 204
        else:
            self.response.status_int = 404
            self.response.write(json.dumps({'error': 'not found'}))
