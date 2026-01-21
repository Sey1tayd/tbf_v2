"""
URL configuration for tbf_panel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# Admin panel başlıklarını özelleştir
admin.site.site_header = "Basketbol Oyun Kuralları ve Yorumları"
admin.site.site_title = "Basketbol Oyun Kuralları ve Yorumları"
admin.site.index_title = "Yönetim Paneli"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # STATIC_URL için Django'nun staticfiles app'i zaten hallediyor
    # Sadece MEDIA_URL'i manuel olarak serve ediyoruz

