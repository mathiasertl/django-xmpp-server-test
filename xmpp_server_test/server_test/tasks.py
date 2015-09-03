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

from .models import ServerTest
from .utils import test_connection

log = get_task_logger(__name__)


@shared_task
def test_server(test):
    test = ServerTest.objects.select_related('server').get(pk=test)
    data = test.data

    # Test client connectivity
    for record in data['dns']['client_records']:
        for ip in record['ips']:
            record['ips'][ip] = test_connection(ip, record['port'])

    # Test server connectivity
    for record in data['dns']['server_records']:
        for ip in record['ips']:
            record['ips'][ip] = test_connection(ip, record['port'])

    test.data = data
    test.finished = True
    test.server.listed = True
    test.server.save()
    test.save()
