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


class ClientStateIndicationStanza(ElementBase):
    name = 'csi'
    namespace = 'urn:xmpp:csi:0'
    interfaces = set()
    plugin_attrib = 'csi'


class feature_csi(BasePlugin):
    """Plugin for XEP-0352: Client State Indication

    .. seealso:: https://xmpp.org/extensions/xep-0352.html
    """

    def plugin_init(self):
        self.description = 'XEP-0352: Client State Indication'
        self.xmpp.register_feature(
            'csi',
            self._handle_csi,
            restart=False,
            order=self.config.get('order', 0))

        register_stanza_plugin(StreamFeatures, ClientStateIndicationStanza)

    def _handle_csi(self, features):
        pass
