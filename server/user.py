#! /usr/bin/env python

"""User data interface implemented by by User class."""

import cerberus
import datetime
import isoweek
import json
import re
import webapp2

import model


def jsonabort(code, jsonDict):
    """Aborts processing, returning given data
    @param code: HTTP status code to be returned.
    @param jsonDict: dict to be returned as JSON
    """
    body = {'code': code, 'detail': jsonDict}
    webapp2.abort(code, headers=[('content-type', 'application/json')],
                  body=json.dumps(body))


def str2date(value):
    if isinstance(value, (str, unicode)):
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()
    else:
        return value


class TimeValidator(cerberus.Validator):
    """Validator with additional 'time' field type"""
    def _validate_type_time(self, value):
        if re.match('\d\d?:\d\d?', value):
            return True


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

"""Working day index numbers [0, 5)"""

WORKDAYS = range(0, 5)


class Day(webapp2.RequestHandler):

    def get(self, userid):
        """return statuses for the range apecified by start and end query
        parameters. If both are not present at the same time, last
        present week is used. If there is no data at all, current week
        is returned.
        """
        start = self.request.get('start')
        end = self.request.get('end')
        flex = None
        if (start and end):
            start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            end = datetime.datetime.strptime(end, '%Y-%m-%d').date()
        else:
            reports = model.report.getList(userid, 0, 1)
            if len(reports) > 0:
                flex = reports[0]['flex']
                nextWeek = isoweek.Week(reports[0]['year'],
                                        reports[0]['week'])+1
                start = nextWeek.monday()
                end = nextWeek.sunday()
        if not (start and end):
            dt = datetime.date.today()
            start = dt - datetime.timedelta(days=dt.weekday())
            end = start + datetime.timedelta(days=6)
        days = model.day.getList(userid, start, end)
        # create frontend-friendly array
        retlist = []
        while start <= end:
            if len(days) and days[0]['date'] < start:
                days.pop(0)
                next
            if len(days) and days[0]['date'] == start:
                retlist.append(days.pop(0))
            else:
                # Append default values
                if start.weekday() in WORKDAYS:
                    retlist.append({'date': start, 'arrival': '8:00',
                                    'break': 15, 'departure': '16:15',
                                    'extra': 0, 'type': 'work'})
                else:
                    retlist.append({'date': start, 'arrival': '',
                                    'break': None, 'departure': '',
                                    'extra': None, 'type': 'off'})

            start += datetime.timedelta(days=1)
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'dl': retlist, 'flex': flex},
                                       cls=DateEncoder))

    def post(self, userid):
        """Sets day properties: 'arrival', 'departure', 'break', 'type' or
        comment."""
        DAY_SCHEMA = {
            'date': {'type': 'date', 'required': True, 'coerce': str2date},
            'arrival': {'type': 'time', 'required': True},
            'break': {'type': 'integer'},
            'departure': {'type': 'time', 'required': True},
            'extra': {'type': 'integer'},
            'type': {'type': 'string', 'required': True,
                     'allowed': ['work', 'flex', 'sick', 'vacation', 'off']}
        }
        validator = TimeValidator(DAY_SCHEMA)
        dayData = validator.validated(json.loads(self.request.body))
        if dayData is None:
            jsonabort(400, validator.errors)
        self.response.content_type = 'application/json'
        self.response.write(json.dumps({'d': model.day.update(userid,
                                                              dayData['date'],
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
        @note never pass clear text password beyond this point.
        FIXME add validation.
        FIXME add admin privileges decorator"""
        self.response.content_type = 'application/json'
        USER_SCHEMA = {'email': {'type': 'string', 'required': True,
                                 'empty': False},
                       'name': {'type': 'string', 'required': True},
                       'password': {'type': 'string', 'required': True,
                                    'empty': False},
                       'status': {'type': 'string', 'allowed': ['active']}}
        validator = cerberus.Validator(USER_SCHEMA)
        user = validator.validated(json.loads(self.request.body))
        if user is None:
            jsonabort(400, validator.errors)
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
        """Authenticates the user. Note: the plain-text password must NEVER leave this
        interface.
        """
        AUTH_SCHEMA = {'email': {'type': 'string', 'required': True,
                                 'empty': False},
                       'password': {'type': 'string', 'required': True,
                                    'empty': False}}
        validator = cerberus.Validator(AUTH_SCHEMA)
        credentials = validator.validated(json.loads(self.request.body))
        if credentials is None:
            jsonabort(400, validator.errors)
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
        """Locks given week. It is the backend that is responsible for
        calculating the flex status etc."""
        REPORT_SCHEMA = {
            'start': {'type': 'date', 'required': True, 'coerce': str2date},
            'end': {'type': 'date', 'required': True, 'coerce': str2date},
        }
        validator = TimeValidator(REPORT_SCHEMA)
        daysToLock = validator.validated(json.loads(self.request.body))
        if daysToLock is None:
            jsonabort(400, validator.errors)
        # basic consistency
        isostart = daysToLock['start'].isocalendar()
        isoend = daysToLock['end'].isocalendar()
        if not (isostart[0] == isoend[0] and isostart[1] == isoend[1] and
                isostart[2] == 1 and isoend[2] == 7):
            jsonabort(400, 'Range must cover exactly a Mon-Sun week')
        # all good, modify the db.
        model.report.add(userid, isostart[0], isostart[1])
        self.response.write(json.dumps({'status': 'OK'}))

    def delete(self, yyyyWw):
        """Unlocks given week"""
        self.response.status = 400
        self.response.write(json.dumps({'error': 'Not implemented'}))

    def get(self, userid):
        """Returns overtime status and last locked week data"""
        reports = model.report.getList(userid, 0)
        self.response.write(json.dumps({'report': reports}))

    def handle_exception(self, exception, debug):
        # Set a custom message.

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, model.ConsistencyError):
            self.response.set_status(400)
            self.response.write(
                'Consistency error: {}'.format(exception.message))
        else:
            super(Report, self).handle_exception(exception, debug)
