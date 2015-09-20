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

from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .forms import ServerTestForm
from .forms import ServerRetestForm
from .models import Server
from .models import ServerTest
from .tasks import test_server


class TestContextMixin(object):
    def add_test_context(self, context):
        context['foobar'] = 'whatever'


class RootView(ListView, FormMixin):
    template_name = 'server_test/root.html'
    queryset = Server.objects.filter(listed=True)
    form_class = ServerTestForm

    def get_context_data(self, **kwargs):
        context = super(RootView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        domain = form.cleaned_data['domain']
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        server, _created = Server.objects.get_or_create(domain=domain)
        test = server.test()
        if test.finished is False:
            test_server.delay(test=test.pk, username=username, password=password)
        return HttpResponseRedirect(test.get_absolute_url())

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class FullListView(ListView):
    queryset = Server.objects.filter(listed=True).order_by('domain')


class ServerView(DetailView, TestContextMixin):
    queryset = Server.objects.all()
    context_object_name = 'server'
    slug_field = 'domain'
    slug_url_kwarg = 'domain'

    def get_context_data(self, **kwargs):
        context = super(ServerView, self).get_context_data(**kwargs)
        context['test'] = self.object.latest_test
        context['data'] = context['test'].data
        self.add_test_context(context)
        return context


class ServerRetestView(FormView, SingleObjectMixin):
    queryset = Server.objects.all()
    context_object_name = 'server'
    slug_field = 'domain'
    slug_url_kwarg = 'domain'
    form_class = ServerRetestForm
    template_name = 'server_test/retest.html'

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super(ServerRetestView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ServerRetestView, self).get_context_data(**kwargs)
        context['server'] = self.object
        return context

    def form_valid(self, form):
        test = self.object.test()

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        if test.finished is False:
            test_server.delay(test=test.pk, username=username, password=password)
        return HttpResponseRedirect(test.get_absolute_url())


class ServerTestView(DetailView, TestContextMixin):
    queryset = ServerTest.objects.select_related('server')
    context_object_name = 'test'

    def get_context_data(self, **kwargs):
        context = super(ServerTestView, self).get_context_data(**kwargs)
        context['data'] = context['test'].data
        context['server'] = context['test'].server
        self.add_test_context(context)
        return context


class RefreshServerTestView(ServerTestView):
    template_name = 'server_test/test.html'
