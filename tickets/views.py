from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http.response import HttpResponse
from django.views import generic
from django.contrib import messages
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Ticket, AddedTicket, Added, Category

from .forms import CheckOut
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TicketSerializers


class TicketsApi(APIView):
    
    def get(self, request):
        ticket = Ticket.objects.all()
        serializer = TicketSerializers(ticket, many=True)
        return Response(serializer.data)
    def post(self):
        pass



def index_ticket_view(request):
    tickets = Ticket.objects.all().order_by('-ticket_added_time')
    page = request.GET.get('page', 1)

    paginator = Paginator(tickets, 3)
    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)
    return render(request, 'index.html', {'tickets': tickets})



class Ticket_list_view(generic.ListView):
    template_name = 'tickets/event_list.html'
    context_object_name = 'tickets_list'
    ordering = ['-ticket_added_time']
    paginate_by = 9

    def get_queryset(self):
        return Ticket.objects.all().order_by('-ticket_added_time')
#

class Create_ticket(LoginRequiredMixin, CreateView):
    model = Ticket
    fields = ('ticket_title', 'location', 'starting_hour', 'starting_date', 'ending_date', 'ending_hour', 'ticket_banner', 'price_1', 'price_2', 'ticket_name_1', 'ticket_name_2', 'quantity_1', 'quantity_2', 'bonus_1', 'bonus_2', 'ticket_description', 'category', 'currency', 'organizer_name', 'organizer_description')
    success_url = reverse_lazy('tickets:dashboard_affiliates')
    login_url = 'login'
    redirect_field_name = 'tickets:create_ticket'

class Ticket_details(generic.DetailView):
    model = Ticket
    template_name = 'tickets/event_details.html'
    context_object_name = 'tickets_detail'

def Category_detail(request, slug):
    template = 'tickets/category_detail.html'
    category = get_object_or_404(Category, slug=slug)
    tickets = Ticket.objects.filter(category=category)
    page = request.GET.get('page', 1)
    paginator = Paginator(tickets, 6)
    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)
    context = {
        'category': category,
        'tickets': tickets,
    }
    return render(request, template, context)



class Update_ticket(LoginRequiredMixin, UpdateView):
    model = Ticket
    fields = ('ticket_title', 'location', 'starting_hour', 'starting_date', 'ending_date', 'ending_hour', 'ticket_banner', 'price_1', 'price_2', 'ticket_name_1', 'ticket_name_2', 'quantity_1', 'quantity_2', 'bonus_1', 'bonus_2', 'ticket_description', 'category', 'currency', 'organizer_name', 'organizer_description')
    success_url = reverse_lazy('tickets:list_view')

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Added.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'tickets/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "you do not have an active order")
            return redirect('tickets:list_view')

        # return render(self.request, 'tickets/order_summary.html')



class Delete_ticket(LoginRequiredMixin, DeleteView):
    model = Ticket
    success_url = reverse_lazy('tickets:list_view')



class Affiliate_help(generic.ListView):
    model = Ticket
    template_name = 'tickets/affiliate_help.html'
    context_object_name = 'affiliate_help'


class About_us(generic.ListView):
    model = Ticket
    template_name = 'tickets/About.html'
    context_object_name = 'about_us'

class Blog(generic.ListView):
    model = Ticket
    template_name = 'tickets/Blog.html'
    context_object_name = 'blog'



class Main_help(generic.ListView):
    model = Ticket
    template_name = 'tickets/help.html'
    context_object_name = 'main_help'


class CheckOutView(View):
    def get(self, *args, **kwargs):
        form = CheckOut()
        context = {
            'form': form
        }
        return render(self.request, "tickets/checkout.html", context)
    def post(self, *args, **kwargs):
        form = CheckOut(self.request.POST or None)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            city = form.cleaned_data.get('city')
            payment_option = form.cleaned_data.get('payment_option')
            country = form.cleaned_data.get('country')
            save_info = form.cleaned_data.get('save_info')
            phone_number = form.cleaned_data.get('phone_number')
            print('this form is valid')
            return redirect('tickets:checkout')
        messages.warning(self.request, "Failed to checkout")
        return redirect('tickets:checkout')


