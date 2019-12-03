from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser

class Included(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
#
# class TicketType(models.Model):
#     name = models.CharField(max_length=50)
#     # price = models.FloatField()
#     # limit = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return '%s ($%.2f)' % (self.name, self.price)


class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Ticket(models.Model):
    ticket_title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    ticket_added_time = models.DateTimeField(auto_now=True)
    starting_hour = models.TimeField()
    ending_hour = models.TimeField()
    ending_date = models.DateField()
    ticket_banner = models.FileField(default='default.jpg')
    ticket_description = models.TextField(max_length=10000)
    # ticket_price = models.FloatField(max_length=250)
    # ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, null=True, blank=True)
    ticket_name_1 = models.CharField(max_length=100)
    price_1 = models.FloatField()
    quantity_1 = models.IntegerField()
    bonus_1 = models.CharField(max_length=60, blank=True, null=True)
    ticket_name_2 = models.CharField(max_length=100, null=True, blank=True)
    price_2 = models.FloatField(null=True, blank=True)
    quantity_2 = models.IntegerField(null=True, blank=True)
    bonus_2 = models.CharField(max_length=60, blank=True, null=True)
    ticket_name_3 = models.CharField(max_length=100, null=True, blank=True)
    price_3 = models.FloatField(null=True, blank=True)
    quantity_3 = models.IntegerField(null=True, blank=True)
    bonus_3 = models.CharField(max_length=60, blank=True, null=True)
    price_choices = (
        ('ticket', ''),
    )
    currency_choices = (
        ('RWF', 'RWF'),
    )
    currency = models.CharField(max_length=100, default='choose', choices=currency_choices)
    # seller_name = models.ForeignKey(UserManagement, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    starting_date = models.DateField()
    organizer_name = models.CharField(max_length=100, null=True, blank=True)
    organizer_description = models.TextField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.ticket_title

    def snippet(self):
        return self.ticket_title[:20] + '...'

    def get_absolute_url(self):
        return reverse('tickets:list_view', kwargs={
            'pk': self.pk
        })

    def get_add_to_cart_url(self):
        return reverse('tickets:add_cart', kwargs={
            'pk': self.pk
        })

    def get_remove_from_cart(self):
        return reverse('tickets:remove_cart', kwargs={
            'pk': self.pk
        })


class AddedTicket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    tickets = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    # ticket_types = models.ManyToManyField(TicketTypes)

    def __str__(self):
        return f"{self.quantity} of {self.tickets.ticket_title}"

    # def get_total_ticket_price(self):
    #     return self.quantity * self.tickets.
    #
    # def get_final_price(self):
    #     return self.get_total_ticket_price()

    def tickets_available(self):
        return max(self.quantity - self.tickets.objects.count(), 0)


class Added(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tickets = models.ManyToManyField(AddedTicket)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    # def get_total(self):
    #     total = 0
    #     for added_ticket in self.tickets.all():
    #         total += added_ticket.get_final_price()
    #     return total


# class TicketPurchase(models.Model):
#     email = models.EmailField(default='', verbose_name="email")
#     name = models.CharField(max_length=100)
#     date = models.DateField(auto_now_add=True, editable=False)
#     amount = models.FloatField()
    status = models.CharField(default='pending', max_length=20)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.status)

    def paid(self):
        return "completed" in self.status

    def invoice(self):
        return self.id