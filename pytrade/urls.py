from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('', RedirectView.as_view(url='core/login', permanent=True)),
    path('accounts/', include('django.contrib.auth.urls')),
]