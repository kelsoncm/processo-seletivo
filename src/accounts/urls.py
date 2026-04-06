from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('callback/', views.CallbackView.as_view(), name='callback'),
    path('suap/callback/', views.SuapCallbackView.as_view(), name='suap_callback'),
    path('django/login/', views.DjangoLoginView.as_view(), name='django_login'),
]
