import datetime
from .models import *
from .helper import helper
from .v1.locale import Locale
from django.contrib.auth.models import User


class Deposits:
    def __init__(self):
        self.help = helper.Helper()

    def getDeopsitById(self, request,lang, depositid):
        if Deposit.objects.filter(pk=depositid).exists():
            ddeposit = Deposit.objects.filter(pk=depositid).get()
            return{
                "payment_means": ddeposit.payment_means,
                "deposit_category": ddeposit.deposit_category,
                "deposit_amount": ddeposit.deposit_amount,
                "currency": ddeposit.currency,
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
            getDeposits = []
            goal = Goal.objects.filter(pk=goalid)
            for deposit in ddeposit:
                amount = deposit.deposit_amount
                totalDeposit += amount
                for goals in goal:
                    getDeposits.append({
                        "deposit_id":deposit.id,
                        "deposit_amount":deposit.deposit_amount,
                        "currency":deposit.currency,
                        "deposit_category":deposit.deposit_category,
                        "payment_means":deposit.payment_means,
                        "account_type":deposit.account_type.code_name
                    })
            return totalDeposit,getDeposits
        else:
            return {
                "0"
            }
    
    def getAllDeposits(self,request,lang,user):
        deposits = []
        totalDepositAmount = 0
        totalUGX = 0
        totalUSD = 0
        totalDepositUGX = 0
        totalDepositUSD = 0
        userid = request.user.id
        ddeposits = Deposit.objects.filter(user_id=userid)
        for deposit in ddeposits:
            if deposit.user.id == userid:
                amount = deposit.deposit_amount
                currency = deposit.currency
                if currency == "UGX":
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
                "currency": deposit.currency,
                "account_type": deposit.account_type.pk,
                "created": deposit.created,
            })
        goalDepositsUGX = Goals.getAllUserGoals(self,request,lang,user)[0]
        goalDepositUSD = Goals.getAllUserGoals(self,request,lang,user)[1]
        
        totalDepositUGX = totalUGX - goalDepositsUGX
        totalDepositUSD = totalUSD - goalDepositUSD
        return totalDepositUGX,totalDepositUSD,totalUGX,totalUSD,deposits
    
    def depositToGoal(self,request,lang,user,goalid):
        current_datetime = datetime.datetime.now()
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        deposit_amount = request.data["deposit_amount"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        # get the user from Authorised user in token
        userid = request.user.id
        user_name = request.user.first_name
        # print(userid)
        # # make sure the user is verified
        is_verified = request.user.userprofile.is_verified
        # print(userid)
        # # create deposit
        account_type = AccountType.objects.filter(code_name=account_type).get()
        if is_verified is True:
        # # create deposit
            deposit = Deposit.objects.create(
                deposit_amount=float(request.data["deposit_amount"]),
                payment_means=request.data["payment_means"],
                user=User(pk=int(userid)),
                goal=Goal(pk=int(goalid)),
                deposit_category=deposit_category,
                currency=currency,
                account_type=account_type
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



    def createDeposit(self, request, lang, user):
        current_datetime = datetime.datetime.now()
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        deposit_amount = request.data["deposit_amount"]
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        # get the user from Authorised user in token
        userid = request.user.id
        user_name = request.user.first_name
        # make sure the user is verified
        is_verified = request.user.userprofile.is_verified
        # print(userid)
        # # create deposit
        account_type = AccountType.objects.filter(code_name=account_type).get()
        if is_verified is True:
            deposit = Deposit.objects.create(
                deposit_amount=float(request.data["deposit_amount"]),
                payment_means=request.data["payment_means"],
                user=User(pk=int(userid)),
                deposit_category=deposit_category,
                currency=currency,
                account_type=account_type
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
        self.help = helper.Helper()
        
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
                deposit = Deposits.getDeopsitByGoalId(Deposits,request,lang,goalid=goalid)
                goals.append({
                "user_id":goal.user.id,
                "goal_id":goalid,
                "goal_name": goal.goal,
                "goal_amount": goal.goal_amount,
                "goal_period": goal.goal_period,
                "deposit_type": goal.deposit_type,
                "deposit_reminder_day": goal.deposit_reminder_day,
                "created": goal.created,
                "deposit": deposit
                }
                )
            return totalUGX,totalUSD,goals
        else: 
            return 0
        
class NextOfKins:
    def __init__(self):
        self.help = helper.Helper()
        
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
        self.help = helper.Helper()
        
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
        investment_option = request.data["investment_option"]
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
            if riskprofile.risk_analysis is not "Incomplete Risk Profile":
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
        
        
        