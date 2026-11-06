from django.contrib import admin
from django.urls import include, path
from apps import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.ingresar, name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.salir, name='logout'),
    path('', include('apps.urls')),
]
