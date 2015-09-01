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

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView

from .forms import DomainForm
from .models import Server
from .models import ServerTest


class RootView(ListView, FormMixin):
    template_name = 'server_test/root.html'
    queryset = Server.objects.all()
    form_class = DomainForm

    def get_context_data(self, **kwargs):
        context = super(RootView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        domain = form.cleaned_data['domain']
        server, created = Server.objects.get_or_create(domain=domain)

        # TODO: If created, check for a very recent test
        test = server.test()
        url = reverse('server-test:servertest', kwargs={'domain': domain, 'pk': test.pk})

        return HttpResponseRedirect(url)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class FullListView(ListView):
    queryset = Server.objects.all()


class ServerView(DetailView):
    queryset = Server.objects.all()
    context_object_name = 'server'
    slug_field = 'domain'
    slug_url_kwarg = 'domain'

    def get_context_data(self, **kwargs):
        context = super(ServerView, self).get_context_data(**kwargs)
        context['test'] = self.object.latest_test
        context['data'] = context['test'].data
        return context


class ServerTestView(DetailView):
    template_name = 'server_test/server_detail.html'
    queryset = ServerTest.objects.select_related('server')
    context_object_name = 'test'

    def get_context_data(self, **kwargs):
        context = super(ServerTestView, self).get_context_data(**kwargs)
        context['data'] = context['test'].data
        context['server'] = context['test'].server
        return context
