# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-server-test
# (https://github.com/mathiasertl/django-xmpp-server-test).
#
# django-xmpp-server-test is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# django-xmpp-server-test is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-server-test.  If not, see <http://www.gnu.org/licenses/>.

from celery import shared_task
from celery.utils.log import get_task_logger

from django.conf import settings

from .models import ServerTest
from .utils import test_connection

log = get_task_logger(__name__)


@shared_task
def test_server(test):
    test = ServerTest.objects.select_related('server').get(pk=test)

    data = test.data
    data['connect']['status'] = True
    data['connect']['client'] = []
    data['connect']['server'] = []

    # Test client connectivity
    for record in data['dns']['client_records']:
        connect = {'host': record['host'], 'port': record['port'], 'ips': {}, }
        for ip in record['ips']:
            status = test_connection(ip, record['port'])
            if status is False:
                data['connect']['status'] = False
                test.server.listed = False
            connect['ips'][ip] = status
        data['connect']['client'].append(connect)

    # Test server connectivity
    for record in data['dns']['server_records']:
        connect = {'host': record['host'], 'port': record['port'], 'ips': {}, }
        for ip in record['ips']:
            status = test_connection(ip, record['port'])
            if status is False:
                data['connect']['status'] = False
                test.server.listed = False
            connect['ips'][ip] = status
        data['connect']['server'].append(connect)

    test.data = data
    test.save()

    # If the server is not marked as listed, we consider it broken. Not for DEBUG of course.
    if test.server.listed is False and settings.DEBUG is False:
        # This means that some connection failed.
        test.finished = True
        test.save()
        test.server.save()
        return

    test.finished = True
    test.server.listed = True
    test.server.save()
    test.save()
