from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # Normal kullanıcı sayfaları
    path('pdfs/', views.pdfs_view, name='pdfs'),
    path('ekolarka-sorular/', views.ekolarka_sorular_view, name='ekolarka_sorular'),
    path('gunluk-soru/', views.gunluk_soru_view, name='gunluk_soru'),
    # Admin panel (uygulama içi)
    path('admin/', views.admin_home_view, name='admin_home'),
    path('admin/users/', views.user_management_view, name='user_management'),
    path('admin/users/add/', views.add_user_view, name='add_user'),
    path('admin/users/delete/<int:user_id>/', views.delete_user_view, name='delete_user'),
    path('logout/', views.logout_view, name='logout'),
]