@login_required
def add_to_cart(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    order_ticket, created = AddedTicket.objects.get_or_create(
        tickets=ticket,
        user=request.user,
        ordered=False)
    added_qs = Added.objects.filter(user=request.user, ordered=False)
    if added_qs.exists():
        order = added_qs[0]
        if order.tickets.filter(tickets__pk=ticket.pk).exists():
            order_ticket.quantity += 1
            order_ticket.save()
            messages.info(request, "this Ticket quantity was updated.")
        else:
            # order = Added.objects.create(user=request.user)
            order.tickets.add(order_ticket)
    else:
        ordered_date = timezone.now()
        order = Added.objects.create(
                user=request.user,
                ordered_date=ordered_date,
            )
        order.tickets.add(order_ticket)
        messages.info(request, "this Ticket added to cart.")

    return redirect("tickets:order-summary")


def remove_to_cart(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    added_qs = Added.objects.filter(user=request.user, ordered=False)
    if added_qs.exists():
        order = added_qs[0]
        if order.tickets.filter(tickets__pk=ticket.pk).exists():
            order_ticket = AddedTicket.objects.filter(
                tickets=ticket,
                user=request.user,
                ordered=False)[0]
            order.tickets.remove(order_ticket)
            messages.info(request, "Ticket removed from cart.")
        else:
            messages.info(request, "this item was not in the cart.")
            return redirect("tickets:list_view")
    else:
        return redirect("tickets:list_view")
    return redirect("tickets:order-summary")



def remove_single_ticket_to_cart(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    added_qs = Added.objects.filter(user=request.user, ordered=False)
    if added_qs.exists():
        order = added_qs[0]
        if order.tickets.filter(tickets__pk=ticket.pk).exists():
            order_ticket = AddedTicket.objects.filter(
                tickets=ticket,
                user=request.user,
                ordered=False)[0]
            if order_ticket.quantity > 1:
                order_ticket.quantity -= 1
                order_ticket.save()
            else:
                order.tickets.remove(order_ticket)
                messages.info(request, "Ticket quantity was updated.")
            return redirect('tickets:order-summary')
        else:
            messages.info(request, "this item was not in the cart.")
            return redirect("tickets:order-summary")
    else:
        return redirect("tickets:order-summary")


def is_valid_queryparam(param):
    return param != '' and param is not None

def ticket_list_filter(request):
    qs = Ticket.objects.all().order_by('-ticket_added_time')
    # page = request.GET.get('page', 1)
    # paginator = Paginator(qs, 9)
    # try:
    #     qs = paginator.page(page)
    # except PageNotAnInteger:
    #     qs = paginator.page(1)
    # except EmptyPage:
    #     qs = paginator.page(paginator.num_pages)

    title_name = request.GET.get('title_contain')
    ticket_min_price_query = request.GET.get('min_price')
    ticket_max_price_query = request.GET.get('max_price')

    if is_valid_queryparam(title_name):
        qs = qs.filter(ticket_title__icontains=title_name)

    if is_valid_queryparam(ticket_min_price_query):
        qs = qs.filter(ticket_price__gte=ticket_min_price_query)

    if is_valid_queryparam(ticket_max_price_query):
        qs = qs.filter(ticket_price__lte=ticket_max_price_query)

    return render(request, 'tickets/event_list.html', {'queryset': qs})



def ticket_filter(request):
    qs = Ticket.objects.all().order_by('-ticket_added_time')
    # page = request.GET.get('page', 1)
    # paginator = Paginator(qs, 3)
    # try:
    #     qs = paginator.page(page)
    # except PageNotAnInteger:
    #     qs = paginator.page(1)
    # except EmptyPage:
    #     qs = paginator.page(paginator.num_pages)

    ticket_name_query = request.GET.get('ticket_name')
    ticket_location_query = request.GET.get('ticket_location')
    ticket_max_date_query = request.GET.get('max_date')
    ticket_min_date_query = request.GET.get('min_date')

    if is_valid_queryparam(ticket_name_query):
        qs = qs.filter(ticket_title__icontains=ticket_name_query)

    if is_valid_queryparam(ticket_location_query):
        qs = qs.filter(location__icontains=ticket_location_query)

    if is_valid_queryparam(ticket_min_date_query):
        qs = qs.filter(starting_date__gte=ticket_min_date_query)

    if is_valid_queryparam(ticket_max_date_query):
        qs = qs.filter(starting_date__lte=ticket_max_date_query)


    context = {
        'queryset': qs
    }
    return render(request, 'index.html', context)


class DashView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/dashboard.html', {})


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        # ticket_available = Ticket.available_tickets
        users_added_tickets = Added.objects.all().count()
        added_tickets = AddedTicket.objects.all().count()
        live_tickets = Ticket.objects.all().count()
        labels = ['Live Tickets', 'Ticket in Cart', 'User Added ticket', 'thur', 'fri', 'sat', 'sun']
        default_items = [live_tickets, added_tickets, users_added_tickets]
        data = {
            "labels": labels,
            "default": default_items,
        }

        return Response(data)


