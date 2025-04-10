from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

lang = 'en'
#############################
urlpatterns = [
    path('', views.index, name="index"),
    path('accounts/verify/', views.VerifyAccount, name="verify-account"),
    path('reset/password/', views.ResetPassword, name="reset-password"),
    path('app/reset/password/', views.AppResetPassword, name="app-reset-password"),
    path('params/', views.getParams, name="get-params"),
]
#############################
urlpatterns = urlpatterns + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)