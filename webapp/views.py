
from rest_framework.response import Response
from api.v1.users.Users import Users
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import json
from api.config import webconfig
# from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError
from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from api.helper.Cryptor import Cryptor
from urllib.parse import unquote_plus
from django.views.decorators.csrf import csrf_exempt


# from .utils import generate_token
# from .models import User
## users
_cryptor = Cryptor()
DEFAULT_LANG = "en"
_user = Users()


def index(request):
    return render(request, "index.html", {})


# def  VerifyAccount(request, userid):
#     if "code" in request.GET:
#         code = request.GET["code"]
#         return render(request, "verify-account.html", {})


def getParams(request):
    url_string = request.META["QUERY_STRING"]
    params = {}
    url_params = url_string.split("&", 1)
    for url_param in url_params:
        url_param_values = url_param.split("=", 1)
        if len(url_param_values) == 2:
            params[url_param_values[0]] = url_param_values[1]
    return params


def VerifyAccount(request):
    lang = "en"
    if not ("verif" in request.GET) or not ("ref" in request.GET):
        return render(
            request,
            "verify-account.html",
            {"message": "Invalid entry point", "success": False},
        )
    elif not str(request.GET["verif"]) or not str(request.GET["ref"]):
        return render(
            request,
            "verify-account.html",
            {"message": "Invalid entry point", "success": False},
        )
    else:
        # try:
        json_params = getParams(request)
        code = int(_cryptor.decrypt(json_params["verif"]))
        userid = int(_cryptor.decrypt(json_params["ref"]))
        ###################
        if _user.isAccounVerifiedByID(request, lang, userid):
            return render(
                request,
                "verify-account.html",
                {"message": "Account already verified", "success": True},
            )
        elif not _user.isVerificationTokenValid(request, lang, userid, code):
            return render(
                request,
                "verify-account.html",
                {
                    "message": "Invalid verification code, either your code already expired or it is invalid, please resend verifiction code",
                    "success": False,
                },
            )
        else:
            _user.VerifyAccount(request, lang, userid, code)
            _user.updateUserVerificationToken(request, lang, userid)
            return render(
                request,
                "verify-account.html",
                {"message": "Account verified successfuly", "success": True},
            )
    # except:
    #     return render(
    #         request,
    #         "verify-account.html",
    #         {"message": "Invalid entry point", "success": False},
    #     )


@csrf_exempt
def ResetPassword(request):
    print(request.GET)
    lang = "en"
    if not ("email" in request.GET) or not ("password" in request.GET) or not ("ref" in request.GET):
        print("NO DATA IN POST")
        return render(
            request,
            "password-reset.html",
            {"message": "Invalid entry point", "success": False},
        )
    else:
        email = request.GET["email"]
        password = request.GET["password"]
        print(email,password)
        user = _user.getAuthUserByEmailReset(request, lang, email)
        userid = user["user_id"]
        update = _user.UpdateAuthUserPassword(request,lang,password,userid)
        if update:
            return render(
                request,
                "password-reset.html",
                {"message": "Your account password has been reset successfully", "success": True},
            )

# def activate_user(request, uidb64, token):

#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))

#         user = User.objects.get(pk=uid)

#     except Exception as e:
#         user = None

#     if user and generate_token.check_token(user, token):
#         user.is_email_verified = True
#         user.save()

#         messages.add_message(request, messages.SUCCESS,
#                              'Email verified, you can now login')
#         return redirect(reverse('login'))

#     return render(request, 'authentication/activate-failed.html', {"user": user})
