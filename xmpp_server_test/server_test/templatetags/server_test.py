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

from server_test.xeps import xeps

register = template.Library()

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
    elif value == 'required':
        text += 'label-success">' + _('Required') + '</span>'
    elif value == 'partial':
        text += 'label-warning">' + _('Partial') + '</span>'
    elif value == 'optional':
        text += 'label-warning">' + _('Optional') + '</span>'
    elif value is False:
        text += 'label-danger">' + _('No') + '</span>'
    else:
        text += 'label-danger">' + _('Unknown') + '</span>'
    return mark_safe(text)


@register.filter
def dictkeysort(value):
    return sorted(value.items(), key=lambda t: t[0])


@register.simple_tag(takes_context=True)
def xep(context, value, number):
    if xeps[number]['name'] is None:
        name = 'XEP-%s' % number
    else:
        name = 'XEP-%s: %s' % (number, xeps[number]['name'])

    td_name = '<td><a href="http://www.xmpp.org/extensions/xep-%s.html">%s</a></td>' % (number, name)
    td_status = '<td>%s</td>' % status(value['status'])
    if value.get('condition') and value['condition'] in _conditions:
        td_notes = '<td>%s</td>' % _conditions[value['condition']]
    elif xeps[number]['notes'] is not None:
        td_notes = '<td>%s</td>' % xeps[number]['notes'](value)
    else:
        td_notes = '<td>%s</td>' % value.get('notes', '')
    row = '<tr>%s%s%s</tr>' % (td_name, td_status, td_notes)
    return mark_safe(row)
