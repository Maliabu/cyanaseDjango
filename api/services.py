
import datetime
from .models import *
from .helper.helper import Helper
from .v1.locale import Locale
from django.contrib.auth.models import User
import requests
import uuid

BEARER_INVESTORS = 'FLWSECK_TEST-ce0f1efc8db1d85ca89adb75bbc1a3c8-X'
BEARER_SAVERS = 'FLWSECK_TEST-abba21c766a57acb5a818a414cd69736-X'


_helper = Helper()

class TransactionRef:
    def getTxRef():
        txRef = str(uuid.uuid4())
        return txRef
class Subscriptions:
    def __init__(self):
        self.help = Helper()
        
    def verifyTransaction(self,transaction_id):
        r = requests.get("https://api.flutterwave.com/v3/transactions/"+transaction_id+"/verify",auth=BearerAuth(BEARER_SAVERS)).json()
        return r["status"]
    
    def getSubscriptionStatus(self,request,lang,userid):
        # account creation date
        account_date = User.objects.filter(pk=userid).get()
        start_date = account_date.date_joined
        startt_date = datetime.datetime.strptime(start_date.strftime("%Y/%m/%d"), "%Y/%m/%d")
        now = datetime.datetime.now()
        noww = datetime.datetime.strptime(now.strftime("%Y/%m/%d"),"%Y/%m/%d")
        delta = noww - startt_date
        time = delta.days
        subscribed = Subscription.objects.filter(user_id=userid)
        if subscribed.exists():
            for subscription in subscribed:
                if subscription.is_subscribed == True:
                    return{
                        "status":"subscribed",
                        "days_passed":time
                    }
                elif subscription.is_subscribed == False and subscription.days_left < 30:
                    return{
                        "status":"pending",
                        "days_passed":time
                    }
                elif subscription.is_subscribed == False and subscription.days_left > 30:
                    return{
                        "status":"overdue",
                        "days_passed":time
                    }
                else:
                    return{
                        "status":"pending",
                        "days_passed":time
                    }
        else:
            if time < 30:
                return{
                        "status":"pending",
                        "days_passed":time
                    }
            else:
                return{
                        "status":"overdue",
                        "days_passed":time
                    }
    
    def subscribe(self,request,lang,userid,txRef):
        days_left = self.getSubscriptionStatus(request,lang,userid)
        days_remaining = days_left["days_passed"]
        created = datetime.datetime.now()
        reference = request.data["reference"]
        referenceid = request.data["reference_id"]
        txRef = txRef
        amount = 20500
        currency = "UGX"
        # lets make sure the user pays the right amount
        subscription_amount = request.data["amount"]
        if str(subscription_amount) != str(amount):
            print(amount,subscription_amount)
            return ({
                "message":"Something went wrong. Subscription unsuccessful - amount",
                "success": False
            })
        else:
            old_subscription = Subscription.objects.filter(user_id=userid)
            if old_subscription.exists():
                old_subscription.update(
                    user=User(pk=int(userid)),
                    days_left=days_remaining,
                    reference=reference,
                    reference_id=referenceid,
                    amount=float(amount),
                    currency=currency,
                    txRef=txRef
                )
                for subscription in old_subscription:
                    return({
                        "message":"You have subscribed successfully",
                    "success": True,
                    "user_id":userid,
                    "subscription_id":subscription.id,
                    "reference_id":subscription.reference_id,
                    "subscription_amount": subscription.amount,
                    "currency":subscription.currency,
                    "reference":subscription.reference,
                    "days_left":subscription.days_left,
                    "created":subscription.created
                    })
            else:
                subscribe = Subscription.objects.create(
                    user=User(pk=int(userid)),
                    days_left=days_remaining,
                    reference=reference,
                    reference_id=referenceid,
                    amount=float(amount),
                    currency=currency,
                    txRef=txRef
                )
                # change status to True
                subscribe.is_subscribed = True
                subscribe.save()
                subscriptionid = subscribe.pk
                return({
                    "message":"You have subscribed successfully",
                    "success": True,
                    "user_id":userid,
                    "subscription_id":subscriptionid,
                    "reference_id":referenceid,
                    "subscription_amount": amount,
                    "currency":currency,
                    "reference":reference,
                    "days_left":days_left,
                    "created":created
                })
