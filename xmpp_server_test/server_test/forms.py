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

from django import forms

_attrs = {'class': 'form-control'}
_char_widget = forms.TextInput(attrs=_attrs)
_pwd_widget = forms.PasswordInput(attrs=_attrs)


def _as_bootstrap(self):
    return self._html_output(
        normal_row='<div class="form-group">%(label)s %(field)s %(help_text)s</div>',
        error_row='%s',
        row_ender='</div>',
        help_text_html=' <p class="help-block">%s</p>',
        errors_on_separate_row=True)

class ServerTestForm(forms.Form):
    domain = forms.CharField(widget=_char_widget)
    username = forms.CharField(widget=_char_widget)
    password = forms.CharField(widget=_pwd_widget)
    as_bootstrap = _as_bootstrap

class ServerRetestForm(forms.Form):
    username = forms.CharField(widget=_char_widget)
    password = forms.CharField(widget=_pwd_widget)
    as_bootstrap = _as_bootstrap
