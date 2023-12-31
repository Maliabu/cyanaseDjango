from django.shortcuts import HttpResponse
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .v1.users.Users import Users
from .services import Deposits, Goals, NextOfKins, RiskProfiles, Withdraws, Networths, BankTransactions, Subscriptions, TransactionRef, AccountTypes, InvestmentOptions
from django.contrib.auth.models import User
from rave_python import Rave, RaveExceptions,Misc
import os
import datetime
from cyanase_api import settings
# from forex_python.converter import CurrencyRates

# Create your views here.

DEFAULT_LANG = "en"
DEPOSIT_PUB_KEY = settings.DEPOSIT_PUB_KEY
DEPOSIT_SEC_KEY = settings.DEPOSIT_SEC_KEY
SUB_PUB_KEY = settings.SUB_PUB_KEY
SUB_SEC_KEY = settings.SUB_SEC_KEY

_user = Users()
_deposit = Deposits()
_withdraw = Withdraws()
_goal = Goals()
_nextOfKin = NextOfKins()
_riskprofile = RiskProfiles()
_networth = Networths()
_transaction = BankTransactions()
_subscription = Subscriptions()
_refs = TransactionRef()
_accountType = AccountTypes()
_investmentOption = InvestmentOptions()


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


class AddAccountTypes(ObtainAuthToken):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        lang = DEFAULT_LANG if lang is None else lang
        type_name = request.data["type_name"]
        code_name = request.data["code_name"]
        description = request.data["description"]
        sort_value = request.data["sort_value"]
        is_default = request.data["is_default"]
        ##########################
        if not type_name:
            return Response({
                'message': "This field is required",
                "type": "type_name",
                'success': False
            })
        elif not code_name:
            return Response({
                'message': "This field is required",
                "type": "code_name",
                'success': False
            })
        elif not description:
            return Response({
                'message': "This field is required",
                "type": "description",
                'success': False
            })
        elif not sort_value:
            return Response({
                'message': "This field is required",
                "type": "sort_value",
                'success': False
            })
        elif not is_default:
            return Response({
                'message': "This field is required",
                "type": "is_default",
                'success': False
            })
        else:
            account_type = _accountType.createAccountTypes(request, lang)
            if account_type["success"] is True:
                return Response({
                    "message": "Account Types added successfully",
                    "success": True
                })
            else:
                return Response({
                    "message": "Account Types not added",
                    "success": False
                })


