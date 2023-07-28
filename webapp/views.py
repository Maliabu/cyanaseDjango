from django.shortcuts import render, redirect
from django.shortcuts import render, HttpResponse
from rest_framework.response import Response
from api.v1.users.Users import Users
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError
from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from api.helper.Cryptor import Cryptor
# from .utils import generate_token
# from .models import User
## users
_cryptor = Cryptor()
DEFAULT_LANG = 'en'
_user = Users()
 
def index(request):
    return render(request, "index.html", {})

# def  VerifyAccount(request, userid):
#     if "code" in request.GET:
#         code = request.GET["code"]
#         return render(request, "verify-account.html", {})
    

def VerifyAccount(request,):
    lang = "en"
    if not "verif" in request.GET or "ref" in request.GET:
        return render(request, 'verify-account.html', {
            'message': "Invalid entry point",
            'success': False
        })
    elif not str(request.GET["verif"]) or not str(request.GET["ref"]):
        return render(request, 'verify-account.html', {"message": "Invalid entry point", "success": False})
    else:
        try:
            code = int(_cryptor.decrypt(request.GET["verif"]))
            userid = int(_cryptor.decrypt(request.GET["ref"]))
            ###################
            if _user.isAccounVerifiedByID(request, lang, userid):
                return render(request, 'verify-account.html', {"message": "Account already verified", "success": True})
            elif not _user.isVerificationTokenValid(request, lang, userid, code):
                return render(request, 'verify-account.html', {"message": "Invalid verification code, either your code already expired or it is invalid, please resend verifiction code", "success": False})
            else:
                _user.VerifyAccount(request, lang, userid, code)
                update = _user.updateUserVerificationToken(request, lang, userid)
                if (update):
                    return render(request, 'verify-account.html', {"message": "Account verified successfuly", "success": True})
        except:
            return render(request, 'verify-account.html', {"message": "Invalid entry point", "success": False})
            
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