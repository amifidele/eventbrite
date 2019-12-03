from django.urls import path
from .import views
from .views import add_to_cart, remove_to_cart, remove_single_ticket_to_cart, Category_detail, ChartData
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'tickets'

urlpatterns = [
    # ticket/api/view/
    path('tickets/api/view/', views.TicketsApi.as_view()),
    # tickets/list/
    path('all-tickets/', views.ticket_list_filter, name='list_view'),
    # tickets/affiliate/help/
    path('affiliate/help/', views.Affiliate_help.as_view(), name='affiliate_help'),
    # # tickets/team/
    # path('team/', views.About_us.as_view(), name='team'),
    # # tickets/team/
    # path('blog/', views.Blog.as_view(), name='blog'),
    # tickets/5/details/
    path('<int:pk>/details/', views.Ticket_details.as_view(), name='ticket_detail'),
    # tickets/create/
    path('create/', views.Create_ticket.as_view(), name='create_ticket'),
    # tickets/5/update/
    path('<int:pk>/update/', views.Update_ticket.as_view(), name='update_ticket'),
    # tickets/5/delete/
    path('<int:pk>/delete/', views.Delete_ticket.as_view(), name='delete_ticket'),
    # tickets/help/affiliate/
    path('help/', views.Main_help.as_view(), name='main_help'),
    # tickets/add/cart/
    path('<int:pk>/add/cart/', add_to_cart, name='add_cart'),
    # tickets/remove/cart/
    path('<int:pk>/remove/cart/', remove_to_cart, name='remove_cart'),
    #tickets/order-summary/
    path('order/summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    # tickets/remove/cart/
    path('<int:pk>/remove/ticket/cart/', remove_single_ticket_to_cart, name='remove_single_ticket_cart'),
    #tickets/checkout/
    path('checkout/', views.CheckOutView.as_view(), name='checkout'),
    #category/cinema/
    path('category/<str:slug>/', Category_detail, name='category'),
    path('category/cinema/', Category_detail, name='category_cinema'),
    path('category/sport/', Category_detail, name='category_sport'),
    path('category/concert/', Category_detail, name='category_concert'),
    path('category/expo/', Category_detail, name='category_expo'),
    path('category/meeting/', Category_detail, name='category_meeting'),
    path('category/others/', Category_detail, name='category_others'),
    path('category/festival/', Category_detail, name='category_festival'),
    path('api/data/', ChartData.as_view(), name='dash-api'),
    path('dashboard/', views.DashView.as_view(), name='dashboard_affiliates'),



]

urlpatterns = format_suffix_patterns(urlpatterns)











