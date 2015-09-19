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

from sleekxmpp.basexmpp import BaseXMPP
from sleekxmpp.clientxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError
from sleekxmpp.plugins.base import load_plugin
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream.handler import Callback
from sleekxmpp.xmlstream.matcher import MatchXPath

#from .plugins import amp
#from .plugins import auth
#from .plugins import bind
from .plugins import caps
from .plugins import compression
from .plugins import csi
from .plugins import dialback
from .plugins import register
from .plugins import rosterver
#from .plugins import session
from .plugins import sm

log = logging.getLogger(__name__)

_feature_mappings = {
    '0012': 'jabber:iq:last',
    '0016': 'jabber:iq:privacy',
    '0039': 'http://jabber.org/protocol/stats',
    '0050': 'http://jabber.org/protocol/commands',
    '0054': 'vcard-temp',
    '0060': 'http://jabber.org/protocol/pubsub',
    '0160': 'msgoffline',
    '0191': 'urn:xmpp:blocking',
    '0199': 'urn:xmpp:ping',
    '0202': 'urn:xmpp:time',
    '0280': 'urn:xmpp:carbons:2',
    '0313': 'urn:xmpp:mam:0',
}


class StreamFeatureMixin(object):
    def handle_compression_stream_feature(self, kind):
        if 'compression' in self._stream_feature_stanzas:
            stanza = self._stream_feature_stanzas['compression']
            methods = [n.text for n in stanza.findall('{%s}method' % stanza.namespace)]
            self.test.data['xeps']['0138'][kind] = methods
        else:
            self.test.data['xeps']['0138'][kind] = []


class StreamFeatureClient(ClientXMPP, StreamFeatureMixin):
    def __init__(self, test, *args, **kwargs):
        super(StreamFeatureClient, self).__init__(*args, **kwargs)
        self.use_ipv6 = settings.USE_IP6
        self.auto_reconnect = False
        self.test = test

        # disable the stock rosterver plugina
        registered_features = {f: p  for p, f in self._stream_feature_order}
        for feature in ['rosterver']:
            if feature in registered_features:
                self.unregister_feature(feature, registered_features[feature])

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
        self.add_event_handler("failed_auth", self.failed_auth)
        self._stream_feature_stanzas = {}

    def replace_plugin(self, name, module):
        self.plugin.disable(name)
        load_plugin(name, module)
        self.plugin.enable(name)

    def failed_auth(self, *args, **kwargs):
        self.test.data['authenticated'] = False
        self.test.save()
        self.disconnect();

    def process_stream_features(self):
        # Process basic core features (stanza is present -> server supports it)
        self.test.data['core']['session']['status'] = 'session' in self._stream_feature_stanzas
        self.test.data['core']['bind']['status'] = 'bind' in self._stream_feature_stanzas

        # Process starttls
        if 'starttls' in self._stream_feature_stanzas:
            stanza = self._stream_feature_stanzas['starttls']
            if stanza.find('{%s}required' % stanza.namespace) is None:
                self.test.data['core']['tls']['status'] = 'optional'
            else:
                self.test.data['core']['tls']['status'] = 'required'
        else:
            self.test.data['core']['tls']['status'] = False

        # Process SASL authentication mechanisms
        if 'mechanisms' in self._stream_feature_stanzas:
            self.test.data['core']['sasl']['status'] = True
            stanza = self._stream_feature_stanzas['mechanisms']
            algos = [n.text for n in stanza.findall('{%s}mechanism' % stanza.namespace)]
            self.test.data['core']['sasl']['algorithms'] = algos
        else:
            self.test.data['core']['sasl']['status'] = False

        self.handle_compression_stream_feature('client')

        # process XEPs
        self.test.data['xeps']['0077']['status'] = 'register' in self._stream_feature_stanzas
        self.test.data['xeps']['0078']['status'] = 'auth' in self._stream_feature_stanzas
        self.test.data['xeps']['0079']['status'] = 'amp' in self._stream_feature_stanzas
        self.test.data['xeps']['0115']['status'] = 'c' in self._stream_feature_stanzas
        self.test.data['xeps']['0198']['status'] = 'sm' in self._stream_feature_stanzas
        self.test.data['xeps']['0352']['status'] = 'csi' in self._stream_feature_stanzas

    def test_xep0030(self):  # XEP-0030: Service Discovery
        try:
            info = self['xep_0030'].get_info(jid=self.boundjid.domain, ifrom=self.boundjid.full)
            self.test.data['xeps']['0030']['status'] = True

            features = info.values['disco_info']['features']
            if 'jabber:iq:version' in features:
                features.remove('jabber:iq:version')
                self.test_xep0092()

            # generic XEPs
            for xep, feature in _feature_mappings.items():
                self.test.data['xeps'][xep]['status'] = feature in features
                self.test.save()
                if feature in features:
                    features.remove(feature)

            # remove any additional pubsub namespaces
            features = [f for f in features if not
                        f.startswith('http://jabber.org/protocol/pubsub')]

            if features:
                log.info('Unhandled features: %s', sorted(features))
        except IqError as e:
            if e.condition == 'feature-not-implemented':
                self.test.data['xeps']['0030']['status'] = 'no'
            else:
                log.error('[XEP-0030]: Unhandled condition: %s', e.condition)
                self.test.data['xeps']['0030']['status'] = False
            self.test.data['xeps']['0030']['condition'] = e.condition

    def test_xep0092(self):  # XEP-0092: Software Version
        try:
            version = self['xep_0092'].get_version(self.boundjid.domain, ifrom=self.boundjid.full)
            if version['type'] == 'result':
                self.test.data['xeps']['0092']['status'] = True
                data = version.values['software_version']

                # assemble a string displayed in the notes field
                note = ''
                if 'name' in data:
                    note += data['name']
                if 'version' in data:
                    note += ' %s' % data['version']
                if 'os' in data:
                    note += ' (%s)' % data['os']
                self.test.data['xeps']['0092']['notes'] = note
            else:
                log.error('[XEP-0092]: Received IQ stanza of type "%s".', version['type'])
                self.test.data['xeps']['0092']['status'] = False
        except IqError as e:
            if e.condition == 'feature-not-implemented':
                self.test.data['xeps']['0092']['status'] = 'no'
            else:
                log.error('[XEP-0092]: Unhandled condition: %s', e.condition)
                self.test.data['xeps']['0092']['status'] = False
            self.test.data['xeps']['0092']['condition'] = e.condition
        except Exception as e:
            log.error("[XEP-0092] %s: %s", type(e).__name__, e)
            self.test.data['xeps']['0092']['status'] = False

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
        self.process_stream_features()
        self.test_xep0030()
        self.disconnect()

    def session_start(self, event):
        pass


