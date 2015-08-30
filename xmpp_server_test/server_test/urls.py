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

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.RootView.as_view(), name='overview'),
    url(r'^(?P<domain>[^/]+)/$', views.ServerView.as_view(), name='server'),
    url(r'^(?P<domain>[^/]+)/(?P<pk>\d+)/$', views.ServerTestView.as_view(), name='servertest'),
]
