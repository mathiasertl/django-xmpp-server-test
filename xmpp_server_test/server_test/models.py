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

from dns import resolver

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from jsonfield import JSONField


class Server(models.Model):
    domain = models.CharField(max_length=255)
    listed = models.BooleanField(default=False)

    @property
    def latest_test(self):
        try:
            return self.tests.filter(finished=True).latest(field_name='created')
        except ServerTest.DoesNotExist:
            try:
                return self.tests.all().latest(field_name='created')
            except ServerTest.DoesNotExist:
                pass

    def get_absolute_url(self):
        return reverse('server-test:server', kwargs={'domain': self.domain, })

    def test(self):
        # TODO: check for a very recent test
        t = self.tests.create()
        t.start_test()
        t.save()
        return t

    def __str__(self):
        return self.domain


class ServerTest(models.Model):
    server = models.ForeignKey(Server, related_name='tests')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    finished = models.BooleanField(default=False)
    data = JSONField(default={}, blank=True)

    def get_absolute_url(self):
        return reverse('server-test:servertest', kwargs={'domain': self.server.domain, 'pk': self.pk, })

    def srv_lookup(self, kind, domain):
        print('Checking xmpp-%s records for %s' % (kind, domain))
        key = '%s_records' % kind
        try:
            srv_records = resolver.query('_xmpp-%s._tcp.%s' % (kind, domain), 'SRV')
        except resolver.NoAnswer:
            self.data['dns']['srv'] = False
            self.data['dns'][kind] = False
            return

        has_ipv4 = False
        has_ipv6 = False

        for record in srv_records:
            host = record.target.split(1)[0].to_text()
            ip4, ip6 = [], []

            # do A/AAAA lookup
            try:
                ip4 = [r.address for r in resolver.query(host, 'A')]
                has_ipv4 = True
            except resolver.NXDOMAIN:
                # The domain name is not at all defined.
                self.data['dns']['srv'] = False
            except resolver.NoAnswer:
                # The domain name is defined, but there just is no A record. This is not an error
                # because there might be other records that provide an A record.
                pass

            if settings.USE_IP6:
                try:
                    ip6 = [r.address for r in resolver.query(host, 'AAAA')]
                    has_ipv6 = True
                except resolver.NoAnswer:
                    # The domain name is defined, but there just is no AAAA record. This is not an error
                    # because there might be other records that provide an AAAA record.
                    pass

            if not ip4 and not ip6:
                # This SRV target has neither an IPv4 nor an IPv6 record. We consider this faulty.
                # The most common mistake would be to point an SRV record to a domain with e.g.
                # only a MX or CNAME record.
                self.data['dns']['srv'] = False
                self.data['dns'][kind] = False

            self.data['dns'][key].append({
                'port': record.port,
                'host': host,
                'ips': ip4 + ip6,  # ip4 and ip6 combined
            })

        # We consider IPv4/6 support ok if there is at least one record of the given type.
        self.data['dns']['%s_ipv4' % kind] = has_ipv4
        self.data['dns']['%s_ipv6' % kind] = has_ipv6
        self.data['dns']['ipv4'] = has_ipv4 and self.data['dns']['ipv4']
        self.data['dns']['ipv6'] = has_ipv6 and self.data['dns']['ipv6']

    def start_test(self):
        domain = self.server.domain

        # set some default values...
        self.data['dns'] = {
            'status': None,
            'client': True,
            'client_ipv4': True,
            'client_ipv4': True,
            'server_ipv6': True,
            'server_ipv6': True,
            'client_records': [],
            'ipv4': True,
            'ipv6': True,
            'server': True,
            'server_records': [],
            'srv': True,
        }
        self.data['connect'] = {
            'status': None,
        }
        self.data['core'] = {
            'status': None,
            'details': {
                'bind': {'status': None, },  # Resource Binding
                'sasl': {'status': None, },  # SASL Authentication
                'session': {'status': None, },  # Session Establishment
                'tls': {'status': None, },  # TLS
            },
        }
        self.data['xeps'] = {
            'status': None,
            'details': {
                '0030': {'status': None, },  # Service Discovery
                '0077': {'status': None, },  # In-Band Registration
                '0078': {'status': None, },  # Non-SASL Authentication
                '0079': {'status': None, },  # Advanced Message Processing
                '0092': {'status': None, },  # Software Version
                '0138': {'status': None, },  # Stream Compression
                '0198': {'status': None, },  # Stream Management
                '0220': {'status': None, },  # Server Dialback
                '0288': {'status': None, },  # Bidirectional Server-to-Server Connections
                '0352': {'status': None, },  # Client State Indication
            },
        }

        # Do client SRV lookups
        self.srv_lookup('client', domain)
        self.srv_lookup('server', domain)

        self.data['dns']['ipv4'] = self.data['dns']['client_ipv4'] \
            and self.data['dns']['client_ipv6']
        self.data['dns']['ipv6'] = self.data['dns']['client_ipv6'] \
            and self.data['dns']['client_ipv6']

        self.data['dns']['status'] = self.data['dns']['srv'] and self.data['dns']['ipv4'] \
            and self.data['dns']['ipv6']
        if self.data['dns']['srv'] is False or self.data['dns']['client'] is False or \
                self.data['dns']['server'] is False:
            # This server has some serious DNS test issues, it should not be listed.
            self.finished = True
            self.server.listed = False
            self.server.save()
            return  # no SRV records

    def __str__(self):
        return '%s: %s' % (self.server.domain, self.created.strftime('%Y-%m-%d %H:%M'))
