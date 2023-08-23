# from django.conf import settings
# from django.conf.urls.static import static
# from django.urls import path
# from rest_framework.authtoken import views
# # from .v1.users.UsersView import CreateAuthUser, CreateUserAuthToken
# import importlib

# DEFAULT_API_VERSION="v1"
# ####################
# user_view = importlib.import_module(f"api.{DEFAULT_API_VERSION}.users.UsersView")
# ##################
# urlpatterns = [
# #  path('', views.index.as_view(), name="index"),
#  path('auth', views.obtain_auth_token),
#  path('<str:lang>/auth/token/', user_view.CreateUserAuthToken.as_view(), name="create-user-token"),
#  path('<str:lang>/auth/user/', user_view.GetAuthUser.as_view(), name="get-auth-user"),
#  path('<str:lang>/auth/user/<int:userid>/', user_view.GetAuthUserById.as_view(), name="get-auth-user-by-id"),
#  path('<str:lang>/auth/users/all', user_view.GetAllUsers.as_view(), name="get-all-users"),
# ]
# urlpatterns = urlpatterns + \
#     static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .v1.uploading import UploadView
import importlib

DEFAULT_API_VERSION = "v1"
####################
user_view = importlib.import_module(
    f"api.{DEFAULT_API_VERSION}.users.UsersView")
upload = importlib.import_module(
     f"api.{DEFAULT_API_VERSION}.uploading.UploadView"
)
##################
urlpatterns = [
     
    path('', views.index.as_view(), name="index"),
    path('<str:lang>/register/user/',
         user_view.CreateAuthUser.as_view(), name="register-user"),
    path('<str:lang>/make/deposit/',
         views.MakeDeposit.as_view(), name="make-deposit"),
    path('<str:lang>/make/card/deposit/',
         views.MakeDepositToBank.as_view(), name="make-card-deposit"),
    path('<str:lang>/get/deposit/',
         views.GetDepositsByAuthUser.as_view(), name="get-deposit"),
    path('<str:lang>/make/bank/withdraw/',
         views.MakeWithdrawFromBank.as_view(), name="make-bank-withdraw"),
    path('<str:lang>/make/goal/bank/withdraw/',
         views.MakeGoalWithdrawFromBank.as_view(), name="make-goal-bank-withdraw"),
    path('<str:lang>/make/mm/withdraw/',
         views.MakeWithdrawFromMobileMoney.as_view(), name="make-mm-withdraw"),
    path('<str:lang>/make/goal/mm/withdraw/',
         views.MakeGoalWithdrawFromMobileMoney.as_view(), name="make-goal-mm-withdraw"),
    path('<str:lang>/get/withdraw/',
         views.GetWithdrawsByAuthUser.as_view(), name="get-all-withdraws"),
    path('<str:lang>/get/pending/withdraw/',
         views.GetPendingWithdrawsByAuthUser.as_view(), name="get-all-pending-withdraws"),
    path('<str:lang>/get/goal/withdraw/',
         views.GetWithdrawNetworths.as_view(), name="get-goal-withdraws"),
    path('<str:lang>/get/deposit/by/id/',
         views.GetDepositsById.as_view(), name="get-deposit-by-id"),
    path('<str:lang>/get/deposit/by/goal/<int:goalid>/',
         views.GetDepositsByGoalId.as_view(), name="get-deposit-by-goal"),
    path('<str:lang>/create/goal/',
         views.CreateGoal.as_view(), name="create-goal"),
    path('<str:lang>/user/nextOfKin/',
         views.AddNextOfKin.as_view(), name="add-nextOfKin"),
    path('<str:lang>/get/nextOfKin/',
         views.GetNextOfKin.as_view(), name="get-nextOfKin"),
    path('<str:lang>/get/user/goal/',
         views.GetGoalsByAuthUser.as_view(), name="get-user-goal"),
    path('<str:lang>/get/goal/by/id/',
         views.GetGoalById.as_view(), name="get-goal-by-id"),
    path('<str:lang>/get/withdraw/fee/',
         views.GetWithdrawFee.as_view(), name="get-withdraw-fee"),
    path('<str:lang>/make/goal/deposit/',
         views.MakeDepositToGoal.as_view(), name="deposit-to-goal"),
    path('<str:lang>/make/subscription/',
         views.Subscribe.as_view(), name="make-subscription"),
    path('<str:lang>/get/subscription/status/',
         views.GetSubscriptionStatus.as_view(), name="get-subscription-status"),
    path('<str:lang>/auth/user/login/',
         user_view.LoginUserAuthToken.as_view(), name="login-user"),
    path('<str:lang>/auth/token/', 
         views.CreateUserAuthToken.as_view(), name="create-user-token"),
    path('<str:lang>/auth/user/',
         user_view.GetAuthUser.as_view(), name="get-auth-user"),
    path('<str:lang>/auth/user/riskprofile/',
         views.AddRiskProfile.as_view(), name="add-risk-profile"),
    path('<str:lang>/auth/get/riskprofile/',
         views.GetRiskProfile.as_view(), name="get-risk-profile"),
    path('<str:lang>/auth/user/<int:userid>/',
         user_view.GetAuthUserById.as_view(), name="get-auth-user-by-id"),
    path('<str:lang>/auth/users/all/',
         user_view.GetAllUsers.as_view(), name="get-all-users"),
    path('<str:lang>/auth/user/networth/',
         views.GetGoalNetworth.as_view(), name="get-user-networth"),
#     path('<str:lang>/auth/user/bank/transfer/',
#          views.BankTransfer.as_view(), name="get-transfer"),
    path('<str:lang>/auth/user/upload/profile/photo/',
         UploadView.UploadPhoto.as_view(), name="upload-photo"),
    path('<str:lang>/auth/user/update/password/',
         user_view.UpdateAuthUserPassword.as_view(), name="update-user-password"),
    path('<str:lang>/password/reset/',
         user_view.InitPasswordReset.as_view(), name="password-reset"),
     path('<str:lang>/email/verify/<str:userid>/',user_view.verifyAccount.as_view(),name = "email-verify"),
    path('<str:lang>/onboard/',user_view.OnboardAuthUsers.as_view(),name = "onboard-users"),
    path('<str:lang>/auth/user/delete/',user_view.DeleteUserAccount.as_view(),name = "delete-user-account"),
    path('deposit/',views.DepositDataSet.as_view(),name = "deposit-data-set")
]
urlpatterns = urlpatterns + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
