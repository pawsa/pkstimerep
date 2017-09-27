#! /usr/bin/env python

"""REST API unit tests"""

import json
import unittest
import webapp2

import main
import model

HEADERS = [('content-type', 'application/json')]


def r_delete(path):
    request = webapp2.Request.blank(path, headers=HEADERS)
    request.method = 'DELETE'
    return request.get_response(main.app)


def r_get(path):
    return webapp2.Request.blank(path).get_response(main.app)


def r_patch(path, data):
    request = webapp2.Request.blank(path, headers=HEADERS)
    request.method = 'PATCH'
    request.body = json.dumps(data)
    return request.get_response(main.app)


def r_post(path, data):
    request = webapp2.Request.blank(path, headers=HEADERS)
    request.method = 'POST'
    request.body = json.dumps(data)
    return request.get_response(main.app)


class DayTest(unittest.TestCase):
    """Day operations; listing, adding and editing"""

    def setUp(self):
        model.setDevModel()
        try:
            model.user.add({'email': 'a', 'password': 'b'})
        except Exception as e:
            print "SEtup warn", e

    def test_get_patch(self):
        """Verify that data can be set and read back"""
        response = r_get('/user/a/day')
        self.assertEqual(response.status_int, 200)
        days = json.loads(response.body)
        self.assertIn('dl', days)
        monday = days['dl'][0]
        monday['break'] = 15
        # test updating current week
        respose = r_post('/user/a/day', monday)
        self.assertEqual(response.status_int, 200)

        # check that the data is there
        response = r_get('/user/a/day?start={}&end={}'
                         .format(days['dl'][0]['date'],
                                 days['dl'][-1]['date']))
        self.assertEqual(response.status_int, 200)
        days = json.loads(response.body)
        self.assertEqual(days['dl'][0]['break'], 15)

        # FIXME: test that updating former week fails
        response = r_get('/user/a/day')
        self.assertEqual(response.status_int, 200)

        # FIXME: test that updating future week fails

    def test_delete_get_range(self):
        """Tests default data, and modified data ranges"""
        response = r_get('/user/a/day')
        self.assertEqual(response.status_int, 200)
        days = json.loads(response.body)
        self.assertIn('dl', days)
        for day in days['dl']:
            response = r_delete('user/a/day/'+day['date'])
            self.assertIn(response.status_int, (200, 404))
        # check that something is read back
        response = r_get('/user/a/day')
        self.assertEqual(response.status_int, 200)
        # check modification
        monday = days['dl'][0]
        monday['break'] = 15
        # test updating current week
        respose = r_post('/user/a/day', monday)
        self.assertEqual(response.status_int, 200)
        # check that you still read the entire week.
        response3 = r_get('/user/a/day')
        self.assertEqual(response3.status_int, 200)
        days3 = json.loads(response3.body)
        self.assertEqual(len(days['dl']), len(days3['dl']))


class UserTest(unittest.TestCase):
    """User operations: listing and adding"""

    def setUp(self):
        model.setDevModel()

    def test_get_list(self):
        response = r_get('/user')

        self.assertEqual(response.status_int, 200)
        users = json.loads(response.body)
        self.assertIn('users', users)

    def test_add_auth(self):
        response = r_post('/user',
                          {'email': 'a', 'name': 'N', 'status': 'active',
                           'password': 'x'})
        self.assertEqual(response.status_int, 200)
        user = json.loads(response.body)
        self.assertIn('u', user)
        self.assertIn('email', user['u'])

        # Successful auth
        response = r_post('/user/auth', {'email': 'a', 'password': 'x'})
        self.assertEqual(response.status_int, 200)

        # failed auth
        response = r_post('/user/auth', {'email': 'a', 'password': 'b'})
        self.assertEqual(response.status_int, 401)


class HolidayTest(unittest.TestCase):
    """Holiday operations: listing, adding, updating, deleting."""

    def setUp(self):
        model.setDevModel()

    def test_get_list(self):
        response = r_get('/holiday')

        self.assertEqual(response.status_int, 200)
        holidays = json.loads(response.body)
        self.assertIn('rdl', holidays)
        self.assertEqual(holidays['rdl'], [])

    def test_get_list_filtered(self):
        response = r_get('/holiday?year=2017')

        self.assertEqual(response.status_int, 200)
        holidays = json.loads(response.body)
        self.assertIn('rdl', holidays)
        self.assertTrue(isinstance(holidays['rdl'], list))
        self.assertEqual(len(holidays['rdl']), 1)

    def test_post_delete(self):
        response = r_post('/holiday',
                          {'date': '2017-01-01', 'name': 'New Year'})
        self.assertEqual(response.status_int, 200)
        newYear = json.loads(response.body)
        response = r_delete('/holiday/' + str(newYear['rd']['id']))
        self.assertEqual(response.status_int, 204)
        response = r_delete('/holiday/' + str(newYear['rd']['id']))
        self.assertEqual(response.status_int, 404)

    def test_patch_err(self):
        response = r_patch('/holiday', {'date': '2', 'name': 'b'})
        self.assertEqual(response.status_int, 405)

    def test_patch_ok(self):
        response = r_patch('/holiday/1', {'date': '2-1', 'name': 'b'})

        # verify modification
        self.assertEqual(response.status_int, 200)

        response = r_get('/holiday?year=2')
        self.assertEqual(response.status_int, 200)
        holidays = json.loads(response.body)
        self.assertIn('rdl', holidays)
        self.assertTrue(isinstance(holidays['rdl'], list))
        self.assertEqual(len(holidays['rdl']), 1)
        self.assertEqual(holidays['rdl'][0]['date'], '2-1')

    def test_delete(self):
        pass


class ReportTest(unittest.TestCase):

    def test_list_add(self):
        response = r_get('/user/1/report')
        self.assertEqual(response.status_int, 200)
        report1 = json.loads(response.body)

        # try adding
        response = r_post('/user/1/report', {'year': 2017, 'week': 2,
                                             'overtime': 2})
        self.assertEqual(response.status_int, 200)

        # add second time, too
        response = r_post('/user/1/report',
                          {'year': 2017, 'week': 3, 'overtime': 3})
        self.assertEqual(response.status_int, 200)

        # test listing
        response = r_get('/user/1/report')
        self.assertEqual(response.status_int, 200)
        report2 = json.loads(response.body)
        self.assertEqual(len(report1['report'])+2, len(report2['report']))


if __name__ == '__main__':
    unittest.main()
