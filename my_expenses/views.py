from django.contrib.auth.models import User
from django.template.loader import get_template

from .forms import UserRegistrationForm, SearchHistoryForm
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import ModelFormMixin, FormMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Item
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

import datetime
from itertools import chain
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from .utils import render_to_pdf
from django.http import HttpResponse


class ItemListView(LoginRequiredMixin, ListView, FormMixin):
    template_name = 'items.html'
    # context_object_name = 'items'
    model = Item
    # paginate_by = 7
    form_class = SearchHistoryForm

    # def get(self, request, *args, **kwargs):
    #     # self.object = None
    #     # self.form = self.get_form_class()
    #     # return ListView.get(self, request, *args, **kwargs)
    #
    #     self.form = self.get_form_class()
    #     return super(ItemListView, self).get(request, *args, **kwargs)



    def get_context_data(self, *args, **kwargs):
        time = []
        total = []
        # context = self.get_context_data(**kwargs)
        # form = context['form']
        user = get_object_or_404(User, username=self.request.user.username)
        print(user)
        today_items = Item.objects.filter(user=user, added_on__day=(datetime.datetime.now()).day).order_by('-added_on')
        # q = User.objects.values('username').filter(username=user.username).annotate(total=Sum('item__price'))
        # print(q.query)
        q = today_items.aggregate(total=Sum('price'))
        today_total = q['total']

        four = Item.objects.filter(Q(user=user), Q(
            Q(Q(added_on__day__lte=(datetime.datetime.now()).day) &
              Q(added_on__month__lte=(datetime.datetime.now()).month)) |
            Q(Q(added_on__day__gte=(datetime.datetime.now() - datetime.timedelta(days=3)).day) &
              Q(added_on__month__gte=(datetime.datetime.now() - datetime.timedelta(days=28)).month)))). \
            order_by('-added_on')

        first = four.filter(added_on__day=datetime.datetime.now().day).aggregate(total=Coalesce(Sum('price'), 0))
        first_total = first['total']
        time.append(datetime.datetime.now().strftime('%a %d-%b'))
        total.append(first_total)

        second = four.filter(added_on__day=(datetime.datetime.now() - datetime.timedelta(days=1)).day). \
            aggregate(total=Coalesce(Sum('price'), 0))
        second_total = second['total']
        time.append((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%a %d-%b'))
        total.append(second_total)

        third = four.filter(added_on__day=(datetime.datetime.now() - datetime.timedelta(days=2)).day). \
            aggregate(total=Coalesce(Sum('price'), 0))
        third_total = third['total']
        time.append((datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%a %d-%b'))
        total.append(third_total)

        fourth = four.filter(added_on__day=(datetime.datetime.now() - datetime.timedelta(days=3)).day). \
            aggregate(total=Coalesce(Sum('price'), 0))
        fourth_total = fourth['total']
        time.append((datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%a %d-%b'))
        total.append(fourth_total)

        # print(f'COunt{}')
        # print(time)
        # daily = list(chain(last_three, today))
        context = {
            'today_items': today_items,
            'today_total': today_total,
            'total': total,
            'time': time,
            'form': self.get_form_class()
        }
        return context


class SearchHistoryView(FormMixin, View):
    form_class = SearchHistoryForm

    def post(self, request, *args, **kwargs):
        # context = self.get_context_data()
        form = self.get_form_class()
        if form.is_valid:
            date_input = self.request.POST.get('added_on')
            btn_value = self.request.POST.get('search_btn')
            print(f'BTN_VALUE={btn_value}')
            print(f'DateInput={date_input}')

            context = getQuery(self, date_input, btn_value)
            print(f"DATE =={context}")
            context['form'] = form
            context['date_input'] = date_input           
            if context['data']:
                return render(request, 'history.html', context)
            else:
               
                messages.error(self.request, f'No items are available on date {date_input}')
                return render(request, 'history.html', {'form': form})

class SignupView(CreateView):
    template_name = 'register.html'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')

        messages.success(self.request, f'User with username {username} is created!')
        return redirect('login')


class AddItemView(CreateView):
    model = Item
    fields = ['name', 'price']
    template_name = 'add_item.html'

    # success_url = reverse_lazy('items')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateItemView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    fields = ['name', 'price']
    template_name = 'item_update.html'

    # success_url = reverse_lazy('items')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Item successfully deleted!")
        return super().form_valid(form)

    def test_func(self):
        item = self.get_object()
        if self.request.user == item.user:
            return True
        return False


class DeleteItemView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = 'item_delete.html'
    model = Item
    success_url = reverse_lazy('items')

    def test_func(self):
        item = self.get_object()
        if self.request.user == item.user:
            return True
        return False


class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        date_input = request.GET.get('pdf')
        btn_value = request.GET.get('pdf-form')
        print(f'btn_value_pdf = {btn_value}')

        context = getQuery(self, date_input, btn_value)

        context['username'] = self.request.user.username
        
        
        template = get_template('pdf/invoice.html')
        
        html = template.render(context)
        pdf = render_to_pdf('pdf/invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %("12341231")
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")



def getQuery(self, date_input, btn_value):
    date = datetime.datetime.strptime(date_input, '%Y-%m-%d').date()
    month = Item.objects.filter(Q(user__username=self.request.user.username),
                                Q(added_on__year=date.year),
                                Q(added_on__month=date.month),
                                )
    if not btn_value:
        day = month.filter(added_on__day=date.day)
    
        context = {
            'data':day,
            'total': (day.aggregate(total=Sum('price')))['total'],
            'date': date
        }
        print(f'Context= {self.request.user.username}')
        return context

    elif btn_value == "month":

        total = month.aggregate(total=Sum('price'))
    
        context = {
            'data':month,
            'total': (month.aggregate(total=Sum('price')))['total'],
            'date': date
        }
        return context




'''
    four = User.objects.filter(Q(username='thapa'), Q(
            Q(Q(item__added_on__day__lte=(datetime.datetime.now()).day) &
              Q(item__added_on__month__lte=(datetime.datetime.now()).month)) |
            Q(Q(item__added_on__day__gte=(datetime.datetime.now() - datetime.timedelta(days=3)).day) &
              Q(item__added_on__month__gte=(datetime.datetime.now() - datetime.timedelta(days=28)).month)))). \
            annotate(sum=Sum('item__price')).values('item__added_on__day','sum').order_by('-item__added_on')
'''
