#! /usr/bin/env python

"""Main PKS timesheet handler.  It simply registers the handlers. It
provides also a development interface with a test backend."""

import sys
import webapp2

import holiday
import user

#
# support PATCH methods, as long as
# https://code.google.com/archive/p/webapp-improved/issues/69 is not merged
# to mainline.
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/user', user.UserCollection),
    ('/user/auth', user.User),
    ('/user/([^/]+)/(meta|active)?$', user.User),
    ('/user/([^/]+)/report', user.Report),
    ('/user/([^/]+)/report/(.+)', user.Report),
    ('/user/([^/]+)/day', user.Day),
    ('/holiday$', holiday.CalendarList),
    ('/holiday/([^/]+)', holiday.CalendarDay),
], debug=True)


def devserver(storageModel):
    """Starts a development server with a development, sqllite based
    model.  Otherwise, gcloud compatible storage will be used."""
    from paste import httpserver
    from paste.urlparser import StaticURLParser
    from paste.cascade import Cascade
    import model
    model.setModel(storageModel)
    static_server = StaticURLParser('client')
    testapp = Cascade([static_server, app])
    httpserver.serve(testapp, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    devserver(sys.argv[1] if len(sys.argv) > 1 else 'mem')
