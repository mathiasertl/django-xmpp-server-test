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

import logging
import socket

log = logging.getLogger(__name__)


def test_connection(host, port):
    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        if af == socket.AF_INET:
            log.info('Test %s:%s', sa[0], sa[1])
        else:
            log.info('Test [%s]:%s', sa[0], sa[1])

        try:
            s = socket.socket(af, socktype, proto)
        except socket.error:
            return False
        try:
            s.connect(sa)
        except socket.error:
            s.close()
            return False
        s.close()

    return True
