from rest_framework import serializers
from .models import Ticket

class TicketSerializers(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id', 'ticket_title', 'available_tickets', 'ticket_price', 'currency', 'organizer_name')
        # fields = '__all__'