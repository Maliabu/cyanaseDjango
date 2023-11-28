
import datetime
from .models import Deposit, AccountType, Goal, Subscription, Withdraw, RiskProfile, Networth, NextOfKin, InvestmentOption, InvestmentPerformance, RiskAnalysis, BankTransaction
from .helper.helper import Helper
# from .v1.locale import Locale
from django.contrib.auth.models import User
import requests
import uuid
from collections import defaultdict
import itertools
# import os

BEARER_INVESTORS = 'FLWSECK_TEST-ce0f1efc8db1d85ca89adb75bbc1a3c8-X'
BEARER_SAVERS = 'FLWSECK_TEST-abba21c766a57acb5a818a414cd69736-X'  # fails to verify transactions with this bearer


_helper = Helper()


class TransactionRef:
    def getTxRef(self):
        txRef = str(uuid.uuid4())
        return txRef


class InvestmentOptions:
    def getInvestmentOptions(self, request, lang, userid):
        user = User.objects.filter(pk=userid).exists()
        option = InvestmentOption.objects.all()
        investment_options = []
        if user is True:
            for options in option:
                investment_options.append({
                    "investment_option_id": options.pk,
                    "investment_option": options.name,
                    "class_type": options.class_type.pk,
                    "fund_manager": options.fund_manager.pk,
                    "minimum_deposit": options.minimum,
                    "interest": options.interest,
                    "status": options.status,
                    "units": options.units,
                    "fund": options.fund,
                    "created": options.created
                })
            return investment_options
        else:
            return {
                "message": "No investment options available",
                "success": False
            }

    def getInvestmentOptionByName(self, request, lang, userid, option):
        user = User.objects.filter(pk=userid).exists()
        option = InvestmentOption.objects.filter(name=option)
        investment_options = []
        if user is True:
            for options in option:
                investment_options.append({
                    "investment_option_id": options.pk,
                    "investment_option": options.name,
                    "class_type": options.class_type.pk,
                    "fund_manager": options.fund_manager.pk,
                    "minimum_deposit": options.minimum,
                    "interest": options.interest,
                    "status": options.status,
                    "units": options.units,
                    "fund": options.fund,
                    "created": options.created
                })
            return investment_options
        else:
            return {
                "message": "This investment option is not available",
                "success": False
            }

    def getInvestmentOptionById(self, request, lang, userid, id, deposit_amount):
        user = User.objects.filter(pk=userid).exists()
        option = InvestmentOption.objects.filter(pk=id)
        units_accumulated = 0
        option_id = ''
        investment_options = []
        biggest_investment_option = []
        performance_ids = []
        biggest_performance = 0
        if user is True:
            # if the user exists, get their selected option
            for options in option:
                investment_options.append({
                    "option_id": options.pk,
                    "investment_option": options.name,
                    "class_type": options.class_type.pk,
                    "fund_manager": options.fund_manager.pk,
                    "minimum_deposit": options.minimum,
                    "interest": options.interest,
                    "status": options.status,
                    "units": options.units,
                    "fund": options.fund,
                    "created": options.created
                })
            option_id = options.pk
            # lets get the performance for the investment option to get
            # units accumulated by the user
            investment_option_performance = InvestmentPerformance.objects.filter(investment_option_id=option_id)
            # multiple ids may be available
            # we need the highest pk value associated with the ids.
            for performance in investment_option_performance:
                # get the result with the biggest performance id
                performance_ids.append(performance.pk)
                order_performance_ids = sorted(performance_ids)
                biggest_performance = order_performance_ids[-1]
                # now we have the highest id, lets get the object there
            if performance.pk == biggest_performance:
                biggest_investment_option.append(performance.pk)
                total_units = performance.units
                selling_price = performance.selling
                units_accumulated = (total_units/selling_price) * int(deposit_amount)
                # now lets update the units for the performance of this investment option
                new_units = total_units + units_accumulated
                # lets get the biggest investment option and update units
                biggest_option = InvestmentPerformance.objects.filter(pk=biggest_performance)
                biggest_option.update(
                    units=new_units
                )
            # return {
            #     "units_accumulated": units_accumulated,
            #     "investment option": options.name,
            #     "handled_by": options.fund_manager.name
            # }
            return units_accumulated
        else:
            return {
                "message": "This investment option is not available",
                "success": False
            }

    def getWithdrawInvestmentOptionById(self, request, lang, userid, id, withdraw_amount):
        user = User.objects.filter(pk=userid).exists()
        option = InvestmentOption.objects.filter(pk=id)
        units_accumulated = 0
        option_id = ''
        investment_options = []
        biggest_investment_option = []
        performance_ids = []
        biggest_performance = 0
        if user is True:
            # if the user exists, get their selected option
            for options in option:
                investment_options.append({
                    "option_id": options.pk,
                    "investment_option": options.name,
                    "class_type": options.class_type.pk,
                    "fund_manager": options.fund_manager.pk,
                    "minimum_deposit": options.minimum,
                    "interest": options.interest,
                    "status": options.status,
                    "units": options.units,
                    "fund": options.fund,
                    "created": options.created
                })
            option_id = options.pk
            # lets get the performance for the investment option to get
            # units accumulated by the user
            investment_option_performance = InvestmentPerformance.objects.filter(investment_option_id=option_id)
            # multiple ids may be available
            # we need the highest pk value associated with the ids.
            for performance in investment_option_performance:
                # get the result with the biggest performance id
                performance_ids.append(performance.pk)
                order_performance_ids = sorted(performance_ids)
                biggest_performance = order_performance_ids[-1]
                # now we have the highest id, lets get the object there
            if performance.pk == biggest_performance:
                biggest_investment_option.append(performance.pk)
                total_units = performance.units
                selling_price = performance.selling
                units_accumulated = (total_units/selling_price) * int(withdraw_amount)
                # now lets update the units for the performance of this investment option
                new_units = total_units - units_accumulated
                # lets get the biggest investment option and update units
                biggest_option = InvestmentPerformance.objects.filter(pk=biggest_performance)
                biggest_option.update(
                    units=new_units
                )
            # return {
            #     "units_accumulated": units_accumulated,
            #     "investment option": options.name,
            #     "handled_by": options.fund_manager.name
            # }
            return units_accumulated
        else:
            return {
                "message": "This investment option is not available",
                "success": False
            }


