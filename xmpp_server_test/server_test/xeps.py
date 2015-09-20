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

from collections import defaultdict

from django.utils.translation import ugettext as _

xeps = defaultdict(lambda: defaultdict(lambda: None))


def xep0138_notes(value):
    if value['status'] is False:
        return ''

    client = set(value.get('client', []))
    server = set(value.get('server', []))

    if value['status'] == 'partial':
        if client:
            return _('Only supported on client: %s') % ', '.join(sorted(client))
        elif server:
            return _('Only supported on client: %s') % ', '.join(sorted(server))
        else:
            return _('')

    if client or server:  # server supports some methods somewhere
        if client == server:  # same methods client/server
            return _('Methods: %s') % ', '.join(sorted(client))
        else:
            label = '<span class="label label-warning">%s</span> %s' % (
                _('Inconsistent methods:'), _('Warning'))
            client = _('<li>Client: %s</li>') % ', '.join(sorted(client))
            server = _('<li>Server: %s</li>') % ', '.join(sorted(server))
            return '%s<ul>%s%s</ul>' % (label, client, server)

    return ''

xeps['0012']['name'] = 'Last Activity'
xeps['0016']['name'] = 'Privacy Lists'
xeps['0030']['name'] = 'Service Discovery'
xeps['0039']['name'] = 'Statistics Gathering'
xeps['0050']['name'] = 'Ad-Hoc Commands'
xeps['0054']['name'] = 'vcard-temp'
xeps['0060']['name'] = 'Publish-Subscribe'
xeps['0077']['name'] = 'In-Band Registration'
xeps['0078']['name'] = 'Non-SASL Authentication'
xeps['0079']['name'] = 'Advanced Message Processing'
xeps['0092']['name'] = 'Software Version'
xeps['0115']['name'] = 'Entity Capabilities'
xeps['0138']['name'] = 'Stream Compression'
xeps['0138']['notes'] = xep0138_notes
xeps['0160']['name'] = 'Best Practices for Handling Offline Messages'
xeps['0191']['name'] = 'Blocking Command'
xeps['0198']['name'] = 'Stream Management'
xeps['0199']['name'] = 'XMPP Ping'
xeps['0202']['name'] = 'Entity Time'
xeps['0220']['name'] = 'Server Dialback'
xeps['0280']['name'] = 'Message Carbons'
xeps['0288']['name'] = 'Bidirectional Server-to-Server Connections'
xeps['0313']['name'] = 'Message Archive Management'
xeps['0352']['name'] = 'Client State Indication'
