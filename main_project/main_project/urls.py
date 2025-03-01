"""
URL configuration for main_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls .i18n import i18n_patterns

handler404 = 'pdfapp.views.not_found'

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('', include('pdfapp.urls')),
    path('i18n/', include('django.conf.urls.i18n')),

    #prefix_default_language=False
 ) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT) \
+  static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)