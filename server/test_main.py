#! /usr/bin/env python

"""REST API unit tests"""

import json
import unittest
import webapp2

import main
import model

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

    def test_add(self):

        request = webapp2.Request.blank('/user',
                                        headers=[('content-type',
                                                  'application/json')])
        request.method = 'POST'
        request.body = json.dumps({'login': 'a', 'name': 'N', 'rights': 'a'})
        response = request.get_response(main.app)
        
        self.assertEqual(response.status_int, 200)
        user = json.loads(response.body)
        self.assertIn('u', user)
        self.assertIn('login', user['u'])


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
        request = webapp2.Request.blank('/holiday',
                                        headers=[('content-type',
                                                  'application/json')] )
        request.method = 'POST'
        request.body = json.dumps({'date': '2017-01-01', 'name': 'New Year'})
        response = request.get_response(main.app)
        self.assertEqual(response.status_int, 200)
        newYear = json.loads(response.body)
        request = webapp2.Request.blank('/holiday/'+ str(newYear['rd']['id']),
                                        headers=[('content-type',
                                                  'application/json')] )
        request.method = 'DELETE'
        response = request.get_response(main.app)
        self.assertEqual(response.status_int, 204)
        response = request.get_response(main.app)
        self.assertEqual(response.status_int, 404)

    def test_patch_err(self):
        request = webapp2.Request.blank('/holiday',
                                        headers=[('content-type',
                                                  'application/json')] )
        request.method = 'PATCH'
        request.body = json.dumps({'date': '2', 'name': 'b'})
        response = request.get_response(main.app)

        self.assertEqual(response.status_int, 405)

    def test_patch_ok(self):
        request = webapp2.Request.blank('/holiday/1',
                                        headers=[('content-type',
                                                  'application/json')] )
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


if __name__ == '__main__':
    unittest.main()

