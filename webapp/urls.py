from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

lang='en'
#############################
urlpatterns = [
 path('', views.index, name="index"),
 path('accounts/verify/', views.VerifyAccount, name="verify-account"),
]
#############################
urlpatterns = urlpatterns + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)