class StreamFeatureServer(BaseXMPP, StreamFeatureMixin):
    def __init__(self, test, jid, lang='en'):
        super(StreamFeatureServer, self).__init__(jid, default_ns='jabber:server')

        self.test = test
        self.use_ipv6 = settings.USE_IP6
        self.auto_reconnect = False
        self.test = test
        self._stream_feature_stanzas = {}

        # adapted from ClientXMPP
        self.default_port = 5269
        self.default_lang = lang
        self.stream_header = "<stream:stream to='%s' %s %s %s %s>" % (
            self.boundjid.host,
            "xmlns:stream='%s'" % self.stream_ns,
            "xmlns='%s'" % self.default_ns,
            "xml:lang='%s'" % self.default_lang,
            "version='1.0'")
        self.stream_footer = "</stream:stream>"

        self.features = set()
        self._stream_feature_handlers = {}
        self._stream_feature_order = []

        self.dns_service = 'xmpp-server'

        self.register_stanza(StreamFeatures)
        self.register_handler(
                Callback('Stream Features',
                         MatchXPath('{%s}features' % self.stream_ns),
                         self._handle_stream_features))

        self.register_plugin('feature_starttls')
        self.register_plugin('feature_dialback', module=dialback)
        self.register_plugin('feature_sm', module=sm)

        self.add_event_handler('stream_negotiated', self._stream_negotiated)

    def connect(self, address=tuple(), reattempt=True,
                use_tls=True, use_ssl=False):
        """Adapted from ClientXMPP.

        When no address is given, a SRV lookup for the server will
        be attempted. If that fails, the server user in the JID
        will be used.

        :param address: A tuple containing the server's host and port.
        :param reattempt: If ``True``, repeat attempting to connect if an
                         error occurs. Defaults to ``True``.
        :param use_tls: Indicates if TLS should be used for the
                        connection. Defaults to ``True``.
        :param use_ssl: Indicates if the older SSL connection method
                        should be used. Defaults to ``False``.
        """
        self.session_started_event.clear()

        # If an address was provided, disable using DNS SRV lookup;
        # otherwise, use the domain from the client JID with the standard
        # XMPP client port and allow SRV lookup.
        if address:
            self.dns_service = None
        else:
            address = (self.boundjid.host, 5269)
            self.dns_service = 'xmpp-server'

        return super(StreamFeatureServer, self).connect(address[0], address[1], use_tls=use_tls,
                                                        use_ssl=use_ssl, reattempt=reattempt)

    def _handle_stream_features(self, features):
        if 'starttls' in features['features']:  # Reset stream features after starttls
            self._stream_feature_stanzas = {
                'starttls': features['starttls'],
            }
        else:  # New stream features encountered
            self._stream_feature_stanzas.update(features.get_features())

        found_tags = set([re.match('{.*}(.*)', n.tag).groups(1)[0]
                         for n in features.xml.getchildren()])
        unhandled = found_tags - set(features.get_features().keys())
        if unhandled:
            log.error("Unhandled stream features: %s", sorted(unhandled))
        return ClientXMPP._handle_stream_features(self, features)

    def process_stream_features(self):
        # Process starttls
        if 'starttls' in self._stream_feature_stanzas:
            stanza = self._stream_feature_stanzas['starttls']
            if stanza.find('{%s}required' % stanza.namespace) is None:
                self.test.data['core']['tls']['server'] = 'optional'
            else:
                self.test.data['core']['tls']['server'] = 'required'
        else:
            self.test.data['core']['tls']['status'] = False

        self.handle_compression_stream_feature('server')

        self.test.data['xeps']['0220']['status'] = 'dialback' in self._stream_feature_stanzas
        self.test.data['xeps']['0288']['status'] = 'bidi' in self._stream_feature_stanzas

    def _stream_negotiated(self, *args, **kwargs):
        self.process_stream_features()
        self.disconnect()

    register_feature = ClientXMPP.register_feature
