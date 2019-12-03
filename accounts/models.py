# from django.db import models
# from django.contrib.auth.models import User
# from django.conf import settings
# from django.contrib.auth import get_user_model
# # from tickets.models import Ticket
# from django.db.models.signals import post_save
#
#
# # class Profile(models.Model):
# #     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
# #     tickets = models.ManyToManyField(Ticket, blank=True)
# #
# #     def __str__(self):
# #         return self.user.username
# #
# # def post_save_profile_create(sender, instance, created, *args, **kwargs):
# #     if created:
# #         Ticket.objects.get_or_create(user=instance)
# # post_save.connect(post_save_profile_create, sender=settings.AUTH_USER_MODEL)
#
# class Ticketing(models.Model):
# 		ticket_name = models.CharField(max_length=250)
# 		ticket_location = models.CharField(max_length=250)
# 		organiser_name =models.CharField(max_length=250)
#
# 		def __self__(request):
#
#
#
#
#
# 	# """docstring for Ticketing"""
# 	#
# 	# def __init__(self, arg):
# 	# 	super(Ticketing, self).__init__()
# 	# 	self.arg = arg
#
