from django.contrib import admin
from django.urls import path, include
from .import views as home_view
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views
from django.conf.urls import handler404, handler500
from tickets import views as ticket_views
from tickets import views
from xyzshopping import views as common_view
from .views import Comming_soon
# handler404 = 'common_view.custom_404'

urlpatterns = [
    path('hitcount/', include('hitcount.urls'), name='hitcount'),
    path('admin/', admin.site.urls),
    path('', include('tickets.urls')),
    path('visitors/home/', ticket_views.ticket_filter, name='home_view'),
    path('', Comming_soon, name='comming_soon'),
    path('team/', ticket_views.About_us.as_view(), name='about_us'),
    path('blog/', ticket_views.Blog.as_view(), name='blog'),
    path('accounts/', include('accounts.urls')),
    path('auth/', include('allauth.urls')),
    # path('tinymce/', include('tinymce.urls')),
    path('profile/', accounts_views.Profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    # path('listview/', Ticket_ListView, name='lists'),
    # path('api/chart/data/', ChartData.as_view(), name='api-chart-data'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Agatike - Administration'