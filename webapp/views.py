from django.shortcuts import render
# Create your views here.
from django.shortcuts import render, HttpResponse
from rest_framework.response import Response
from api.v1.users.Users import Users
## users
_user = Users()
# Create your views here.
def index(request):
    return render(request, "index.html", {})

def  VerifyAccount(request, userid):
    if "code" in request.GET["code"]:
        code = request.GET["code"]
    return render(request, "verify-account.html", {})
 
def get(self, request, lang, userid):
    if not str(userid):
        return Response({"message": "Incomplete data request", "success": False}, status=400)
    if not ("code" in request.GET):
        return Response({
            'message': "Incomplete data request",
            'success': False
        }, status=400)
    elif not str(request.GET["code"]):
        return Response({"message": "Verification token is required", "success": False}, status=400)
    elif _user.isAccounVerifiedByID(request, lang, userid):
        return Response({"message": "Account already verified", "success": True}, status=200)
    elif not _user.isVerificationTokenValid(request, lang, userid, request.GET["code"]):
        return Response({"message": "Invalid verification code, either your code already expired or it is invalid, please resend verifiction code", "success": False}, status=400)
    else:
        _user.VerifyAccount(request, lang, userid, request.GET["code"])
        _user.updateUserVerificationToken(request, lang, userid)
        return Response({"message": "Account verified successfuly", "success": True}, status=200)
    return render(request, "verify-account.html", {})
