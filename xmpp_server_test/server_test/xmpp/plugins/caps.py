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

from sleekxmpp.plugins import BasePlugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream import ElementBase


class CapsStanza(ElementBase):
    name = 'c'
    namespace = 'http://jabber.org/protocol/caps'
    interfaces = set()
    plugin_attrib = name


class feature_caps(BasePlugin):
    """Plugin for Entity Capabilities (XEP-0115).

    .. seealso:: http://xmpp.org/extensions/xep-0115.html
    """

    def plugin_init(self):
        self.description = 'XEP-0115: Entity Capabilities'
        self.xmpp.register_feature(
            'c',
            self._handle_caps,
            restart=False,
            order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, CapsStanza)

    def _handle_caps(self, features):
        pass