class MakeDeposit(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        lang = DEFAULT_LANG if lang is None else lang
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        deposit_amount = request.data["deposit_amount"]
        currency = request.data["currency"]
        investment_id = request.data["investment_id"]
        investment_option = request.data["investment_option"]
        account_type = request.data["account_type"]
        reference = request.data["reference"]
        reference_id = request.data["reference_id"]
        user = _user.getAuthUser(request, lang)
        userid = user["user_id"]
        ##########################
        if not payment_means:
            return Response({
                'message': "This field is required",
                "type": "payment_means",
                'success': False
            })
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
        elif not investment_option:
            return Response({
                'message': "This field is required",
                "type": "investment_option",
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
        elif not reference:
            return Response({
                'message': "This field is required",
                "type": "reference",
                'success': False
            })
        elif not reference_id:
            return Response({
                'message': "This field is required",
                "type": "reference_id",
                'success': False
            })
        elif not investment_id:
            return Response({
                'message': "This field is required",
                "type": "investment_id",
                'success': False
            })
        else:
            # providers = _deposit.getLinkingProviders
            # print(providers)
            transaction_id = str(reference_id)
            verified = _deposit.verifyTransaction(transaction_id)
            # error or success - status returned (flutterwave)
            if verified == "success":
                txRef = _refs.getTxRef()
                tx_ref = _deposit.getTxRefById(request, lang, user, txRef)
                if tx_ref["success"] is False:
                    if int(investment_id) != 0:
                        # get units
                        units = _investmentOption.getInvestmentOptionById(request, lang, userid, investment_id, deposit_amount)
                        deposit = _deposit.createDeposit(request, lang, txRef, units, investment_id, deposit_amount)
                        return Response(deposit)
                    else:
                        # get percentages from analysis --- Risk profile
                        analysis = _riskprofile.getInvestmentByRiskProfile(request, lang)
                        for any_analysis in analysis:
                            # create a deposit rotating each in list
                            # get new deposit amount
                            new_deposit_amount = float(any_analysis["percentage"])/100 * int(deposit_amount)
                            new_investment_id = any_analysis["id"]
                            units = _investmentOption.getInvestmentOptionById(request, lang, userid, new_investment_id, new_deposit_amount)
                            deposit = _deposit.createDeposit(request, lang, txRef, units, new_investment_id, new_deposit_amount)
                        return Response({
                            "message": "Deposits made successfully",
                            "success": True,
                            "type": "Automatic deposits made successfully"
                        })
                else:
                    return Response({
                        'message': "Something went wrong",
                        'success': False,
                        "type": "reference found/missing"
                    })
            else:
                return Response({
                    'message': "Unathorised",
                    'success': False,
                    "type": "Transaction"
                })


class MakeDepositToBank(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        lang = DEFAULT_LANG if lang is None else lang
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        deposit_amount = request.data["deposit_amount"]
        currency = request.data["currency"]
        investment_option = request.data["investment_option"]
        account_type = request.data["account_type"]
        cardno = request.data["cardno"]
        cvv = request.data["cvv"]
        expirymonth = request.data["expirymonth"]
        expiryyear = request.data["expiryyear"]
        user = _user.getAuthUser(request, lang)
        ##########################
        if not payment_means:
            return Response({
                'message': "This field is required",
                "type": "payment_means",
                'success': False
            })
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
        elif not investment_option:
            return Response({
                'message': "This field is required",
                "type": "investment_option",
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
        elif not cardno:
            return Response({
                'message': "This field is required",
                "type": "cardno",
                'success': False
            })
        elif not cvv:
            return Response({
                'message': "This field is required",
                "type": "cvv",
                'success': False
            })
        elif not expirymonth:
            return Response({
                'message': "This field is required",
                "type": "expiry month",
                'success': False
            })
        elif not expiryyear:
            return Response({
                'message': "This field is required",
                "type": "expiry year",
                'success': False
            })
        else:
            transactions = []
            rave = Rave(DEPOSIT_PUB_KEY, DEPOSIT_SEC_KEY, usingEnv=False)
            payload = {
                "cardno": cardno,
                "cvv": cvv,
                "expirymonth": expirymonth,
                "expiryyear": expiryyear,
                "amount": deposit_amount,
                "email": user["email"],
                "phonenumber": user["profile"]["phoneno"],
                "firstname": user["first_name"],
                "lastname": user["last_name"],
                "tx_ref": "MC-3243e",
                "IP": "355426087298442",
            }
            try:
                res = rave.Card.charge(payload)

                if res["suggestedAuth"]:
                    arg = Misc.getTypeOfArgsRequired(res["suggestedAuth"])

                    if arg == "pin":
                        Misc.updatePayload(res["suggestedAuth"], payload, pin="3310")
                    if arg == "address":
                        Misc.updatePayload(res["suggestedAuth"], payload, address= {"billingzip": "07205", "billingcity": "Hillside", "billingaddress": "470 Mundet PI", "billingstate": "NJ", "billingcountry": "US"})
       
                res = rave.Card.charge(payload)

                if res["validationRequired"]:
                    rave.Card.validate(res["flwRef"], "12345")

                transactions.append(res)
                res = rave.Card.verify(res["txRef"])
                print(res["transactionComplete"])

            except RaveExceptions.CardChargeError as e:
                print(e.err["errMsg"])
                print(e.err["flwRef"])

            except RaveExceptions.TransactionValidationError as e:
                print(e.err)
                print(e.err["flwRef"])

            except RaveExceptions.TransactionVerificationError as e:
                print(e.err["errMsg"])
                print(e.err["txRef"])
            # reference = transactions[0]["flwRef"]
            # txRef = transactions[0]["txRef"]
            # reference_id = payload["tx_ref"]
            # deposit = _deposit.createDeposit(request, lang, user,reference,reference_id,txRef)
            return Response(transactions)


class MakeDepositToGoal(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        lang = DEFAULT_LANG if lang is None else lang
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        deposit_amount = request.data["deposit_amount"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        reference = request.data["reference"]
        reference_id = request.data["reference_id"]
        txRef = request.data["tx_ref"]
        goalid = request.data["goal_id"]
        user = _user.getAuthUser(request, lang)
        userid = user["user_id"]
        ##########################
        if not payment_means:
            return Response({
                'message': "This field is required",
                "type": "payment_means",
                'success': False
            })
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
        elif not reference:
            return Response({
                'message': "This field is required",
                "type": "reference",
                'success': False
            })
        elif not reference_id:
            return Response({
                'message': "This field is required",
                "type": "reference_id",
                'success': False
            })
        elif not txRef:
            return Response({
                'message': "This field is required",
                "type": "txRef",
                'success': False
            })
        else:
            transaction_id = str(reference_id)
            verified = _deposit.verifyTransaction(transaction_id)
            if verified == "success":
                txRef = _refs.getTxRef()
                tx_ref = _deposit.getTxRefById(request, lang, user, txRef)
                if tx_ref["success"] is False:
                    # get percentages from analysis
                    analysis = _riskprofile.getInvestmentByRiskProfile(request, lang)
                    for any_analysis in analysis:
                        # create a deposit rotating each in list
                        # get new deposit amount
                        new_deposit_amount = float(any_analysis["percentage"])/100 * int(deposit_amount)
                        new_investment_id = any_analysis["id"]
                        units = _investmentOption.getInvestmentOptionById(request, lang, userid, new_investment_id, new_deposit_amount)
                        deposit = _deposit.depositToGoal(request, lang, goalid, txRef, units, new_investment_id, new_deposit_amount)
                    return Response({
                        "message": "Deposits made successfully",
                        "success": True,
                        "type": "Automatic deposits made successfully"
                    })
                else:
                    return Response({
                        'message': "Something went wrong",
                        'success': False,
                        "type": "reference found/missing"
                    })
            else:
                return Response({
                    'message': "Unathorised",
                    'success': False,
                    "type": "Transaction"
                })


class GetDepositsByAuthUser(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        userid = request.user.id
        user = _user.getAuthUserById(request, lang, userid)
        lang = DEFAULT_LANG if lang is None else lang
        deposit = _deposit.getAllDeposits(request, lang)
        return Response(deposit)


class GetDepositsById(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang, depositid=34):
        lang = DEFAULT_LANG if lang is None else lang
        deposit = _deposit.getDeopsitById(request, lang, depositid)
        return Response(deposit)


class GetDepositsByGoalId(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang, goalid=16):
        lang = DEFAULT_LANG if lang is None else lang
        deposit = _deposit.getDeopsitByGoalId(request, lang, goalid)
        return Response(deposit)


class GetGoalById(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang, goalid):
        lang = DEFAULT_LANG if lang is None else lang
        goal = _goal.getGoalById(request, lang, goalid)
        return Response(goal)


class CreateGoal(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        user = _user.getAuthUser(request, lang)
        lang = DEFAULT_LANG if lang is None else lang
        goal_name = request.data["goal_name"]
        goal_period = request.data["goal_period"]
        goal_amount = request.data["goal_period"]
        deposit_type = request.data["deposit_type"]
        # deposit_reminder_day = request.data["deposit_reminder_day"]
        # payment_means = request.data["payment_means"]
        # deposit_category = request.data["deposit_category"]
        # deposit_amount = request.data["deposit_amount"]
        # currency = request.data["currency"]
        # account_type = request.data["account_type"]
        # reference = request.data["reference"]
        # reference_id = request.data["reference_id"]
        # txRef = request.data["tx_ref"]
        if not goal_name:
            return Response({
                "message": "This field is required",
                "success": False,
                "type": "goal name"
            })
        elif not goal_period:
            return Response({
                "message": "This field is required",
                "success": False,
                "type": "goal period"
            })
        elif not goal_amount:
            return Response({
                "message": "This field is required",
                "success": False,
                "type": "goal amount"
            })
        elif not deposit_type:
            return Response({
                "message": "This field is required",
                "success": False,
                "type": "deposit type"
            })
        # elif not payment_means:
        #     return Response({
        #         'message': "This field is required",
        #         "type": "payment_means",
        #         'success': False
        #     })
        # elif not account_type:
        #     return Response({
        #         'message': "This field is required",
        #         "type": "account_type",
        #         'success': False
        #     })
        # elif not deposit_category:
        #     return Response({
        #         'message': "This field is required",
        #         "type": "deposit_category",
        #         'success': False
        #     })
        # elif not deposit_amount:
        #     return Response({
        #         'message': "This field is required",
        #         "type": "deposit_amount",
        #         'success': False
        #     })
        # elif not currency:
        #     return Response({
        #         'message': "This field is required",
        #         "type": "currency",
        #         'success': False
        #     })
        # elif not reference:
        #     return Response({
        #         'message': "This field is required",
        #         "type": "reference",
        #         'success': False
        #     })
        # elif not reference_id:
        #     return Response({
        #         'message': "This field is required",
        #         "type": "reference_id",
        #         'success': False
        #     })
        # elif not txRef:
        #     return Response({
        #         'message': "This field is required",
        #         "type": "txRef",
        #         'success': False
        #     })
        else:
            goal = _goal.createGoal(request, lang, user)
            # goalid = goal["goalid"]
            if goal["success"] is True:
                return Response({
                    "message": "Goal created successfully",
                    "success": True
                })
            else:
                return Response({
                    "message": "Goal not created, account is not verified",
                    "success": False
                })
            # transaction_id = str(reference_id)
            # verified = _deposit.verifyTransaction(transaction_id)
            # if verified == "success":
            #     txRef = _refs.getTxRef()
            #     tx_ref = _deposit.getTxRefById(request, lang, user, txRef)
            #     if tx_ref["success"] is False:
            #         deposit = _deposit.depositToGoal(request, lang, user, goalid, txRef)
            #         return Response(goal)
            #     if tx_ref["success"] is True:
            #         return Response({
            #             'message': "Something went wrong. Goal not created",
            #             'success': False
            #         })
            # else:
            #     return Response({
            #             'message': "Something went wrong. Goal not created",
            #             'success': False
            #         })


class GetGoalsByAuthUser(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        userid = request.user.id
        user = _user.getAuthUserById(request, lang, userid)
        lang = DEFAULT_LANG if lang is None else lang
        goal = _goal.getAllUserGoals(request, lang)
        return Response(goal)


class AddNextOfKin(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        user = _user.getAuthUser(request, lang)
        lang = DEFAULT_LANG if lang is None else lang
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        email = request.data["email"]
        phone = request.data["phone"]
        if not first_name:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not last_name:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not email:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not phone:
            return {
                "message": "This field is required",
                "success": False
            }
        else:
            nextOfKin = _nextOfKin.addNextOfKin(request, lang, user)
            return Response(nextOfKin)


class GetNextOfKinById(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang, nextOfKinId):
        lang = DEFAULT_LANG if lang is None else lang
        nextOfKin = _nextOfKin.getNextOfKinById(request, lang, nextOfKinId)
        return Response(nextOfKin)


class GetNextOfKin(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        lang = DEFAULT_LANG if lang is None else lang
        user = _user.getAuthUser(request, lang)
        nextOfKin = _nextOfKin.getNextOfKin(request, lang, user)
        return Response(nextOfKin)


class AddRiskProfile(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        user = _user.getAuthUser(request, lang)
        lang = DEFAULT_LANG if lang is None else lang
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
        risk_analysis = request.data["risk_analysis"]
        if not qn1:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not qn2:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not qn3:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not qn4:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not qn5:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not qn6:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not qn7:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not qn8:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not qn9:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not qn10:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not qn11:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not risk_analysis:
            return {
                "message": "This field is required",
                "success": False
            }
        elif not score:
            return {
                "message": "This field is required",
                "success": False
            }
        else:
            riskprofile = _riskprofile.addRiskProfile(request, lang, user)
            return Response(riskprofile)


class GetRiskProfile(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        lang = DEFAULT_LANG if lang is None else lang
        user = _user.getAuthUser(request, lang)
        riskprofile = _riskprofile.getRiskProfile(request, lang, user)
        return Response(riskprofile)


class GetRiskAnalysisPercentages(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        lang = DEFAULT_LANG if lang is None else lang
        risk_analysis_percentages = _riskprofile.getInvestmentByRiskProfile(request, lang)
        return Response(risk_analysis_percentages)


class GetCountryBanks(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        lang = DEFAULT_LANG if lang is None else lang
        userid = request.user.id
        user = _user.getAuthUserById(request, lang, userid)
        code = user["profile"]["country"]
        banks = _withdraw.getAllCountryBanks(code)
        return Response(banks)


class MakeWithdrawFromBank(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        user = _user.getAuthUser(request, lang)
        userid = user["user_id"]
        lang = DEFAULT_LANG if lang is None else lang
        withdraw_channel = request.data["withdraw_channel"]
        withdraw_amount = request.data["withdraw_amount"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        account_bank = request.data["account_bank"]
        account_number = request.data["account_number"]
        narration = "Withdraw"
        investment_option_id = request.data["investment_id"]
        beneficiary_name = user["last_name"]+" "+user["first_name"]
        is_verified = request.user.userprofile.is_verified
        is_subscribed = _subscription.getSubscriptionStatus(request, lang, userid)
        if not withdraw_channel:
            return {
                "message": "This field is required",
                "success": False,
                "type": "withdraw channel"
            }
        elif not account_type:
            return Response({
                'message': "This field is required",
                "type": "account_type",
                'success': False
            })
        elif not withdraw_amount:
            return {
                "message": "This field is required",
                "success": False,
                "type": "withdraw amount"
            }
        elif not currency:
            return Response({
                'message': "This field is required",
                "type": "currency",
                'success': False
            })
        elif not account_bank:
            return Response({
                'message': "This field is required",
                "type": "account bank",
                'success': False
            })
        elif not account_number:
            return Response({
                'message': "This field is required",
                "type": "account number",
                'success': False
            })
        elif not beneficiary_name:
            return Response({
                'message': "This field is required",
                "type": "beneficiary name",
                'success': False
            })
        else:
            # if verified user
            if is_verified is True:
                # if subscribed
                if is_subscribed["status"] == "subscribed":
                    # get units
                    units = _investmentOption.getWithdrawInvestmentOptionById(request, lang, userid, investment_option_id, withdraw_amount)
                    print("UNITS ACCUMULATED: ", units)
                    _type = ""
                    if withdraw_channel == "bank":
                        _type = "account"
                    if withdraw_channel == "mobile money":
                        _type = "mobilemoney"
                    getWithdrawFee = _withdraw.getWithdrawfee(request, lang, userid, withdraw_amount, currency, _type)
                    total_withdraw = float(withdraw_amount) - float(getWithdrawFee)
                    transactions = []
                    tErrors = []
                    try:
                        rave = Rave(DEPOSIT_PUB_KEY, DEPOSIT_SEC_KEY, usingEnv=False)

                        res = rave.Transfer.initiate({
                            "account_bank": account_bank,
                            "account_number": account_number,
                            "amount": total_withdraw,
                            "narration": narration,
                            "currency": currency,
                            "beneficiary_name": beneficiary_name
                        })
                        transactions.append(res)
                    except RaveExceptions.IncompletePaymentDetailsError as e:
                        tErrors.append(e)
                    except RaveExceptions.InitiateTransferError as e:
                        tErrors.append(e)
                    except RaveExceptions.TransferFetchError as e:
                        tErrors.append(e)
                    except RaveExceptions.ServerError as e:
                        tErrors.append(e)
                    # if all is well
                    if transactions[0]["error"] is False:
                        transaction = _transaction.createTransfer(request, lang, transactions)
                        transactionid = transaction["transaction_id"]
                        withdraw = _withdraw.withdraw(request, lang, user, transactionid, investment_option_id, units)
                        return Response(withdraw)
                    else:
                        return Response({
                            "message": transactions[0]["errMsg"],
                            "success": False,
                            "type": "withdraw amount"
                        })
                else:
                    # not subscribed
                    substatus = is_subscribed["status"]
                    return Response({
                        "message": "your account subscription is "+substatus+", withdraw may not proceed till you subscribe",
                        "success": False
                    })
            else:
                # not verified user
                return Response({
                    "message": "your account is not verified, please check your email and verify",
                    "success": False
                })


class MakeGoalWithdrawFromBank(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        user = _user.getAuthUser(request, lang)
        userid = user["user_id"]
        lang = DEFAULT_LANG if lang is None else lang
        withdraw_channel = request.data["withdraw_channel"]
        withdraw_amount = request.data["withdraw_amount"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        account_bank = request.data["account_bank"]
        account_number = request.data["account_number"]
        goalid = request.data["goalid"]
        narration = "Withdraw"
        beneficiary_name = user["last_name"]+" "+user["first_name"]
        is_verified = request.user.userprofile.is_verified
        is_subscribed = _subscription.getSubscriptionStatus(request, lang, userid)
        if not withdraw_channel:
            return {
                "message": "This field is required",
                "success": False,
                "type": "withdraw channel"
            }
        elif not account_type:
            return Response({
                'message': "This field is required",
                "type": "account_type",
                'success': False
            })
        elif not withdraw_amount:
            return {
                "message": "This field is required",
                "success": False,
                "type": "withdraw amount"
            }
        elif not currency:
            return Response({
                'message': "This field is required",
                "type": "currency",
                'success': False
            })
        elif not account_bank:
            return Response({
                'message': "This field is required",
                "type": "account bank",
                'success': False
            })
        elif not account_number:
            return Response({
                'message': "This field is required",
                "type": "account number",
                'success': False
            })
        elif not beneficiary_name:
            return Response({
                'message': "This field is required",
                "type": "beneficiary name",
                'success': False
            })
        elif not goalid:
            return Response({
                'message': "This field is required",
                "type": "goalid",
                'success': False
            })
        else:
            if is_verified is True:
                if is_subscribed["status"] == "subscribed":
                    # check goal status
                    goal_status = _goal.getGoalById(request, lang, goalid)
                    if goal_status["is_active"] is False:
                        _type = ""
                        if withdraw_channel == "bank":
                            _type = "account"
                        if withdraw_channel == "mobile money":
                            _type = "mobilemoney"
                        getWithdrawFee = _withdraw.getWithdrawfee(request, lang, userid, withdraw_amount, currency, _type)
                        total_withdraw = float(withdraw_amount) - float(getWithdrawFee)
                        transactions = []
                        try:
                            rave = Rave(DEPOSIT_PUB_KEY, DEPOSIT_SEC_KEY, usingEnv=False)

                            res = rave.Transfer.initiate({
                                "account_bank": account_bank,
                                "account_number": account_number,
                                "amount": total_withdraw,
                                "narration": narration,
                                "currency": currency,
                                "beneficiary_name": beneficiary_name
                            })
                            transactions.append(res)

                        except RaveExceptions.IncompletePaymentDetailsError as e:
                            print(e)

                        except RaveExceptions.InitiateTransferError as e:
                            print(e.err)

                        except RaveExceptions.TransferFetchError as e:
                            print(e.err)

                        except RaveExceptions.ServerError as e:
                            print(e.err)
                        if transactions[0]["error"] is False:
                            transaction = _transaction.createTransfer(request,lang,transactions)
                            transactionid = transaction["transaction_id"]
                            withdraw = _withdraw.withdrawFromGoal(request,lang,goalid,user,transactionid)
                            return Response(withdraw)
                    elif goal_status["is_active"] == True:
                        return Response({
                            "message": "This goal is done.",
                            "success": False
                        })
                else:
                    substatus = is_subscribed["status"]
                    time_left = is_subscribed["days_passed"]
                    print(substatus)
                    print(time_left)
                    return Response({
                        "message": "your account subscription is "+substatus+", withdraw may not proceed till you subscribe",
                        "success": False
                    })
            else:
                return Response({
                    "message": "your account is not verified, please check your email and verify",
                    "success": False
                })


class GetWithdrawFee(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        userid = request.user.id
        withdraw_amount = request.data["withdraw_amount"]
        currency = request.data["currency"]
        _type = request.data["type"]
        if not currency:
            return {
                "message": "This field is required",
                "success": False,
                "type": "currency"
            }
        elif not _type:
            return Response({
                'message': "This field is required",
                "type": "type",
                'success': False
            })
        elif not withdraw_amount:
            return {
                "message": "This field is required",
                "success": False,
                "type": "withdraw amount"
            }
        else:
            withdraw_fee = _withdraw.getWithdrawfee(request, lang, userid, withdraw_amount, currency, _type)
            return Response(withdraw_fee)


class MakeWithdrawFromMobileMoney(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        user = _user.getAuthUser(request, lang)
        userid = user["user_id"]
        lang = DEFAULT_LANG if lang is None else lang
        withdraw_channel = request.data["withdraw_channel"]
        withdraw_amount = request.data["withdraw_amount"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        account_bank = request.data["account_bank"]
        phone_number = request.data["phone_number"]
        beneficiary_name = user["last_name"]+" "+user["first_name"]
        investment_option_id = request.data["investment_id"]
        is_verified = request.user.userprofile.is_verified
        is_subscribed = _subscription.getSubscriptionStatus(request, lang, userid)
        if not withdraw_channel:
            return {
                "message": "This field is required",
                "success": False,
                "type": "withdraw channel"
            }
        elif not withdraw_amount:
            return {
                "message": "This field is required",
                "success": False,
                "type": "withdraw amount"
            }
        elif not account_type:
            return Response({
                'message': "This field is required",
                "type": "account_type",
                'success': False
            })
        elif not currency:
            return Response({
                'message': "This is required",
                "type": "currency",
                'success': False
            })
        elif not account_bank:
            return Response({
                'message': "This field is required",
                "type": "account bank",
                'success': False
            })
        elif not phone_number:
            return Response({
                'message': "This field is required",
                "type": "account number",
                'success': False
            })
        elif not beneficiary_name:
            return Response({
                'message': "This field is required",
                "type": "beneficiary name",
                'success': False
            })
        else:
            # if verified user
            if is_verified is True:
                # if subscribed
                if is_subscribed["status"] == "subscribed":
                    # get units
                    units = _investmentOption.getWithdrawInvestmentOptionById(request, lang, userid, investment_option_id, withdraw_amount)
                    _type = ""
                    if withdraw_channel == "bank":
                        _type = "account"
                    if withdraw_channel == "mobile money":
                        _type = "mobilemoney"
                    getWithdrawFee = _withdraw.getWithdrawfee(request, lang, userid, withdraw_amount, currency, _type)
                    total_withdraw = float(withdraw_amount) - float(getWithdrawFee)
                    transactions = []
                    rave = Rave(DEPOSIT_PUB_KEY, DEPOSIT_SEC_KEY, usingEnv=False)

                    details = {
                            "account_bank": account_bank,
                            "account_number": phone_number,
                            "amount": total_withdraw,
                            "currency": currency,
                            "beneficiary_name": beneficiary_name,
                            "meta": {
                                "sender": "Flutterwave Developers",
                                "sender_country": "ZA",
                                "mobile_number": "23457558595"
                                }
                            }
                    res = rave.Transfer.initiate(details)
                    transactions.append(res)
                    if transactions[0]["error"] is False:
                        transaction = _transaction.createTransfer(request, lang, transactions)
                        transactionid = transaction["transaction_id"]
                        withdraw = _withdraw.withdraw(request, lang, user, transactionid, investment_option_id, units)
                        return Response(withdraw)
                else:
                    return Response({
                        "message": "your account subscription is overdue, withdraw may not proceed till you subscribe",
                        "success": False,
                        "type": "subscription"
                    })
            else:
                return Response({
                    "message": "your account is not verified, please check your email and verify",
                    "success": False,
                    "type": "verification"
                })


class MakeGoalWithdrawFromMobileMoney(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        user = _user.getAuthUser(request, lang)
        userid = user["user_id"]
        lang = DEFAULT_LANG if lang is None else lang
        withdraw_channel = request.data["withdraw_channel"]
        withdraw_amount = request.data["withdraw_amount"]
        currency = request.data["currency"]
        goalid = request.data["goalid"]
        account_type = request.data["account_type"]
        account_bank = request.data["account_bank"]
        account_number = request.data["account_number"]
        beneficiary_name = user["last_name"]+" "+user["first_name"]
        is_verified = request.user.userprofile.is_verified
        is_subscribed = _subscription.getSubscriptionStatus(request, lang, userid)
        if not withdraw_channel:
            return {
                "message": "This field is required",
                "success": False,
                "type": "withdraw channel"
            }
        elif not withdraw_amount:
            return {
                "message": "This field is required",
                "success": False,
                "type": "withdraw amount"
            }
        elif not account_type:
            return Response({
                'message': "This field is required",
                "type": "account_type",
                'success': False
            })
        elif not currency:
            return Response({
                'message': "This is required",
                "type": "currency",
                'success': False
            })
        elif not account_bank:
            return Response({
                'message': "This field is required",
                "type": "account bank",
                'success': False
            })
        elif not account_number:
            return Response({
                'message': "This field is required",
                "type": "account number",
                'success': False
            })
        elif not beneficiary_name:
            return Response({
                'message': "This field is required",
                "type": "beneficiary name",
                'success': False
            })
        elif not goalid:
            return Response({
                'message': "This field is required",
                "type": "goalid",
                'success': False
            })
        else:
            if is_verified is True:
                if is_subscribed["status"] != "subscribed":
                    _type = ""
                    if withdraw_channel == "bank":
                        _type = "account"
                    if withdraw_channel == "mobile money":
                        _type = "mobilemoney"
                    getWithdrawFee = _withdraw.getWithdrawfee(request, lang, userid, withdraw_amount, currency,_type)
                    total_withdraw = float(withdraw_amount) - float(getWithdrawFee)
                    transactions = []
                    rave = Rave(DEPOSIT_PUB_KEY, DEPOSIT_SEC_KEY, usingEnv=False)

                    details = {
                            "account_bank": account_bank,
                            "account_number": account_number,
                            "amount": total_withdraw,
                            "currency": currency,
                            "beneficiary_name": beneficiary_name,
                            "meta": {
                                "sender": "Flutterwave Developers",
                                "sender_country": "ZA",
                                "mobile_number": "23457558595"
                                }
                            }
                    res = rave.Transfer.initiate(details)
                    transactions.append(res)
                    if transactions[0]["error"] is False:
                        transaction = _transaction.createTransfer(request, lang, transactions)
                        transactionid = transaction["transaction_id"]
                        withdraw = _withdraw.withdrawFromGoal(request, lang, goalid, user, transactionid)
                        return Response(withdraw)
                else:
                    return Response({
                        "message": "your account subscription is overdue, withdraw may not proceed till you subscribe",
                        "success": False
                    })
            else:
                return Response({
                    "message": "your account is not verified, please check your email and verify",
                    "success": False
                })


class GetWithdrawsByAuthUser(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        userid = request.user.id
        user = _user.getAuthUserById(request, lang, userid)
        lang = DEFAULT_LANG if lang is None else lang
        withdraw = _withdraw.getAllWithdraws(request, lang, user)
        return Response(withdraw)


class GetInvestmentWithdraws(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        userid = request.user.id
        lang = DEFAULT_LANG if lang is None else lang
        withdraw = _withdraw.getWithdrawsByInvestmentOption(request, lang, userid)
        return Response(withdraw)


class IsVerified(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        is_verified = request.user.userprofile.is_verified
        if is_verified is True:
            return Response({
                "message": "User is verified",
                "success": True
            })
        else:
            return Response({
                "message": "User is not verified",
                "success": False
            })


class GetInvestmentOption(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        userid = request.user.id
        lang = DEFAULT_LANG if lang is None else lang
        options = _investmentOption.getInvestmentOptions(request, lang, userid)
        return Response(options)


class GetInvestmentOptionByName(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang):
        investment_option = request.data
        userid = request.user.id
        lang = DEFAULT_LANG if lang is None else lang
        options = _investmentOption.getInvestmentOptionByName(request, lang, userid, option=investment_option)
        return Response(options)


class GetInvestmentOptionById(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang):
        investment_id = request.data["investment_id"]
        deposit_amount = request.data["deposit_amount"]
        userid = request.user.id
        if not investment_id:
            return {
                "message": "This field is required",
                "success": False,
                "type": "investment option id"
            }
        elif not deposit_amount:
            return {
                "message": "This field is required",
                "success": False,
                "type": "deposit amount"
            }
        lang = DEFAULT_LANG if lang is None else lang
        options = _investmentOption.getInvestmentOptionById(request, lang, userid, investment_id, deposit_amount)
        return Response(options)


class GetTotalWithdrawByAuthUser(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        userid = request.user.id
        user = _user.getAuthUserById(request, lang, userid)
        lang = DEFAULT_LANG if lang is None else lang
        withdraw = _withdraw.getAllTotalWithdraws(request, lang, user)
        return Response(withdraw)


class GetPendingWithdrawsByAuthUser(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        userid = request.user.id
        user = _user.getAuthUserById(request, lang, userid)
        lang = DEFAULT_LANG if lang is None else lang
        withdraw = _withdraw.getAllPendingWithdraws(request, lang, user)
        return Response(withdraw)


class GetWithdrawNetworths(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        userid = request.user.id
        user = _user.getAuthUserById(request, lang, userid)
        lang = DEFAULT_LANG if lang is None else lang
        withdraw = _withdraw.getWithdrawNetworths(request, lang, user)
        return Response(withdraw)


class GetWithdrawsById(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang, withdrawid):
        lang = DEFAULT_LANG if lang is None else lang
        withdraw = _withdraw.getWithdrawById(request, lang, withdrawid)
        return Response(withdraw)


class GetNetworth(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang, user):
        lang = DEFAULT_LANG if lang is None else lang
        networth = _networth.getNetworth(request, lang)
        return Response(networth)


class GetGoalNetworth(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        lang = DEFAULT_LANG if lang is None else lang
        userid = request.user.id
        user = _user.getAuthUserById(request, lang, userid)
        networth = _networth.getGoalNetworth(request, lang, user)
        return Response(networth)


class GetSubscriptionStatus(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang):
        lang = DEFAULT_LANG if lang is None else lang
        userid = request.user.id
        subscription = _subscription.getSubscriptionStatus(request, lang, userid)
        return Response(subscription)


class Subscribe(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        user = _user.getAuthUser(request, lang)
        userid = user["user_id"]
        reference = request.data["reference"]
        reference_id = request.data["reference_id"]
        amount = request.data["amount"]
        lang = DEFAULT_LANG if lang is None else lang
        txRef = request.data["tx_ref"]
        if not txRef:
            return Response({
                "message": "This field is required",
                "success": False,
                "type": "txRef"
            })
        elif not reference_id:
            return Response({
                "message": "This field is required",
                "success": False,
                "type": "reference_id"
            })
        elif not reference:
            return Response({
                "message": "This field is required",
                "success": False,
                "type": "reference number"
            })
        elif not amount:
            return Response({
                "message": "This field is required",
                "success": False,
                "type": "amount"
            })
        else:
            txRef = _refs.getTxRef()
            subscribe = _subscription.subscribe(request, lang, userid, txRef)
            return Response(subscribe)


#######################################
# deposit data set
class DepositDataSet(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        data_set = request.data
        if not data_set:
            return Response({
                "message": "The data set is required",
                "success": False
            })
        else:
            for data in data_set:
                date = data["date"]
                year = datetime.datetime.strptime(date, "%Y-%m-%d")
                month = year.strftime("%b")
                new_year = year.strftime("%Y")
                data["date"] = new_year
                data["updated"] = month
            return Response(data_set)


class OnboardAuthUsersDeposits(ObtainAuthToken):
    authentication_classes = ()
    permission_classes = ()
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        lang = DEFAULT_LANG if lang is None else lang
        deposits = request.data
        if len(deposits) <= 0:
            return Response({
                "message": "No deposits in this databse",
                "success": False
            })
        else:
            for deposit in deposits:
                if not deposit["email"] or not deposit["deposit_amount"] or not deposit["payment_method"] or not deposit["currency"] or not deposit["date"]:
                    return Response({
                        'message': "Something is missing",
                        "type": "required",
                        'success': False
                    })
                else:
                    email = deposit["email"]
                    user = _user.getAuthUserByEmail(request, lang, email)
                    _deposit.createDeposits(request, lang, deposit, user)
            number = len(deposits)
            return Response({
                "users": number,
                "message": "These users have their deposits in order",
                "success": True
            })


class OnboardAuthUsersWithdraws(ObtainAuthToken):
    authentication_classes = ()
    permission_classes = ()
    http_method_names = ['post']

    def post(self, request, lang, *args, **kwargs):
        lang = DEFAULT_LANG if lang is None else lang
        withdraws = request.data
        if len(withdraws) <= 0:
            return Response({
                "message": "No withdraw data",
                "success": False
            })
        else:
            for withdraw in withdraws:
                if not withdraw["email"] or not withdraw["withdraw"] or not withdraw["date"]:
                    return Response({
                        'message': "Something is missing",
                        "type": "required",
                        'success': False
                    })
                else:
                    email = withdraw["email"]
                    user = _user.getAuthUserByEmail(request, lang, email)
                    _withdraw.withdraws(request, lang, withdraw, user)
            number = len(withdraws)
            return Response({
                "users": number,
                "message": "These users have their withdraws in order",
                "success": True
            })


class GetUserActualNetworthData(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, lang, *args, **kwargs):
        lang = DEFAULT_LANG if lang is None else lang
        userid = request.user.id
        user_deposit = _deposit.getDepositsByInvestmentOption(request, lang, userid)
        return Response(user_deposit)


# class CheckSubscriptionModalDisplayStatus(APIView):
#     authentication_classes = [SessionAuthentication, TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     http_method_names = ['get']

#     def get(self, request, lang, *args, **kwargs):
#         lang = DEFAULT_LANG if lang is None else lang
#         userid = request.user.id
#         user_deposit = _deposit.getDepositsByInvestmentOption(request, lang, userid)
#         return Response(user_deposit)
