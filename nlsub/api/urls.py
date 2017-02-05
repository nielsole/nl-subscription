"""nlsub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView
from api.views import subscribe, confirm_subscribe, confirm_unsubscribe, send

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^lists/([\w]{1,30})/subscribe/', subscribe),
    url(r'^subscribe$', confirm_subscribe),
    url(r'^unsubscribe$', confirm_unsubscribe),
    url(r'^send$', send)
]

from rest_framework.authtoken import views
urlpatterns += [
    url(r'^api-token-auth/', views.obtain_auth_token)
]
