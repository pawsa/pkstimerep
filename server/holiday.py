#! /usr/bin/env python

"""Manages holiday/red day defaults"""

import json
import webapp2

import model

class Calendar(webapp2.RequestHandler):

    def post(self):
        """Adds given holiday. FIXME add validation"""
        holiday = json.loads(self.request.body)
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'rd': model.holiday.add(holiday)}))

    def get(self):
        """"returns a list of holidays for given year"""
        year = self.request.get('year')
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'rdl': model.holiday.getList(year)}))

    def patch(self, holidayid):
        """change the name or data for given holiday"""
        holiday = json.loads(self.request.body)
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'rd': model.holiday.update(holidayid,
                                                                     holiday)}))

    def delete(self, holidayid):
        """Delete given holiday"""
        self.response.content_type = 'application/json'
        self.response.write(json.dumps(model.holiday.delete(holidayid)))