class Deposits:
    def __init__(self):
        self.help = Helper()

    def getDeopsitById(self, request,lang, depositid):
        if Deposit.objects.filter(pk=depositid).exists():
            ddeposit = Deposit.objects.filter(pk=depositid).get()
            return{
                "payment_means": ddeposit.payment_means,
                "deposit_category": ddeposit.deposit_category,
                "deposit_amount": ddeposit.deposit_amount,
                "currency": ddeposit.currency,
                "investment_option":ddeposit.investment_option,
                "account_type": ddeposit.account_type.pk,
                "created": ddeposit.created,
            }
        else:
            return {
                "0"
            }
    
    def getDeopsitByGoalId(self, request,lang, goalid):
        if Deposit.objects.filter(goal_id=goalid).exists():
            ddeposit = Deposit.objects.filter(goal_id=goalid)
            totalDeposit = 0
            withdraw = Withdraws.getWithdrawsByGoalId(Withdraws,request,lang,goalid)
            withdraw_list = list(withdraw)
            networth = 0
            getDeposits = []
            goal = Goal.objects.filter(pk=goalid)
            for deposit in ddeposit:
                amount = deposit.deposit_amount
                totalDeposit += amount
                networth = float((totalDeposit*0.15)+totalDeposit) - float(withdraw_list[0])
                for goals in goal:
                    getDeposits.append({
                        "deposit_id":deposit.id,
                        "deposit_amount":deposit.deposit_amount,
                        "currency":deposit.currency,
                        "deposit_category":deposit.deposit_category,
                        "payment_means":deposit.payment_means,
                        "investment_option":deposit.investment_option,
                        "account_type":deposit.account_type.code_name
                    })
            return totalDeposit,networth,getDeposits
        else:
            return {
                "0"
            }
            
    def verifyTransaction(self,transaction_id):
        r = requests.get("https://api.flutterwave.com/v3/transactions/"+transaction_id+"/verify",auth=BearerAuth(BEARER_INVESTORS)).json()
        print(r["status"])
        return r["status"]
            
    def getTxRefById(self,request,lang,user,txRef):
        userid = request.user.id
        ddeposits = Deposit.objects.filter(user_id=userid)
        if ddeposits.exists():
            for deposit in ddeposits:
                tx_ref = deposit.txRef
                txref = str(txRef)
                print(txref,tx_ref)
                if txref == tx_ref:
                    print("YES")
                    return {
                        "message":"txRef matches",
                        "success": True
                    }
                else:
                    print("NO")
                    return {
                        "message":"txRef doesnot match",
                        "success": False
                    }
        else:
            print("NO")
            return {
                        "message":"No deposits found for your account",
                        "success": False
                    }
            
    def getAllDeposits(self,request,lang,user):
        deposits = []
        options = []
        dates = []
        totalDepositAmount = 0
        totalUGX = 0
        totalUSD = 0
        depo = []
        totalDepositUGX = 0
        totalDepositUSD = 0
        userid = request.user.id
        ddeposits = Deposit.objects.filter(user_id=userid)
        for deposit in ddeposits:
            if deposit.user.id == userid:
                amount = deposit.deposit_amount
                currency = deposit.currency
                if currency != "USD":
                    totalUGX += amount
                else:
                    totalUSD += amount
                    totalDepositAmount += amount
            depositid = deposit.pk
            deposits.append({
                "user":deposit.user.username,
                "user_id":deposit.user.id,
                "deposit_id":depositid,
                "payment_means": deposit.payment_means,
                "deposit_category": deposit.deposit_category,
                "deposit_amount": deposit.deposit_amount,
                "investment_option":deposit.investment_option,
                "currency": deposit.currency,
                "account_type": deposit.account_type.pk,
                "created": deposit.created.strftime("%d %b"),
            })
            options.append(deposit.investment_option)
        goalDepositsUGX = Goals.getAllUserGoals(self,request,lang,user)[0]
        goalDepositUSD = Goals.getAllUserGoals(self,request,lang,user)[1]
        
        totalDepositUGX = totalUGX - goalDepositsUGX
        totalDepositUSD = totalUSD - goalDepositUSD
        option = set(options)
        for item in option:
            aamount = Deposit.objects.filter(investment_option=item)
            for amount in aamount:
                depo.append({"name":item, "datas":amount.deposit_amount/1000,"date":amount.created.strftime("%d %b")})
                dates.append(amount.created.strftime("%d %b"))
        # myData = list({names["name"]:names for names in depo}.values())
        # deposits.sort(reverse=True)
        return totalDepositUGX,totalDepositUSD,totalUGX,totalUSD,depo,dates,deposits,goalDepositsUGX
    
    def depositToGoal(self,request,lang,user,goalid,txRef):
        current_datetime = datetime.datetime.now()
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        investment_option = request.data["investment_option"]
        deposit_amount = request.data["deposit_amount"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        reference = request.data["reference"]
        reference_id = request.data["reference_id"]
        txRef = txRef
        # get the user from Authorised user in token
        userid = request.user.id
        user_name = request.user.first_name
        # print(userid)
        # # make sure the user is verified
        is_verified = request.user.userprofile.is_verified
        # print(userid)
        # # create deposit
        account_type = AccountType.objects.filter(code_name=account_type).get()
        if is_verified is False:
        # # create deposit
            deposit = Deposit.objects.create(
                deposit_amount=float(deposit_amount),
                payment_means=payment_means,
                user=User(pk=int(userid)),
                goal=Goal(pk=int(goalid)),
                deposit_category=deposit_category,
                investment_option = investment_option,
                currency=currency,
                account_type=account_type,
                reference = reference,
                reference_id = reference_id,
                txRef=txRef
            )
            deposit.save()
            # # get deposit id
            depositid = deposit.id
            # # Get the user making the deposit by id
            deposit = self.getDeopsitById(request, lang, depositid)
            goal = Goal.objects.filter(pk=goalid).get()
            goalname = goal.goal
            goal.save()
            return {
                "message": f"You have successfully deposited {currency} {deposit_amount} to {goalname}",
                "success": True,
                "user_id": userid,
                "goal_id": goalid,
                "user_name": user_name,
                "deposit_id": depositid,
                "deposit": deposit,
                "time of deposit": current_datetime
            }
        else:
            return{
                "message": "your account is not verified, please check your email and verify",
                "success": False
            }



    def createDeposit(self, request, lang, user,txRef):
        current_datetime = datetime.datetime.now()
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        deposit_amount = request.data["deposit_amount"]
        investment_option = request.data["investment_option"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        reference = request.data["reference"]
        reference_id = request.data["reference_id"]
        txRef = txRef
        # get the user from Authorised user in token
        userid = request.user.id
        user_name = request.user.first_name
        # make sure the user is verified
        is_verified = request.user.userprofile.is_verified
        # print(userid)
        # # create deposit
        account_type = AccountType.objects.filter(code_name=account_type).get()
        # check if a user is verified to deposit
        if is_verified is False:
            deposit = Deposit.objects.create(
                deposit_amount=float(request.data["deposit_amount"]),
                payment_means=payment_means,
                user=User(pk=int(userid)),
                deposit_category=deposit_category,
                investment_option=investment_option,
                currency=currency,
                account_type=account_type,
                reference=reference,
                reference_id=reference_id,
                txRef=txRef
            )
            deposit.save()
            # # get deposit id
            depositid = deposit.id
            # # Get the user making the deposit by id
            deposit = self.getDeopsitById(request, lang, depositid)
            return {
                "message": f"You have successfully deposited {currency} {deposit_amount} to your {account_type} account",
                "success": True,
                "user_id": userid,
                "user_name": user_name,
                "deposit_id": depositid,
                "deposit": deposit,
                "time of deposit": current_datetime
            }
        else:
            return{
                "message": "your account is not verified, please check your email and verify",
                "success": False
            }

class Goals:
    def __init__(self):
        self.help = Helper()
        
    def createGoal(self, request,lang,user):
        current_datetime = datetime.datetime.now()
        goalname = request.data["goal_name"]
        goalperiod = request.data["goal_period"]
        goalamount = request.data["goal_amount"]
        deposittype = request.data["deposit_type"]
        dreminderday = request.data["deposit_reminder_day"]
        userid = request.user.id
        goal = Goal.objects.create(
            goal = goalname,
            goal_period = goalperiod,
            goal_amount = goalamount,
            user=User(pk=int(userid)),
            deposit_type = deposittype,
            deposit_reminder_day = dreminderday
        )
        goal.save()
        goalid = goal.id
        goal = self.getGoalById(request,lang,goalid)
        return{
            "message": f"You have successfully created a goal to {goalname} of {goalamount} within {goalperiod} years",
            "success": True,
            "user_id":userid,
            "goalid": goalid,
            "goal": goal,
            "time goal was created": current_datetime
        }
            
    def getGoalById(self, request,lang, goalid):
        if Goal.objects.filter(pk=goalid).exists():
            goal = Goal.objects.filter(pk=goalid).get()
            return{
                "user_id":goal.user.id,
                "goal_id":goalid,
                "goal_name": goal.goal,
                "goal_amount": goal.goal_amount,
                "goal_period": goal.goal_period,
                "deposit_type": goal.deposit_type,
                "deposit_reminder_day": goal.deposit_reminder_day,
                "status": goal.is_active,
                "created": goal.created
            }
        else:
            return {
                "no id found"
            }
    
    def getAllUserGoals(self,request,lang,user):
        goals = []
        totalUGX = 0
        totalUSD = 0
        userid = request.user.id
        ggoals = Goal.objects.filter(user_id=userid)
        if ggoals.exists:
            for goal in ggoals:
                goalid = goal.pk
                deposit = Deposits.getDeopsitByGoalId(Deposits,request,lang,goalid)
                withdraw = Withdraws.getWithdrawsByGoalId(Withdraws,request,lang,goalid)
                goals.append({
                "user_id":goal.user.id,
                "goal_id":goalid,
                "goal_name": goal.goal,
                "goal_amount": goal.goal_amount,
                "goal_period": goal.goal_period,
                "deposit_type": goal.deposit_type,
                "deposit_reminder_day": goal.deposit_reminder_day,
                "created": goal.created,
                "deposit": deposit,
                "withdraw":withdraw
                }
                )
            return totalUGX,totalUSD,goals
        else: 
            return 0
        
class NextOfKins:
    def __init__(self):
        self.help = Helper()
        
    def addNextOfKin(self,request,lang,user):
        current_datetime = datetime.datetime.now()
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        email = request.data["email"]
        phone = request.data["phone"]
        userid = request.user.id
        user_email = User.objects.filter(pk=userid).get()
        useremail = user_email.email
        if useremail == email:
            return{
                "message": "you cannot be your own next of kin",
                "success": False
            }
        # check for existing next of kin for the suer
        nnextOfKin = NextOfKin.objects.filter(user_id=userid)
        if nnextOfKin.exists():
            # update existing
            nnextOfKin.update(
                first_name = first_name,
                last_name = last_name,
                email = email,
                phone = phone
            )
            for nnext_of_kin in nnextOfKin:
                return{
                    "message": f"You have successfully edited a Next of Kin",
                    "success": True,
                    "user_id":userid,
                    "next_of_kin_id": nnext_of_kin.id,
                    "created": current_datetime
                }
        
        else:
            # create a new one
            nextOfKin = NextOfKin.objects.create(
                first_name = first_name,
                last_name = last_name,
                email = email,
                phone = phone,
                user=User(pk=int(userid))
            )
            nextOfKin.save()
            nextOfKinId = nextOfKin.id
            nextOfKin = self.getNextOfKinById(request,lang,nextOfKinId,userid)
            return{
                "message": f"You have successfully added a Next of Kin",
                "success": True,
                "user_id":userid,
                "next_of_kin_id": nextOfKinId,
                "next_of_kin": nextOfKin,
                "time goal was created": current_datetime
            }
        
        
    def getNextOfKinById(self,request,lang,nextOfKinId,userid):
        if NextOfKin.objects.filter(pk=nextOfKinId).exists():
            nextOfKin = NextOfKin.objects.filter(pk=nextOfKinId).get()
            return {
                "user_id":userid,
                "Next_of_kin_id": nextOfKin.id,
                "kin_first_name": nextOfKin.first_name,
                "kin_last_name": nextOfKin.last_name,
                "kin_email": nextOfKin.email,
                "kin_phone": nextOfKin.phone,
                "created": nextOfKin.created
            }
        else: return {
            "no id found"
        }
    
    
    def getNextOfKin(self,request,lang,user):
        userid = request.user.id
        nextOfKin = NextOfKin.objects.filter(user_id=userid)
        if nextOfKin.exists():
            for item in nextOfKin:
                itemid = item.id
                return {
                    "user_id":userid,
                    "Next_of_kin_id": itemid,
                    "kin_first_name": item.first_name,
                    "kin_last_name": item.last_name,
                    "kin_email": item.email,
                    "kin_phone": item.phone,
                    "created": item.created
                }
        else: return {
            "no next of kin exists for this user"
        }
    
    def updateNextOfKin(self,request,lang,nextOfKinId,userid):
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        email = request.data["email"]
        phone = request.data["phone"]
        old_nextOfKin = NextOfKin.objects.filter(pk=nextOfKinId)
        if old_nextOfKin.exists():
            old_nextOfKin.update(
                first_name = first_name,
                last_name = last_name,
                email = email,
                phone = phone
            )
            return{
                "message": "Next of kin updated successfully",
                "success": True
            }
        else:
            return{
                "message": "Please add a next of kin",
                "success": False
            }

class RiskProfiles:
    def __init__(self):
        self.help = Helper()
        
    def addRiskProfile(self,request,lang,user):
        userid = request.user.id
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
        investmentOption = request.data["investment_option"]
        print(investmentOption)
        investment_option = ""
        if investmentOption == "":
            investment_option = "Cash | Venture | Credit"
        else:
            investment_option = investmentOption
        # check for exisiting risk profile for the user
        rriskprofile = RiskProfile.objects.filter(user_id=userid)
        if rriskprofile.exists():
            rriskprofile.update(
                qn1 = qn1,
                qn2 = qn2,
                qn3 = qn3,
                qn4 = qn4,
                qn5 = qn5,
                qn6 = qn6,
                qn7 = qn7,
                qn8 = qn8,
                qn9 = qn9,
                qn10 = qn10,
                qn11 = qn11,
                score = score,
                investment_option = investment_option,
                risk_analysis = risk_analysis
            )
            for rrisk_profile in rriskprofile:
                if rrisk_profile.risk_analysis == "Incomplete Risk Profile":
                    rrisk_profile.is_complete = False
                    return {
                        "message": "risk profile is incomplete",
                        "success": False,
                        "riskprofile_id":rrisk_profile.id,
                        "status": rrisk_profile.is_complete
                    }
                elif rrisk_profile.risk_analysis == "Complete":
                    rrisk_profile.is_complete = True
                    return {
                        "message": "risk profile updated successfully",
                        "success": True,
                        "riskprofile_id":rrisk_profile.id,
                        "status": rrisk_profile.is_complete
                }
        else:
            # create the risk profile
            riskprofile = RiskProfile.objects.create(
                qn1 = qn1,
                qn2 = qn2,
                qn3 = qn3,
                qn4 = qn4,
                qn5 = qn5,
                qn6 = qn6,
                qn7 = qn7,
                qn8 = qn8,
                qn9 = qn9,
                qn10 = qn10,
                qn11 = qn11,
                investment_option = investment_option,
                score = score,
                user=User(pk=int(userid)),
                risk_analysis = risk_analysis
            )
            if riskprofile.risk_analysis != "Incomplete Risk Profile":
                riskprofile.is_complete = True
                riskprofile.save()
                riskprofileid = riskprofile.id
                return {
                    "message": "risk profile created successfully",
                    "success": True,
                    "riskprofile_id":riskprofileid,
                    "status": riskprofile.is_complete
                }
            else:
                return{
                    "message": "risk profile not created",
                    "success":False
                }
    
    def getRiskProfile(self,request,lang,user):
        userid = request.user.id
        riskprofile = RiskProfile.objects.filter(user_id=userid)
        if riskprofile.exists():
            for item in riskprofile:
                itemid = item.id
                return {
                    "user_id":userid,
                    "riskprofile_id": itemid,
                    "status": item.is_complete,
                    "investment_option":item.investment_option,
                    "created": item.created
                }
        else: return {
            "no risk profile exists for this user"
        }
        
        
class Withdraws:
    def __init__(self):
        self.help = Helper()
        
    def withdraw(self,request,lang,user,transactionid):
        withdraw_channel = request.data["withdraw_channel"]
        withdraw_amount = request.data["withdraw_amount"]
        userid = request.user.id
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        created = datetime.datetime.now()
        account_type = AccountType.objects.filter(code_name=account_type).get()
        status = "pending"
        withdraw = Withdraw.objects.create(
                    withdraw_channel=withdraw_channel,
                    withdraw_amount=float(withdraw_amount),
                    currency=currency,
                    account_type=account_type,
                    user=User(pk=int(userid)),
                    transaction=BankTransaction(pk=int(transactionid)),
                    status=status
                )
        withdrawid = withdraw.id
        withdraw.save()
        wwithdraw = self.getWithdrawById(request,lang,withdrawid)
        return{
                    "message": f"Your withdraw is now pending",
                    "success": True,
                    "user_id":userid,
                    "withdraw_id": withdrawid,
                    "withdraw": wwithdraw,
                    "time withdraw was created": created,
                    "transaction":transactionid
                }
        
    def getAllWithdraws(self,request,lang,user):
        wwithdraws = []
        total_withdraw = 0
        userid = request.user.id
        withdraws = Withdraw.objects.filter(user_id=userid)
        if withdraws.exists:
            for withdraw in withdraws:
                withdrawid = withdraw.pk
                total_withdraw+=withdraw.withdraw_amount
                wwithdraws.append({
                    "withdarw_id": withdrawid,
                    "withdraw_channel":withdraw.withdraw_channel,
                    "withdraw_amount":withdraw.withdraw_amount,
                    "currency":withdraw.currency,
                    "account_type":withdraw.account_type.code_name,
                    "status":withdraw.status,
                    "created":withdraw.created
                })
            return wwithdraws
        else:
            return 0
    
    def getAllTotalWithdraws(self,request,lang,user):
        total_withdraw = 0
        userid = request.user.id
        withdraws = Withdraw.objects.filter(user_id=userid)
        if withdraws.exists:
            for withdraw in withdraws:
                total_withdraw+=withdraw.withdraw_amount
            return total_withdraw
        else:
            return 0
        
    def getAllPendingWithdraws(self,request,lang,user):
        wwithdraws = []
        userid = request.user.id
        withdraws = Withdraw.objects.filter(user_id=userid)
        if withdraws.exists:
            for withdraw in withdraws:
                withdrawid = withdraw.pk
                if withdraw.status == "pending":
                    wwithdraws.append({
                    "withdarw_id": withdrawid,
                    "withdraw_channel":withdraw.withdraw_channel,
                    "withdraw_amount":withdraw.withdraw_amount,
                    "currency":withdraw.currency,
                    "account_type":withdraw.account_type.code_name,
                    "status":withdraw.status,
                    "created":withdraw.created.strftime("%d %b")
                    })
            return wwithdraws
        else:
            return "None"
    
    def getWithdrawById(self,request,lang,withdrawid):
        withdraws = Withdraw.objects.filter(pk=withdrawid)
        if withdraws.exists():
            withdraw = withdraws.get()
            return{
                "withdarw_id": withdrawid,
                "withdraw_channel":withdraw.withdraw_channel,
                "withdraw_amount":withdraw.withdraw_amount,
                "currency":withdraw.currency,
                "account_type":withdraw.account_type.code_name,
                "status":withdraw.status,
                "created":withdraw.created
            }
            
    def getWithdrawsByGoalId(self, request,lang, goalid):
        if Withdraw.objects.filter(goal_id=goalid).exists():
            wwithdraw = Withdraw.objects.filter(goal_id=goalid)
            totalWithdraw = 0
            getWithdraws = []
            goal = Goal.objects.filter(pk=goalid)
            for withdraw in wwithdraw:
                amount = withdraw.withdraw_amount
                totalWithdraw += amount
                for goals in goal:
                    getWithdraws.append({
                        "withdraw_id":withdraw.id,
                        "withdraw_amount":withdraw.withdraw_amount,
                        "currency":withdraw.currency,
                        "withdraw_channel":withdraw.withdraw_channel,
                        "account_type":withdraw.account_type.code_name
                    })
            return totalWithdraw,getWithdraws
        else:
            return {
                "0"
            }
    
    def withdrawFromGoal(self,request,lang,goalid,user,transactionid):
        withdraw_channel = request.data["withdraw_channel"]
        withdraw_amount = request.data["withdraw_amount"]
        userid = request.user.id
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        created = datetime.datetime.now()
        is_verified = request.user.userprofile.is_verified
        account_type = AccountType.objects.filter(code_name=account_type).get()
        status = "pending"
        ## remember to verify the user
        if is_verified is False:
        # # create withdraw transaction
            withdraw = Withdraw.objects.create(
            withdraw_channel=withdraw_channel,
            withdraw_amount=withdraw_amount,
            currency=currency,
            goal=Goal(pk=int(goalid)),
            account_type=account_type,
            user=User(pk=int(userid)),
            status=status,
            transaction=BankTransaction(pk=int(transactionid))
            )
            withdrawid = withdraw.id
            withdraw.save()
            wwithdraw = self.getWithdrawById(request,lang,withdrawid)
            goal = Goal.objects.filter(pk=goalid).get()
            goalname = goal.goal
            goal.save()
            return {
                "message": f"You have successfully withdrawn {currency} {withdraw_amount} from goal: {goalname}",
                "success": True,
                "user_id": userid,
                "goal_id": goalid,
                "withdraw_id": withdrawid,
                "withdraw": wwithdraw,
                "time of withdraw": created
            }
        else:
            return{
                "message": "your account is not verified, please check your email and verify",
                "success": False
            }
            
    def getWithdrawNetworths(self,request,lang,user):
        no_goals = 0
        goals = 0
        userid = request.user.id
        withdraw = Withdraw.objects.filter(user_id=userid)
        for wwithdraw in withdraw:
            goal = wwithdraw
            amount = wwithdraw.withdraw_amount
            if goal.goal is None:
                no_goals+=amount
            else:
                goals+=amount
        return goals,no_goals
    
    
    def getWithdrawfee(self,request,lang,userid,withdraw_amount,currency,_type):
        amount = request.data["withdraw_amount"]
        currency = request.data["currency"]
        withdraw_amount = str(amount)
        # _type = "account" | "mobilemoney"
        r = requests.get("https://api.flutterwave.com/v3/transfers/fee?amount="+withdraw_amount+"&currency="+currency+"&type="+_type,auth=BearerAuth(BEARER_INVESTORS)).json()
        return r["data"][0]["fee"]
            
class BearerAuth(requests.auth.AuthBase):
        
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r    
class Networths:
    def __init__(self):
        self.help = Helper()
        
    def getNetworth(self,request,lang,user):
        totalDeposit = 0
        userid = request.user.id
        deposit = Deposit.objects.filter(user_id=userid)
        for ddeposit in deposit:
            amount = ddeposit.deposit_amount
            totalDeposit+=amount
        return totalDeposit
        
    def getGoalNetworth(self,request,lang,user):
        no_goals = 0
        goals = 0
        userid = request.user.id
        deposit = Deposit.objects.filter(user_id=userid)
        for ddeposit in deposit:
            goal = ddeposit
            amount = ddeposit.deposit_amount
            if goal.goal is None:
                no_goals+=amount
            else:
                goals+=amount
        withdraw = Withdraws.getWithdrawNetworths(Withdraws,request,lang,user)
        networth = (no_goals*0.15)+no_goals
        networths = networth - float(withdraw[1])
        return goals,no_goals,networths

class BankTransactions:
    def __init__(self):
        self.help = Helper()
        
    def createTransfer(self,request,lang,transaction):
        userid = request.user.id
        account_number = transaction[0]["data"]["account_number"]
        bank_code = transaction[0]["data"]["bank_code"]
        reference_id = transaction[0]["data"]["id"]
        reference = transaction[0]["data"]["reference"]
        created = transaction[0]["data"]["date_created"]
        transfer = BankTransaction.objects.create(
            user=User(pk=int(userid)),
            account_number=account_number,
            bank_code=bank_code,
            reference_id=reference_id,
            reference=reference,
            created=created
        )
        transferid = transfer.id
        transfer.save()
        ttransfer = BankTransactions.getTransferById(self,request,lang,transferid)
        return{
            "message": f"Transaction made successfully",
                "success": True,
                "user_id": userid,
                "transaction_id": transferid,
                "transaction":ttransfer
            }
        
    def getTransferById(self,request,lang,transferid):
        transfer = BankTransaction.objects.filter(pk=transferid)
        if transfer.exists():
            ttransfer = transfer.get()
            return{
                "transaction_id": transferid,
                "refrence_id": ttransfer.reference_id,
                "reference": ttransfer.reference,
                "account_number": ttransfer.account_number,
                "bank_code":ttransfer.bank_code,
                "created":ttransfer.created
            }