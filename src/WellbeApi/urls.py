"""WellbeApi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('api/v1/users/', include('api.v1.users.urls')),
    path('api/v1/products/', include('api.v1.products.urls')),
    path('api/v1/texts/', include('api.v1.texts.urls')),
    path('api/v1/surveys/', include('api.v1.surveys.urls')),
    path('api/v1/recommendations/', include('api.v1.recommendations.urls')),
    path('api/v1/worksheets/buying/', include('api.v1.worksheets.BuyingForms.urls')),
]
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
