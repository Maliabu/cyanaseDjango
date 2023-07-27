from django.shortcuts import render, redirect
from django.shortcuts import render, HttpResponse
from rest_framework.response import Response
from api.v1.users.Users import Users
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError
from django.urls import reverse
from django.contrib import messages
# from .utils import generate_token
# from .models import User
## users
DEFAULT_LANG = 'en'
_user = Users()
 
def index(request):
    return render(request, "index.html", {})

def  VerifyAccount(request, userid):
    if "code" in request.GET:
        code = request.GET["code"]
        return render(request, "verify-account.html", {})
    
@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def get(request, userid, lang=DEFAULT_LANG):
    if not str(userid):
        print("NO USER ID")
        return Response({"message": "Incomplete data request", "success": False}, template_name='verify-account.html')
    if not ("code" in request.GET["code"]):
        # 487092  
        print("NO VERIFICATION CODE")
        return Response({
            'message': "Incomplete data request",
            'success': False
        }, template_name='verify-account.html')
    elif not str(request.GET["code"]):
        print("VERIFICATION CODE MUST BE A STRING")
        return Response({"message": "Verification token is required", "success": False}, template_name='verify-account.html')
    elif _user.isAccounVerifiedByID(request, lang, userid):
        print("ACCOUNT ALREADY VERIFIED")
        return Response({"message": "Account already verified", "success": True}, template_name='verify-account.html')
    elif not _user.isVerificationTokenValid(request, lang, userid, request.GET["code"]):
        print("INVALID VERIFICATION CODE")
        return Response({"message": "Invalid verification code, either your code already expired or it is invalid, please resend verifiction code", "success": False}, template_name='verify-account.html')
    else:
        _user.VerifyAccount(request, lang, userid, request.GET["code"])
        update = _user.updateUserVerificationToken(request, lang, userid)
        if (update):
            data = {"message": "Account verified successfuly", "success": True}
            print("EVERYTHING IS JUUUUUUUST RIGHT")
            return Response(data, template_name='verify-account.html')

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