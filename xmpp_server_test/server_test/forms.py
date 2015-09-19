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

class ServerTestForm(forms.Form):
    domain = forms.CharField(widget=_char_widget)
    username = forms.CharField(widget=_char_widget)
    password = forms.CharField(widget=_pwd_widget)


class ServerRetestForm(forms.Form):
    username = forms.CharField(widget=_char_widget)
    password = forms.CharField(widget=_pwd_widget)
