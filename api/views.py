from django.shortcuts import render
# Create your views here.
from django.shortcuts import render, HttpResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .v1.users.Users import Users
from .services import Deposits, Goals, NextOfKins, RiskProfiles
from django.contrib.auth.models import User

# Create your views here.
DEFAULT_LANG = "en"
_user = Users()
_deposit = Deposits()
_goal = Goals()
_nextOfKin = NextOfKins()
_riskprofile = RiskProfiles()

class index(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, format=None):
        return HttpResponse("<h2>Invalid Entry point </h2>")


class GetUserView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)

class CreateUserAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class MakeDeposit(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        lang = DEFAULT_LANG if lang == None else lang
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        deposit_amount = request.data["deposit_amount"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        user = _user.getAuthUser(request, lang)
        ##########################
        if not payment_means:
            return Response({
                'message': "This field is required",
                "type": "payment_means",
                'success': False
            }, status=400)
        elif not account_type:
            return Response({
                'message': "This field is required",
                "type": "account_type",
                'success': False
            })
        elif not deposit_category:
            return Response({
                'message': "This field is required",
                "type": "deposit_category",
                'success': False
            })
        elif not deposit_amount:
            return Response({
                'message': "This field is required",
                "type": "deposit_amount",
                'success': False
            })
        elif not currency:
            return Response({
                'message': "This field is required",
                "type": "currency",
                'success': False
            }, status=400)
        else:
            deposit = _deposit.createDeposit(request, lang, user)
            return Response(deposit)


class MakeDepositToGoal(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang,*args, **kwargs):
        lang = DEFAULT_LANG if lang == None else lang
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        deposit_amount = request.data["deposit_amount"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        goalid = request.data["goal_id"]
        user = _user.getAuthUser(request, lang)
        ##########################
        if not payment_means:
            return Response({
                'message': "This field is required",
                "type": "payment_means",
                'success': False
            }, status=400)
        elif not account_type:
            return Response({
                'message': "This field is required",
                "type": "account_type",
                'success': False
            })
        elif not deposit_category:
            return Response({
                'message': "This field is required",
                "type": "deposit_category",
                'success': False
            })
        elif not deposit_amount:
            return Response({
                'message': "This field is required",
                "type": "deposit_amount",
                'success': False
            })
        elif not currency:
            return Response({
                'message': "This field is required",
                "type": "currency",
                'success': False
            }, status=400)
        else:
            deposit = _deposit.depositToGoal(request, lang, user,goalid)
            return Response(deposit)

class GetDepositsByAuthUser(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self,request,lang):
        userid = request.user.id
        user = _user.getAuthUserById(request, lang, userid)
        lang = DEFAULT_LANG if lang == None else lang
        deposit = _deposit.getAllDeposits(request,lang,user)
        return Response(deposit)

class GetDepositsById(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self,request,lang,depositid=34):
        lang = DEFAULT_LANG if lang == None else lang
        deposit = _deposit.getDeopsitById(request,lang,depositid)
        return Response(deposit)

class GetDepositsByGoalId(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self,request,lang,goalid=16):
        lang = DEFAULT_LANG if lang == None else lang
        deposit = _deposit.getDeopsitByGoalId(request,lang,goalid)
        return Response(deposit)

class GetGoalById(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self,request,lang,goalid):
        lang = DEFAULT_LANG if lang == None else lang
        goal = _goal.getGoalById(request,lang,goalid)
        return Response(goal)
    
    
class CreateGoal(APIView):
    authentication_classes = [SessionAuthentication,TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']
    
    def post(self, request, lang, *args, **kwargs):
        user = _user.getAuthUser(request,lang)
        lang = DEFAULT_LANG if lang == None else lang
        goal_name = request.data["goal_name"]
        goal_period = request.data["goal_period"]
        goal_amount = request.data["goal_period"]
        deposit_type = request.data["deposit_type"]
        deposit_reminder_day = request.data["deposit_reminder_day"]
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        deposit_amount = request.data["deposit_amount"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        if not goal_name:
            return{
                "message": "This field is required",
                "success": False,
                "type": "goal name"
            }
        elif not goal_period:
            return{
                "message": "This field is required",
                "success": False,
                "type": "goal period"
            }
        elif not goal_amount:
            return{
                "message": "This field is required",
                "success": False,
                "type": "goal amount"
            }
        elif not deposit_type:
            return{
                "message": "This field is required",
                "success": False,
                "type": "deposit type"
            }
        elif not payment_means:
            return Response({
                'message': "This field is required",
                "type": "payment_means",
                'success': False
            }, status=400)
        elif not account_type:
            return Response({
                'message': "This field is required",
                "type": "account_type",
                'success': False
            })
        elif not deposit_category:
            return Response({
                'message': "This field is required",
                "type": "deposit_category",
                'success': False
            })
        elif not deposit_amount:
            return Response({
                'message': "This field is required",
                "type": "deposit_amount",
                'success': False
            })
        elif not currency:
            return Response({
                'message': "This field is required",
                "type": "currency",
                'success': False
            })
        else:
            goal = _goal.createGoal(request, lang,user)
            goalid = goal["goalid"]
            deposit = _deposit.depositToGoal(request,lang,user,goalid)
            return Response(goal)
        
class GetGoalsByAuthUser(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self,request,lang):
        userid = request.user.id
        user = _user.getAuthUserById(request, lang, userid)
        lang = DEFAULT_LANG if lang == None else lang
        goal = _goal.getAllUserGoals(request,lang,user)
        return Response(goal)
    
class AddNextOfKin(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']
    
    def post(self,request,lang,*args, **kwargs):
        user = _user.getAuthUser(request,lang)
        lang = DEFAULT_LANG if lang == None else lang
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        email = request.data["email"]
        phone = request.data["phone"]
        
        if not first_name:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not last_name:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not email:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not phone:
            return{
                "message": "This field is required",
                "success": False
            }
        else:
            nextOfKin = _nextOfKin.addNextOfKin(request,lang,user)
            return Response(nextOfKin)
        
class GetNextOfKinById(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self,request,lang,nextOfKinId):
        lang = DEFAULT_LANG if lang == None else lang
        nextOfKin = _nextOfKin.getNextOfKinById(request,lang,nextOfKinId)
        return Response(nextOfKin)

class GetNextOfKin(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self,request,lang):
        lang = DEFAULT_LANG if lang == None else lang
        user = _user.getAuthUser(request,lang)
        nextOfKin = _nextOfKin.getNextOfKin(request,lang,user)
        return Response(nextOfKin)
    

class AddRiskProfile(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']
    
    def post(self,request,lang,*args, **kwargs):
        user = _user.getAuthUser(request,lang)
        lang = DEFAULT_LANG if lang == None else lang
        qn1 = request.data["qn1"]
        qn2 = request.data["qn2"]
        qn3 = request.data["qn3"]
        qn4 = request.data["qn4"]
        qn5 = request.data["qn5"]
        qn6 = request.data["qn6"]
        qn7 = request.data["qn7"]
        qn8 = request.data["qn8"]
        qn9 = request.data["qn9"]
        qn10 = request.data["qn10"]
        qn11 = request.data["qn11"]
        score = request.data["score"]
        investment_option = request.data["investment_option"]
        risk_analysis = request.data["risk_analysis"]
        if not qn1:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not qn2:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not qn3:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not qn4:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not qn5:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not qn6:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not qn7:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not qn8:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not qn9:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not qn10:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not qn11:
            return{
                "message": "This field is required",
                "success": False
            }
        elif not risk_analysis:
            return{
                "message": "This field is required",
                "success": False
            }
        else:
            riskprofile = _riskprofile.addRiskProfile(request,lang,user)
            return Response(riskprofile)
        
class GetRiskProfile(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self,request,lang):
        lang = DEFAULT_LANG if lang == None else lang
        user = _user.getAuthUser(request,lang)
        riskprofile = _riskprofile.getRiskProfile(request,lang,user)
        return Response(riskprofile)