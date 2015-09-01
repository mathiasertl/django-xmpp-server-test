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

    def test(self):
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

    def srv_lookup(self, kind, domain):
        key = '%s_records' % kind
        try:
            for record in resolver.query('_xmpp-%s._tcp.%s' % (kind, domain), 'SRV'):
                host = record.target.split(1)[0].to_text()

                # do A/AAAA lookup
                ips = []
                try:
                    for a in resolver.query(host, 'A'):
                        ips.append(a.address)
                except resolver.NXDOMAIN:
                    self.data['dns']['ipv4'] = False
                try:
                    for aaaa in resolver.query(host, 'AAAA'):
                        ips.append(aaaa.address)
                except resolver.NXDOMAIN:
                    self.data['dns']['ipv6'] = False

                self.data['dns'][key].append({
                    'port': record.port,
                    'host': host,
                    'ips': ips,
                })

            # check if there is at least one record pointing to at least one IP
            validity = [bool(e['ips']) for e in self.data['dns'][key]]
            if True not in validity:
                self.data['dns'][kind] = False
        except resolver.NoAnswer:
            self.data['dns']['srv'] = False
            self.data['dns'][kind] = False

    def start_test(self):
        server = self.server
        domain = server.domain

        self.data['dns'] = {
            'client_records': [],
            'client': True,
            'ipv4': True,
            'ipv6': True,
            'server_records': [],
            'server': True,
            'srv': True,
        }

        # Do client SRV lookups
        self.srv_lookup('client', domain)
        self.srv_lookup('server', domain)

        if self.data['dns']['srv'] is False or self.data['dns']['client'] is False or \
                self.data['dns']['server'] is False:
            return  # no SRV records

        self.finished = True

    def __str__(self):
        return '%s: %s' % (self.server.domain, self.created.strftime('%Y-%m-%d %H:%M'))
