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
import re

from django.conf import settings

from sleekxmpp.clientxmpp import ClientXMPP
from sleekxmpp.plugins.base import load_plugin

#from .plugins import amp
#from .plugins import auth
#from .plugins import bind
from .plugins import caps
from .plugins import compression
from .plugins import csi
#from .plugins import dialback
from .plugins import register
from .plugins import rosterver
#from .plugins import session
from .plugins import sm

log = logging.getLogger(__name__)


class StreamFeatureClient(ClientXMPP):
    def __init__(self, test, *args, **kwargs):
        self.servertest = test
        super(StreamFeatureClient, self).__init__(*args, **kwargs)
        self.use_ipv6 = settings.USE_IP6
        self.auto_reconnect = False

        # disable the stock rosterver plugina
        self.unregister_feature('rosterver', 9000)
#        self.unregister_feature('bind', 10000)
#        self.unregister_feature('session', 10001)
        self.replace_plugin('feature_rosterver', rosterver)
#        self.replace_plugin('feature_bind', bind)
#        self.replace_plugin('feature_session', session)

        # register additional known plugins
        self.register_plugin('feature_caps', module=caps)
        self.register_plugin('feature_compression', module=compression)
        self.register_plugin('feature_register', module=register)
        self.register_plugin('feature_sm', module=sm)
        self.register_plugin('feature_csi', module=csi)

        # register various xep plugins
        self.register_plugin('xep_0030')  # service discovery
        self.register_plugin('xep_0092')  # software version

        self.add_event_handler('stream_negotiated', self._stream_negotiated)
        self.add_event_handler("session_start", self.session_start)
        self._stream_feature_stanzas = {}

    def replace_plugin(self, name, module):
        self.plugin.disable(name)
        load_plugin(name, module)
        self.plugin.enable(name)

    def process_stream_features(self):
        self.servertest.data['xeps']['0077']['status'] = 'register' in self._stream_feature_stanzas
        self.servertest.data['xeps']['0078']['status'] = 'auth' in self._stream_feature_stanzas
        self.servertest.data['xeps']['0079']['status'] = 'amp' in self._stream_feature_stanzas
        self.servertest.data['xeps']['0138']['status'] = 'compress' in self._stream_feature_stanzas
        self.servertest.data['xeps']['0198']['status'] = 'sm' in self._stream_feature_stanzas

    def test_xep0092(self):
        log.info('### Trying to get software version...')
        try:
            version = self['xep_0092'].get_version(self.boundjid.domain, ifrom=self.boundjid.full)
            if version['type'] == 'result':
                self.servertest.data['xeps']['0092']['status'] = False
            else:
                self.servertest.data['xeps']['0092']['status'] = False
        except:
            self.servertest.data['xeps']['0092']['status'] = False

    def _handle_stream_features(self, features):
        """Collect incoming stream features.

        This method is invoked multiple times if (e.g. after starttls) the stream is renegotiated.
        """
        if 'starttls' in features['features']:  # Reset stream features after starttls
            self._stream_feature_stanzas = {
                'starttls': features['starttls'],
            }
        else:  # New stream features encountered
            self._stream_feature_stanzas.update(features.get_features())

        # compute list of unhandled stream features
        found_tags = set([re.match('{.*}(.*)', n.tag).groups(1)[0]
                         for n in features.xml.getchildren()])
        unhandled = found_tags - set(features.get_features().keys())
        if unhandled:
            log.error("Unhandled stream features: %s", sorted(unhandled))

        return super(StreamFeatureClient, self)._handle_stream_features(features)

    def _stream_negotiated(self, *args, **kwargs):
        log.info('### Stream negotiated.')
        self.process_stream_features()
        self.test_xep0092()
        #self.disconnect()

    def session_start(self, event):
        pass
