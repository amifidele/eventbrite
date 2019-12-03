from django.contrib import admin
from .models import Ticket, Added, AddedTicket, Category, Included


# Register your models here.

admin.site.register(Ticket)
admin.site.register(AddedTicket)
admin.site.register(Added)
admin.site.register(Included)
admin.site.register(Category)

