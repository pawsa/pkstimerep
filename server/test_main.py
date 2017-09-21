#! /usr/bin/env python

"""REST API unit tests"""

import json
import unittest
import webapp2

import main
import model

class UserTest(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()

