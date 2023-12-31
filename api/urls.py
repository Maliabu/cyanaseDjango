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
    path('<str:lang>/register/api/user/',
         user_view.CreateApiUser.as_view(), name="register-api-user"),
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
    path('<str:lang>/get/investment/withdraws/',
         views.GetInvestmentWithdraws.as_view(), name="get-investment-withdraws"),
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
    path('<str:lang>/get/user/verification/',
         user_view.IsUserVerified.as_view(), name="get-user-verification"),
    path('<str:lang>/get/verification/',
         views.IsVerified.as_view(), name="get-verification"),
    path('<str:lang>/resend/verification/email/',
         user_view.ResendVerificationEmail.as_view(), name="resend-verification-email"),
    path('<str:lang>/get/risk/analysis/percentages/',
         views.GetRiskAnalysisPercentages.as_view(), name="get-risk-analysis-percentages"),
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
    path('<str:lang>/auth/user/email/',
         user_view.GetAuthUserByEmail.as_view(), name="get-auth-user-by-email"),
    path('<str:lang>/auth/user/riskprofile/',
         views.AddRiskProfile.as_view(), name="add-risk-profile"),
    path('<str:lang>/auth/get/riskprofile/',
         views.GetRiskProfile.as_view(), name="get-risk-profile"),
    path('<str:lang>/auth/user/<int:userid>/',
         user_view.GetAuthUserById.as_view(), name="get-auth-user-by-id"),
    path('<str:lang>/auth/users/all/',
         user_view.GetAllUsers.as_view(), name="get-all-users"),
    path('<str:lang>/auth/user/banks/',
         views.GetCountryBanks.as_view(), name="get-all-banks-by-country"),
    path('<str:lang>/auth/users/emails/all/',
         user_view.GetAllUsersEmails.as_view(), name="get-all-users-emails"),
    path('<str:lang>/auth/user/networth/',
         views.GetGoalNetworth.as_view(), name="get-user-networth"),
    path('<str:lang>/auth/get/investment/options/',
         views.GetInvestmentOption.as_view(), name="get-investment-options"),
    path('<str:lang>/auth/user/networth/data/',
         views.GetUserActualNetworthData.as_view(), name="get-user-networth-data"),
    path('<str:lang>/auth/get/investment/option/',
         views.GetInvestmentOptionByName.as_view(), name="get-investment-option-by-name"),
    path('<str:lang>/auth/get/investment/option/units/',
         views.GetInvestmentOptionById.as_view(), name="get-investment-option-units"),
    path('<str:lang>/auth/user/upload/profile/photo/',
         UploadView.UploadPhoto.as_view(), name="upload-photo"),
    path('<str:lang>/auth/user/account/type/',
         views.AddAccountTypes.as_view(), name="add-account-types"),
    path('<str:lang>/auth/user/update/password/',
         user_view.UpdateAuthUserPassword.as_view(), name="update-user-password"),
    path('<str:lang>/password/reset/',
         user_view.InitPasswordReset.as_view(), name="password-reset"),
     path('<str:lang>/email/verify/<str:userid>/',user_view.verifyAccount.as_view(),name = "email-verify"),
    path('<str:lang>/onboard/', user_view.OnboardAuthUsers.as_view(),name = "onboard-users"),
    path('<str:lang>/auth/user/delete/',user_view.DeleteUserAccount.as_view(),name = "delete-user-account"),
    path('deposit/',views.DepositDataSet.as_view(),name = "deposit-data-set"),
    path('<str:lang>/users/deposits/',views.OnboardAuthUsersDeposits.as_view(),name = "all-user-deposits"),
    path('<str:lang>/users/withdraws/',views.OnboardAuthUsersWithdraws.as_view(),name = "all-user-withdraws")
]
urlpatterns = urlpatterns + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
