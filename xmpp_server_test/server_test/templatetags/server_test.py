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


from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

register = template.Library()


_xep_names = {
    '0030': 'Service Discovery',
    '0077': 'In-Band Registration',
    '0078': 'Non-SASL Authentication',
    '0079': 'Advanced Message Processing',
    '0092': 'Software Version',
    '0115': 'Entity Capabilities',
    '0138': 'Stream Compression',
    '0198': 'Stream Management',
    '0220': 'Server Dialback',
    '0288': 'Bidirectional Server-to-Server Connections',
    '0352': 'Client State Indication',
}
_conditions = {
    'feature-not-implemented': _('Not supported.'),
}


@register.filter
def status(value):
    text = '<span class="label '
    if value is None:
        text += 'label-default">' + _('Pending') + '</span>'
    elif value is True:
        text += 'label-success">' + _('OK') + '</span>'
    elif value is False:
        text += 'label-danger">' + _('Failed') + '</span>'
    elif value == 'no':
        text += 'label-danger">' + _('No') + '</span>'
    else:
        text += 'label-danger">' + _('Unknown') + '</span>'
    return mark_safe(text)


@register.filter
def xep(value, number):
    if _xep_names.get(number):
        name = 'XEP-%s: %s' % (number, _xep_names[number])
    else:
        name = 'XEP-%s' % number

    td_name = '<td><a href="http://www.xmpp.org/extensions/xep-%s.html">%s</a></td>' % (number, name)
    td_status = '<td>%s</td>' % status(value[number]['status'])
    if value[number].get('condition') and value[number]['condition'] in _conditions:
        td_notes = '<td>%s</td>' % _conditions[value[number]['condition']]
    else:
        td_notes = '<td>%s</td>' % value[number].get('notes', '')
    row = '<tr>%s%s%s</tr>' % (td_name, td_status, td_notes)
    return mark_safe(row)
