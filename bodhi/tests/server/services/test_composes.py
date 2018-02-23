# -*- coding: utf-8 -*-
# Copyright 2017-2018 Red Hat, Inc.
#
# This file is part of Bodhi.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""This module contains tests for bodhi.server.services.composes."""

from pyramid import testing
from pyramid import security

from bodhi.server import models
from bodhi.server.services import composes
from bodhi.tests.server import base


class TestCompose__init__(base.BaseTestCase):
    """This class contains tests for the Compose.__init__() method."""
    def test___init__(self):
        """Assert the request is stored properly."""
        request = testing.DummyRequest()

        composes_resource = composes.Composes(request)

        self.assertIs(composes_resource.request, request)


class TestCompose__acl__(base.BaseTestCase):
    """This class contains tests for the Compose.__acl__() method."""
    def test___acl__(self):
        """Assert the permissions are correct."""
        request = testing.DummyRequest()
        composes_resource = composes.Composes(request)

        acls = composes_resource.__acl__()

        self.assertEqual(acls, [(security.Allow, security.Everyone, 'view_composes')])


class TestComposeCollectionGet(base.BaseTestCase):
    """This class contains tests for the Compose.collection_get() method."""
    def test_no_composes(self):
        """Assert correct behavior when there are no composes."""
        response = self.app.get('/composes/', status=200, headers={'Accept': 'text/html'})

        # The Composes header should still appear in the page
        self.assertTrue('<h1>Composes</h1>' in response)

    def test_with_compose(self):
        """Assert correct behavior when there is a compose."""
        update = models.Update.query.first()
        compose = models.Compose(release=update.release, request=update.request)
        self.db.add(compose)
        self.db.flush()

        response = self.app.get('/composes/', status=200, headers={'Accept': 'text/html'})

        # The Composes header should still appear in the page
        self.assertTrue('<h1>Composes</h1>' in response)
        self.assertTrue(
            '/composes/{}/{}'.format(compose.release.name, compose.request.value) in response)
        self.assertTrue(compose.state.description in response)


class TestComposeGet(base.BaseTestCase):
    """This class contains tests for the Compose.get() method."""
    def test_404_compose(self):
        """Assert a 404 error code when there isn't a Compose matching the URL."""
        release = models.Release.query.first()

        self.app.get('/composes/{}/testing'.format(release.name), status=404,
                     headers={'Accept': 'text/html'})

    def test_404_release(self):
        """Assert a 404 error code when the release component of the URL does not exist."""
        self.app.get('/composes/dne/testing', status=404, headers={'Accept': 'text/html'})

    def test_404_request(self):
        """Assert a 404 error code when the request component of the URL does not exist."""
        release = models.Release.query.first()

        self.app.get('/composes/{}/hahahwhatisthis'.format(release.name), status=404,
                     headers={'Accept': 'text/html'})

    def test_with_compose(self):
        """Assert correct behavior when there is a compose."""
        update = models.Update.query.first()
        update.locked = True
        compose = models.Compose(release=update.release, request=update.request)
        self.db.add(compose)
        self.db.flush()

        response = self.app.get(
            '/composes/{}/{}'.format(compose.release.name, compose.request.value),
            status=200, headers={'Accept': 'text/html'})

        self.assertTrue(compose.state.description in response)
        self.assertTrue('{} {}'.format(compose.release.name, compose.request.value) in response)
        self.assertTrue(update.beautify_title(amp=True, nvr=True) in response)
