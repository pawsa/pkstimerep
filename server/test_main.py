#! /usr/bin/env python

"""REST API unit tests"""

import json
import unittest
import webapp2

import main
import model

HEADERS = [('content-type', 'application/json')]


class DayTest(unittest.TestCase):
    """Day operations; listing, adding and editing"""

    def setUp(self):
        model.setDevModel()
        try:
            model.user.add({'email': 'a', 'password': 'b'})
        except Exception as e:
            print "SEtup warn", e

    def test_get_patch(self):
        request = webapp2.Request.blank('/user/a/day')
        response = request.get_response(main.app)
        self.assertEqual(response.status_int, 200)
        days = json.loads(response.body)
        self.assertIn('dl', days)
        # test updating current week

        # test that updating former week fails

        # test that updating future week fails


class UserTest(unittest.TestCase):
    """User operations: listing and adding"""

    def setUp(self):
        model.setDevModel()

    def test_get_list(self):
        request = webapp2.Request.blank('/user')
        response = request.get_response(main.app)

        self.assertEqual(response.status_int, 200)
        users = json.loads(response.body)
        self.assertIn('users', users)

    def test_add_auth(self):

        request = webapp2.Request.blank('/user',
                                        headers=HEADERS)
        request.method = 'POST'
        request.body = json.dumps({'email': 'a', 'name': 'N',
                                   'status': 'active',
                                   'password': 'x'})
        response = request.get_response(main.app)

        self.assertEqual(response.status_int, 200)
        user = json.loads(response.body)
        self.assertIn('u', user)
        self.assertIn('email', user['u'])

        # Successful auth
        request = webapp2.Request.blank('/user/auth', headers=HEADERS)
        request.method = 'POST'
        request.body = json.dumps({'email': 'a', 'password': 'x'})
        response = request.get_response(main.app)

        self.assertEqual(response.status_int, 200)

        # failed auth
        request = webapp2.Request.blank('/user/auth', headers=HEADERS)
        request.method = 'POST'
        request.body = json.dumps({'email': 'a', 'password': 'b'})
        response = request.get_response(main.app)

        self.assertEqual(response.status_int, 401)


class HolidayTest(unittest.TestCase):
    """Holiday operations: listing, adding, updating, deleting."""

    def setUp(self):
        model.setDevModel()

    def test_get_list(self):
        request = webapp2.Request.blank('/holiday')
        response = request.get_response(main.app)

        self.assertEqual(response.status_int, 200)
        holidays = json.loads(response.body)
        self.assertIn('rdl', holidays)
        self.assertEqual(holidays['rdl'], [])

    def test_get_list_filtered(self):
        request = webapp2.Request.blank('/holiday?year=2017')
        response = request.get_response(main.app)

        self.assertEqual(response.status_int, 200)
        holidays = json.loads(response.body)
        self.assertIn('rdl', holidays)
        self.assertTrue(isinstance(holidays['rdl'], list))
        self.assertEqual(len(holidays['rdl']), 1)

    def test_post_delete(self):
        request = webapp2.Request.blank('/holiday', headers=HEADERS)
        request.method = 'POST'
        request.body = json.dumps({'date': '2017-01-01', 'name': 'New Year'})
        response = request.get_response(main.app)
        self.assertEqual(response.status_int, 200)
        newYear = json.loads(response.body)
        request = webapp2.Request.blank('/holiday/' + str(newYear['rd']['id']),
                                        headers=HEADERS)
        request.method = 'DELETE'
        response = request.get_response(main.app)
        self.assertEqual(response.status_int, 204)
        response = request.get_response(main.app)
        self.assertEqual(response.status_int, 404)

    def test_patch_err(self):
        request = webapp2.Request.blank('/holiday',
                                        headers=HEADERS)
        request.method = 'PATCH'
        request.body = json.dumps({'date': '2', 'name': 'b'})
        response = request.get_response(main.app)

        self.assertEqual(response.status_int, 405)

    def test_patch_ok(self):
        request = webapp2.Request.blank('/holiday/1',
                                        headers=HEADERS)
        request.method = 'PATCH'
        request.body = json.dumps({'date': '2-1', 'name': 'b'})
        response = request.get_response(main.app)

        # verify modification
        self.assertEqual(response.status_int, 200)

        request = webapp2.Request.blank('/holiday?year=2')
        response = request.get_response(main.app)

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
        request = webapp2.Request.blank('/user/1/report')
        response = request.get_response(main.app)

        self.assertEqual(response.status_int, 200)
        report1 = json.loads(response.body)
        # try adding
        request = webapp2.Request.blank('/user/1/report', headers=HEADERS)
        request.method = 'POST'
        request.body = json.dumps({'year': 2017, 'week': 2, 'overtime': 2})
        response = request.get_response(main.app)
        self.assertEqual(response.status_int, 200)

        # add second time, too
        request.body = json.dumps({'year': 2017, 'week': 3, 'overtime': 3})
        response = request.get_response(main.app)

        # test listing
        request = webapp2.Request.blank('/user/1/report')
        response = request.get_response(main.app)

        self.assertEqual(response.status_int, 200)
        report2 = json.loads(response.body)

        self.assertEqual(len(report1['report'])+2, len(report2['report']))


if __name__ == '__main__':
    unittest.main()