class Subscriptions:
    def __init__(self):
        self.help = Helper()

    def verifyTransaction(self, transaction_id):
        r = requests.get("https://api.flutterwave.com/v3/transactions/"+transaction_id+"/verify", auth=BearerAuth(BEARER_SAVERS)).json()
        return r["status"]

    def getSubscriptionStatus(self, request, lang, userid):
        # account creation date
        account_date = User.objects.filter(pk=userid).get()
        start_date = account_date.date_joined
        startt_date = datetime.datetime.strptime(start_date.strftime("%Y/%m/%d"), "%Y/%m/%d")
        now = datetime.datetime.now()
        noww = datetime.datetime.strptime(now.strftime("%Y/%m/%d"), "%Y/%m/%d")
        delta = noww - startt_date
        time = delta.days
        subscribed = Subscription.objects.filter(user_id=userid)
        if subscribed.exists():
            for subscription in subscribed:
                if subscription.is_subscribed is True:
                    return {
                        "status": "subscribed",
                        "days_passed": time
                    }
                elif subscription.is_subscribed is False and subscription.days_left < 30:
                    return {
                        "status": "pending",
                        "days_passed": time
                    }
                elif subscription.is_subscribed is False and subscription.days_left > 30:
                    return {
                        "status": "overdue",
                        "days_passed": time
                    }
                else:
                    return {
                        "status": "pending",
                        "days_passed": time
                    }
        else:
            if time < 30:
                return {
                        "status": "pending",
                        "days_passed": time
                    }
            else:
                return {
                        "status": "overdue",
                        "days_passed": time
                    }

    def subscribe(self, request, lang, userid, txRef):
        days_left = self.getSubscriptionStatus(request, lang, userid)
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
            return ({
                "message": "Something went wrong. Subscription unsuccessful - amount",
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
                    return ({
                        "message": "You have subscribed successfully",
                        "success": True,
                        "user_id": userid,
                        "subscription_id": subscription.id,
                        "reference_id": subscription.reference_id,
                        "subscription_amount": subscription.amount,
                        "currency": subscription.currency,
                        "reference": subscription.reference,
                        "days_left": subscription.days_left,
                        "created": subscription.created
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
                return ({
                    "message": "You have subscribed successfully",
                    "success": True,
                    "user_id": userid,
                    "subscription_id": subscriptionid,
                    "reference_id": referenceid,
                    "subscription_amount": amount,
                    "currency": currency,
                    "reference": reference,
                    "days_left": days_left,
                    "created": created
                })


class Deposits:
    def __init__(self):
        self.help = Helper()

    def getDeopsitById(self, request, lang, depositid):
        if Deposit.objects.filter(pk=depositid).exists():
            ddeposit = Deposit.objects.filter(pk=depositid).get()
            return {
                "payment_means": ddeposit.payment_means,
                "deposit_category": ddeposit.deposit_category,
                "deposit_amount": ddeposit.deposit_amount,
                "currency": ddeposit.currency,
                "investment_option": ddeposit.investment_option.name,
                "account_type": ddeposit.account_type.pk,
                "created": ddeposit.created,
            }
        else:
            return {
                "0"
            }

    def getDeopsitByGoalId(self, request, lang, goalid):
        if Deposit.objects.filter(goal_id=goalid).exists():
            ddeposit = Deposit.objects.filter(goal_id=goalid)
            totalDeposit = 0
            withdraw = Withdraws.getWithdrawsByGoalId(Withdraws, request, lang, goalid)
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
                        "deposit_id": deposit.id,
                        "deposit_amount": deposit.deposit_amount,
                        "currency": deposit.currency,
                        "deposit_category": deposit.deposit_category,
                        "payment_means": deposit.payment_means,
                        "investment_option": deposit.investment_option.name,
                        "account_type": deposit.account_type.code_name
                    })
            return totalDeposit, networth, getDeposits
        else:
            return {
                "0"
            }

    def verifyTransaction(self, transaction_id):
        r = requests.get("https://api.flutterwave.com/v3/transactions/"+transaction_id+"/verify", auth=BearerAuth(BEARER_INVESTORS)).json()
        return r["status"]

    # def getLinkingProviders(self):
    #     r = requests.get("http://localhost:4040/linking/providers")
    #     print(r["providers"])
    #     return r["providers"]

    def getTxRefById(self, request, lang, user, txRef):
        userid = request.user.id
        ddeposits = Deposit.objects.filter(user_id=userid)
        if ddeposits.exists():
            for deposit in ddeposits:
                tx_ref = deposit.txRef
                txref = str(txRef)
                if txref == tx_ref:
                    return {
                        "message": "txRef matches",
                        "success": True
                    }
                else:
                    return {
                        "message": "txRef doesnot match",
                        "success": False
                    }
        else:
            return {
                        "message": "No deposits found for your account",
                        "success": False
                    }

    def getDepositsByInvestmentOption(self, request, lang, userid):
        investment_options_ids = []
        investment_data = []
        option_withdraws = Withdraw.objects.filter(user_id=userid)
        # get all user deposits
        deposits = Deposit.objects.filter(user_id=userid)
        if deposits.exists():
            for deposit in deposits:
                investment_options_ids.append(deposit.investment_option.pk)
        for item in investment_options_ids:
            option_withdraws.filter(investment_option_id=item)
        for withdraw in option_withdraws:
            if withdraw is not None:
                investment_data.append({
                    "name": withdraw.investment_option.name,
                    "withdraw_amount": withdraw.withdraw_amount
                })
            else:
                investment_data.append({
                    "name": withdraw.investment_option.name,
                    "withdraw_amount": 0
                })
        return investment_data

    def getAllDeposits(self, request, lang):
        deposits = []
        options = []
        dates = []
        totalDepositAmount = 0
        totalUGX = 0
        totalUSD = 0
        depo = []
        totalNetworth = 0
        totalDepositUGX = 0
        totalDepositUSD = 0
        userid = request.user.id
        ddeposits = Deposit.objects.filter(user_id=userid)
        for deposit in ddeposits:
            if deposit.user.id == userid:
                amount = deposit.deposit_amount
                networth = deposit.networth
                currency = deposit.currency
                if currency != "USD":
                    totalUGX += amount
                    totalNetworth += networth
                else:
                    totalUSD += amount
                    totalDepositAmount += amount
            depositid = deposit.pk
            if deposit.investment_option.pk is not None:
                deposits.append({
                    "user": deposit.user.username,
                    "user_id": deposit.user.id,
                    "deposit_id": depositid,
                    "payment_means": deposit.payment_means,
                    "deposit_category": deposit.deposit_category,
                    "deposit_amount": deposit.deposit_amount,
                    "investment_option": deposit.investment_option.pk,
                    "currency": deposit.currency,
                    "networth": deposit.networth,
                    "account_type": deposit.account_type.pk,
                    "created": deposit.created.strftime("%d %b")
                })
            else:
                pass
        for amount in ddeposits:
            depo.append({"name": amount.investment_option.name, "datas": amount.deposit_amount/1000, "date": amount.created.strftime("%d %b"), "networths": amount.networth, "id": amount.investment_option.pk})
            dates.append(amount.created.strftime("%d %b"))
        goalDepositsUGX = Goals.getAllUserGoals(self, request, lang)[0]
        goalDepositUSD = Goals.getAllUserGoals(self, request, lang)[1]
        totalDepositUGX = totalUGX - goalDepositsUGX
        totalDepositUSD = totalUSD - goalDepositUSD
        # get total networths for diff investments options invested by user
        grouped_dict = defaultdict(list)
        for investment in deposits:
            grouped_dict[investment["investment_option"]].append(investment)
        grouping = grouped_dict.values()
        # grouped_dict["total"].append(sum_networths)
        # values = set(map(lambda x: x[1], depo))
        # newlist = [[y[0] for y in depo if y[1] == x] for x in values]
        ###########################
        # dates.append((str(amount.created))[0:10])
        # myData = list({names["name"]:names for names in depo}.values())
        # deposits.sort(reverse=True)
        return totalDepositUGX, totalDepositUSD, totalUGX, totalUSD, depo, dates, deposits, goalDepositsUGX, options, totalNetworth, grouped_dict, grouping

    def depositToGoal(self, request, lang, goalid, txRef, investment, investment_id, deposit_amount):
        current_datetime = datetime.datetime.now()
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
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
        if is_verified is True:
            # # create deposit
            deposit = Deposit.objects.create(
                deposit_amount=float(deposit_amount),
                payment_means=payment_means,
                user=User(pk=int(userid)),
                deposit_category=deposit_category,
                investment_option=InvestmentOption(pk=int(investment_id)),
                currency=currency,
                account_type=account_type,
                reference=reference,
                reference_id=reference_id,
                txRef=txRef,
                units=int(investment),
                available=True,
                goal=Goal(pk=int(goalid))
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
                "time of deposit": current_datetime
            }
        else:
            return {
                "message": "your account is not verified, please check your email and verify",
                "success": False
            }

    def createDeposit(self, request, lang, txRef, investment, investment_id, deposit_amount):
        current_datetime = datetime.datetime.now()
        payment_means = request.data["payment_means"]
        deposit_category = request.data["deposit_category"]
        # deposit_amount = request.data["deposit_amount"]
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
        if is_verified is True:
            deposit = Deposit.objects.create(
                deposit_amount=float(deposit_amount),
                payment_means=payment_means,
                user=User(pk=int(userid)),
                deposit_category=deposit_category,
                investment_option=InvestmentOption(pk=int(investment_id)),
                currency=currency,
                account_type=account_type,
                reference=reference,
                reference_id=reference_id,
                txRef=txRef,
                units=int(investment),
                available=True
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
            return {
                "message": "your account is not verified, please check your email and verify",
                "success": False
            }

    def createDeposits(self, request, lang, deposit, user):
        payment_means = "online"
        deposit_category = "personal"
        deposit_amount = deposit["deposit_amount"]
        currency = deposit["currency"]
        created = deposit["date"]
        account_type = "basic"
        reference = "TEST"
        reference_id = 0
        txRef = "CYANASE_TEST"
        userid = user["user_id"]
        account_type = AccountType.objects.filter(code_name=account_type).get()
        deposit = Deposit.objects.create(
                deposit_amount=float(deposit_amount),
                payment_means=payment_means,
                user=User(pk=int(userid)),
                deposit_category=deposit_category,
                currency=currency,
                account_type=account_type,
                reference=reference,
                reference_id=reference_id,
                investment_option=InvestmentOption(pk=0),
                txRef=txRef,
                created=created,
                units=0,
                available=True
            )
        deposit.save()
        # # get deposit id
        depositid = deposit.id
        # # Get the user making the deposit by id
        deposit = self.getDeopsitById(request, lang, depositid)
        if deposit:
            return {
                "message": "Yeap deposits are in",
                "success": True
            }
        else:
            return {
                "message": "something went terribly wrong",
                "success": False
            }


class AccountTypes:
    def __init__(self):
        self.help = Helper()

    def createAccountTypes(self, request, lang):
        type_name = request.data["type_name"]
        code_name = request.data["code_name"]
        description = request.data["description"]
        sort_value = request.data["sort_value"]
        is_default = request.data["is_default"]
        is_disabled = False
        account_type = AccountType.objects.create(
            type_name=type_name,
            code_name=code_name,
            description=description,
            sort_value=sort_value,
            is_default=is_default,
            is_disabled=is_disabled
        )
        account_type.save()
        accounttypeid = account_type.id
        if accounttypeid:
            return {
                "message": "Account Types added",
                "success": True
            }
        else:
            return {
                "message": "Account Types not added here",
                "success": False
            }


class Goals:
    def __init__(self):
        self.help = Helper()

    def createGoal(self, request, lang, user):
        current_datetime = datetime.datetime.now()
        goalname = request.data["goal_name"]
        goalperiod = request.data["goal_period"]
        goalamount = request.data["goal_amount"]
        deposittype = request.data["deposit_type"]
        dreminderday = request.data["deposit_reminder_day"]
        userid = request.user.id
        is_verified = request.user.userprofile.is_verified
        if is_verified is True:
            goal = Goal.objects.create(
                goal=goalname,
                goal_period=goalperiod,
                goal_amount=goalamount,
                user=User(pk=int(userid)),
                deposit_type=deposittype,
                deposit_reminder_day=dreminderday
            )
            goal.save()
            goalid = goal.id
            goal = self.getGoalById(request, lang, goalid)
            return {
                "message": f"You have successfully created a goal to {goalname} of {goalamount} within {goalperiod} years",
                "success": True,
                "user_id": userid,
                "goalid": goalid,
                "goal": goal,
                "time goal was created": current_datetime
            }
        else:
            return {
                "message": "your account is not verified, please check your email and verify",
                "success": False
            }

    def getGoalById(self, request, lang, goalid):
        if Goal.objects.filter(pk=goalid).exists():
            goal = Goal.objects.filter(pk=goalid).get()
            return {
                "user_id": goal.user.id,
                "goal_id": goalid,
                "goal_name": goal.goal,
                "goal_amount": goal.goal_amount,
                "goal_period": goal.goal_period,
                "deposit_type": goal.deposit_type,
                "deposit_reminder_day": goal.deposit_reminder_day,
                "status": goal.is_active,
                "created": goal.created.strftime("%d %b")
            }
        else:
            return {
                "no id found"
            }

    def getAllUserGoals(self, request, lang):
        goals = []
        totalUGX = 0
        totalUSD = 0
        userid = request.user.id
        ggoals = Goal.objects.filter(user_id=userid)
        if ggoals.exists:
            for goal in ggoals:
                goalid = goal.pk
                deposit = Deposits.getDeopsitByGoalId(Deposits, request, lang, goalid)
                withdraw = Withdraws.getWithdrawsByGoalId(Withdraws, request, lang, goalid)
                goals.append({
                    "user_id": goal.user.id,
                    "goal_id": goalid,
                    "goal_name": goal.goal,
                    "goal_amount": goal.goal_amount,
                    "goal_period": goal.goal_period,
                    "deposit_type": goal.deposit_type,
                    "deposit_reminder_day": goal.deposit_reminder_day,
                    "created": goal.created.strftime("%d %b"),
                    "deposit": deposit,
                    "withdraw": withdraw
                }
                )
            return totalUGX, totalUSD, goals
        else:
            return 0


class NextOfKins:
    def __init__(self):
        self.help = Helper()

    def addNextOfKin(self, request, lang, user):
        current_datetime = datetime.datetime.now()
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        email = request.data["email"]
        phone = request.data["phone"]
        userid = request.user.id
        user_email = User.objects.filter(pk=userid).get()
        useremail = user_email.email
        if useremail == email:
            return {
                "message": "you cannot be your own next of kin",
                "success": False
            }
        # check for existing next of kin for the suer
        nnextOfKin = NextOfKin.objects.filter(user_id=userid)
        if nnextOfKin.exists():
            # update existing
            nnextOfKin.update(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone
            )
            for nnext_of_kin in nnextOfKin:
                return {
                    "message": "You have successfully edited a Next of Kin",
                    "success": True,
                    "user_id": userid,
                    "next_of_kin_id": nnext_of_kin.id,
                    "created": current_datetime
                }
        else:
            # create a new one
            nextOfKin = NextOfKin.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                user=User(pk=int(userid))
            )
            nextOfKin.save()
            nextOfKinId = nextOfKin.id
            nextOfKin = self.getNextOfKinById(request, lang, nextOfKinId, userid)
            return {
                "message": "You have successfully added a Next of Kin",
                "success": True,
                "user_id": userid,
                "next_of_kin_id": nextOfKinId,
                "next_of_kin": nextOfKin,
                "time goal was created": current_datetime
            }

    def getNextOfKinById(self, request, lang, nextOfKinId, userid):
        if NextOfKin.objects.filter(pk=nextOfKinId).exists():
            nextOfKin = NextOfKin.objects.filter(pk=nextOfKinId).get()
            return {
                "user_id": userid,
                "Next_of_kin_id": nextOfKin.id,
                "kin_first_name": nextOfKin.first_name,
                "kin_last_name": nextOfKin.last_name,
                "kin_email": nextOfKin.email,
                "kin_phone": nextOfKin.phone,
                "created": nextOfKin.created
            }
        else:
            return {
                "no id found"
            }

    def getNextOfKin(self, request, lang, user):
        userid = request.user.id
        nextOfKin = NextOfKin.objects.filter(user_id=userid)
        if nextOfKin.exists():
            for item in nextOfKin:
                itemid = item.id
                return {
                    "user_id": userid,
                    "Next_of_kin_id": itemid,
                    "kin_first_name": item.first_name,
                    "kin_last_name": item.last_name,
                    "kin_email": item.email,
                    "kin_phone": item.phone,
                    "created": item.created
                }
        else:
            return {
                "no next of kin exists for this user"
            }

    def updateNextOfKin(self, request, lang, nextOfKinId, userid):
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        email = request.data["email"]
        phone = request.data["phone"]
        old_nextOfKin = NextOfKin.objects.filter(pk=nextOfKinId)
        if old_nextOfKin.exists():
            old_nextOfKin.update(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone
            )
            return {
                "message": "Next of kin updated successfully",
                "success": True
            }
        else:
            return {
                "message": "Please add a next of kin",
                "success": False
            }


class RiskProfiles:
    def __init__(self):
        self.help = Helper()

    def addRiskProfile(self, request, lang, user):
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
        risk_analysis = []
        investmentOption = request.data["investment_option"]
        investment_option = ""
        analysis = RiskAnalysis.objects.all()
        if investmentOption == "":
            investment_option = "Cash | Venture | Credit | Absolute Return"
            # get risk analysis from score
            for item in analysis:
                min_value = item.score_min
                max_value = item.score_max + 1
                score_range = range(min_value, max_value)
                if int(score) in score_range:
                    risk_analysis.append(item.pk)
        else:
            investment_option = investmentOption
            for item in analysis:
                if item.name == "Non Risk Profile":
                    risk_analysis.append(item.pk)
        # check for exisiting risk profile for the user and update
        rriskprofile = RiskProfile.objects.filter(user_id=userid)
        if rriskprofile.exists():
            rriskprofile.update(
                qn1=qn1,
                qn2=qn2,
                qn3=qn3,
                qn4=qn4,
                qn5=qn5,
                qn6=qn6,
                qn7=qn7,
                qn8=qn8,
                qn9=qn9,
                qn10=qn10,
                qn11=qn11,
                score=score,
                investment_option=investment_option,
                risk_analysis=RiskAnalysis(pk=int(risk_analysis[0]))
            )
            for rrisk_profile in rriskprofile:
                if rrisk_profile.risk_analysis == "Incomplete Risk Profile":
                    rrisk_profile.is_complete = False
                    return {
                        "message": "risk profile is incomplete",
                        "success": False,
                        "riskprofile_id": rrisk_profile.id,
                        "status": rrisk_profile.is_complete
                    }
                elif rrisk_profile.risk_analysis == "Complete":
                    rrisk_profile.is_complete = True
                    return {
                        "message": "risk profile updated successfully",
                        "success": True,
                        "riskprofile_id": rrisk_profile.id,
                        "status": rrisk_profile.is_complete
                    }
        else:
            # create new risk profile
            riskprofile = RiskProfile.objects.create(
                qn1=qn1,
                qn2=qn2,
                qn3=qn3,
                qn4=qn4,
                qn5=qn5,
                qn6=qn6,
                qn7=qn7,
                qn8=qn8,
                qn9=qn9,
                qn10=qn10,
                qn11=qn11,
                investment_option=investment_option,
                score=score,
                user=User(pk=int(userid)),
                risk_analysis=RiskAnalysis(pk=int(risk_analysis[0]))
            )
            if riskprofile.risk_analysis != "Incomplete Risk Profile":
                riskprofile.is_complete = True
                riskprofile.save()
                riskprofileid = riskprofile.id
                return {
                    "message": "risk profile created successfully",
                    "success": True,
                    "riskprofile_id": riskprofileid,
                    "status": riskprofile.is_complete
                }
            else:
                return {
                    "message": "risk profile not created",
                    "success": False
                }

    def getRiskProfile(self, request, lang, user):
        userid = request.user.id
        riskprofile = RiskProfile.objects.filter(user_id=userid)
        if riskprofile.exists():
            for item in riskprofile:
                itemid = item.id
                return {
                    "user_id": userid,
                    "riskprofile_id": itemid,
                    "status": item.is_complete,
                    "investment_option": item.investment_option,
                    "created": item.created
                }
        else:
            return {
                "no risk profile exists for this user"
            }

    def getInvestmentByRiskProfile(self, request, lang):
        userid = request.user.id
        cash = 0
        credit = 0
        venture = 0
        absolute_return = 0
        names = ["Cash", "Credit", "Venture", "Absolute Return"]
        ids = [11, 5, 12, 13]
        percentages = []
        result = []
        # get percentages
        risk_profile = RiskProfile.objects.filter(user_id=userid)
        if risk_profile.exists():
            for item in risk_profile:
                cash = item.risk_analysis.cash
                credit = item.risk_analysis.credit
                venture = item.risk_analysis.venture
                absolute_return = item.risk_analysis.absolute_return
                percentages.append(cash)
                percentages.append(credit)
                percentages.append(venture)
                percentages.append(absolute_return)
        for (name, id, percentage) in itertools.zip_longest(names, ids, percentages):
            result.append({
                "name": name,
                "id": id,
                "percentage": percentage
            })
        return result


class Withdraws:
    def __init__(self):
        self.help = Helper()

    def getAllCountryBanks(self, countryCode):
        r = requests.get("https://api.flutterwave.com/v3/banks/"+str(countryCode), auth=BearerAuth(BEARER_INVESTORS)).json()
        return r

    def withdraw(self, request, lang, user, transactionid, investment_option_id, units):
        withdraw_channel = request.data["withdraw_channel"]
        withdraw_amount = request.data["withdraw_amount"]
        userid = request.user.id
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        created = datetime.datetime.now()
        account_type = AccountType.objects.filter(code_name=account_type).get()
        status = "pending"
        # claculate units to withdraw
        withdraw = Withdraw.objects.create(
                    withdraw_channel=withdraw_channel,
                    withdraw_amount=float(withdraw_amount),
                    currency=currency,
                    account_type=account_type,
                    user=User(pk=int(userid)),
                    transaction=BankTransaction(pk=int(transactionid)),
                    status=status,
                    investment_option=InvestmentOption(pk=int(investment_option_id)),
                    units=int(units)
                )
        withdrawid = withdraw.id
        withdraw.save()
        wwithdraw = self.getWithdrawById(request, lang, withdrawid)
        return {
            "message": "Your withdraw is now pending",
            "success": True,
            "user_id": userid,
            "withdraw_id": withdrawid,
            "withdraw": wwithdraw,
            "time withdraw was created": created,
            "transaction": transactionid
        }

    def withdraws(self, request, lang, withdraw, user):
        withdraw_channel = "bank"
        withdraw_amount = withdraw["withdraw"]
        userid = user["user_id"]
        currency = "UGX"
        account_type = "personal"
        created = withdraw["date"]
        account_type = "basic"
        account_type = AccountType.objects.filter(code_name=account_type).get()
        status = "successful"
        withdraw = Withdraw.objects.create(
                    withdraw_channel=withdraw_channel,
                    withdraw_amount=float(withdraw_amount),
                    currency=currency,
                    account_type=account_type,
                    user=User(pk=int(userid)),
                    created=created,
                    status=status,
                    units=0,
                    investment_option=InvestmentOption(pk=11)
                )
        withdrawid = withdraw.id
        withdraw.save()
        wwithdraw = self.getWithdrawById(request, lang, withdrawid)
        return {
            "message": "ohhh yeah",
            "success": True
        }

    def getWithdrawUnitsByInvestmentOption(self, request, lang, userid):
        withdraw_obj = []
        units = []
        # get all user withdraws
        withdraws = Withdraw.objects.filter(user_id=userid)
        if withdraws.exists():
            for withdraw in withdraws:
                withdraw_obj.append({"name": withdraw.investment_option.name, "datas": withdraw.withdraw_amount, "date": withdraw.created.strftime("%d %b"), "units": withdraw.units})
            return withdraw_obj
        else:
            return units

    def getWithdrawsByInvestmentOption(self, request, lang, userid):
        withdraw_obj = []
        all_withdraws = []
        # get all user withdraws
        withdraws = Withdraw.objects.filter(user_id=userid)
        if withdraws.exists():
            for withdraw in withdraws:
                withdraw_obj.append({"name": withdraw.investment_option.name, "datas": withdraw.withdraw_amount, "date": withdraw.created.strftime("%d %b")})
            return withdraw_obj
        else:
            return all_withdraws

    def getAllWithdraws(self, request, lang, user):
        wwithdraws = []
        total_withdraw = 0
        userid = request.user.id
        withdraws = Withdraw.objects.filter(user_id=userid)
        if withdraws.exists():
            for withdraw in withdraws:
                withdrawid = withdraw.pk
                total_withdraw += withdraw.withdraw_amount
                wwithdraws.append({
                    "withdarw_id": withdrawid,
                    "withdraw_channel": withdraw.withdraw_channel,
                    "withdraw_amount": withdraw.withdraw_amount,
                    "currency": withdraw.currency,
                    "account_type": withdraw.account_type.code_name,
                    "status": withdraw.status,
                    "investment_option": withdraw.investment_option.name,
                    "created": withdraw.created
                })
            return wwithdraws, total_withdraw
        else:
            return 0

    def getAllTotalWithdraws(self, request, lang, user):
        total_withdraw = 0
        userid = request.user.id
        withdraws = Withdraw.objects.filter(user_id=userid)
        if withdraws.exists():
            for withdraw in withdraws:
                total_withdraw += withdraw.withdraw_amount
            return total_withdraw
        else:
            return 0

    def getAllPendingWithdraws(self, request, lang, user):
        wwithdraws = []
        userid = request.user.id
        withdraws = Withdraw.objects.filter(user_id=userid)
        if withdraws.exists():
            for withdraw in withdraws:
                withdrawid = withdraw.pk
                if withdraw.status == "pending":
                    wwithdraws.append({
                        "withdarw_id": withdrawid,
                        "withdraw_channel": withdraw.withdraw_channel,
                        "withdraw_amount": withdraw.withdraw_amount,
                        "currency": withdraw.currency,
                        "account_type": withdraw.account_type.code_name,
                        "status": withdraw.status,
                        "investment_option": withdraw.investment_option.name,
                        "created": withdraw.created.strftime("%d %b")
                    })
            return wwithdraws
        else:
            return "None"

    def getWithdrawById(self, request, lang, withdrawid):
        withdraws = Withdraw.objects.filter(pk=withdrawid)
        if withdraws.exists():
            withdraw = withdraws.get()
            return {
                "withdarw_id": withdrawid,
                "withdraw_channel": withdraw.withdraw_channel,
                "withdraw_amount": withdraw.withdraw_amount,
                "currency": withdraw.currency,
                "account_type": withdraw.account_type.code_name,
                "status": withdraw.status,
                "created": withdraw.created
            }

    def getWithdrawsByGoalId(self, request, lang, goalid):
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
                        "withdraw_id": withdraw.id,
                        "withdraw_amount": withdraw.withdraw_amount,
                        "currency": withdraw.currency,
                        "withdraw_channel": withdraw.withdraw_channel,
                        "account_type": withdraw.account_type.code_name
                    })
            return totalWithdraw, getWithdraws
        else:
            return {
                "0"
            }

    def withdrawFromGoal(self, request, lang, goalid, user, transactionid):
        withdraw_channel = request.data["withdraw_channel"]
        withdraw_amount = request.data["withdraw_amount"]
        userid = request.user.id
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        created = datetime.datetime.now()
        is_verified = request.user.userprofile.is_verified
        account_type = AccountType.objects.filter(code_name=account_type).get()
        status = "pending"
        # remember to verify the user
        if is_verified is True:
            # create withdraw transaction
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
            wwithdraw = self.getWithdrawById(request, lang, withdrawid)
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
            return {
                "message": "your account is not verified, please check your email and verify",
                "success": False
            }

    def getWithdrawNetworths(self, request, lang, user):
        no_goals = 0
        goals = 0
        userid = request.user.id
        withdraw = Withdraw.objects.filter(user_id=userid)
        for wwithdraw in withdraw:
            goal = wwithdraw
            amount = wwithdraw.withdraw_amount
            if goal.goal is None:
                no_goals += amount
            else:
                goals += amount
        return goals, no_goals

    def getWithdrawfee(self, request, lang, userid, withdraw_amount, currency, _type):
        amount = request.data["withdraw_amount"]
        currency = request.data["currency"]
        withdraw_amount = str(amount)
        # _type = "account" | "mobilemoney"
        r = requests.get("https://api.flutterwave.com/v3/transfers/fee?amount="+withdraw_amount+"&currency="+currency+"&type="+_type, auth=BearerAuth(BEARER_INVESTORS)).json()
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

    def getNetworth(self, request, lang, user):
        totalDeposit = 0
        userid = request.user.id
        deposit = Deposit.objects.filter(user_id=userid)
        for ddeposit in deposit:
            amount = ddeposit.deposit_amount
            totalDeposit += amount
        return totalDeposit

    def getGoalNetworth(self, request, lang, user):
        # no goals networth
        # userid = request.user.id
        # networth = Networth.objects.filter(user_id=userid)
        # total_networth = 0
        # for nnetworth in networth:
        #      total_networth += nnetworth.amount
        # return total_networth
        no_goals = 0
        goals = 0
        userid = request.user.id
        # deposit = Deposit.objects.filter(user_id=userid)
        networth = Networth.objects.filter(user_id=userid)
        for nnetworth in networth:
            goal = nnetworth
            amount = nnetworth.amount
            if goal.goal is None:
                no_goals += amount
            else:
                goals += amount
        withdraw = Withdraws.getWithdrawNetworths(Withdraws, request, lang, user)
        networth = (no_goals*0.15)+no_goals
        networths = networth - float(withdraw[1])
        return goals, no_goals, networths


class BankTransactions:
    def __init__(self):
        self.help = Helper()

    def createTransfer(self, request, lang, transaction):
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
        ttransfer = BankTransactions.getTransferById(self, request, lang, transferid)
        return {
            "message": "Transaction made successfully",
            "success": True,
            "user_id": userid,
            "transaction_id": transferid,
            "transaction": ttransfer
        }

    def getTransferById(self, request, lang, transferid):
        transfer = BankTransaction.objects.filter(pk=transferid)
        if transfer.exists():
            ttransfer = transfer.get()
            return {
                "transaction_id": transferid,
                "refrence_id": ttransfer.reference_id,
                "reference": ttransfer.reference,
                "account_number": ttransfer.account_number,
                "bank_code": ttransfer.bank_code,
                "created": ttransfer.created
            }
