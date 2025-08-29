
import datetime
import os
import random
from .models import Deposit, AccountType, Goal, Subscription, Withdraw, RiskProfile, Networth, NextOfKin, InvestmentOption, InvestmentPerformance, RiskAnalysis, BankTransaction, UserProfile, InvestmentClass, InvestmentTrack, Transaction
from .helper.helper import Helper
# from .v1.locale import Locale
from django.contrib.auth.models import User
import requests
import uuid
from collections import defaultdict
import itertools
# import os
from cyanase_api import settings
from api.config import webconfig

import os, hashlib, warnings, requests, json
import base64
from Crypto.Cipher import DES3


BEARER_INVESTORS = DEPOSIT_SEC_KEY
BEARER_SAVERS = SUB_SEC_KEY



_helper = Helper()


class PayTest:

    """this is the getKey function that generates an encryption Key for you by passing your Secret Key as a parameter."""

    def __init__(self):
        pass

    def getKey(self, secret_key):
        hashedseckey = hashlib.md5(secret_key.encode("utf-8")).hexdigest()
        hashedseckeylast12 = hashedseckey[-12:]
        seckeyadjusted = secret_key.replace('FLWSECK-', '')
        seckeyadjustedfirst12 = seckeyadjusted[:12]
        return seckeyadjustedfirst12 + hashedseckeylast12

    """This is the encryption function that encrypts your payload by passing the text and your encryption Key."""

    def encryptData(self, key, plainText):
        blockSize = 8
        padDiff = blockSize - (len(plainText) % blockSize)
        cipher = DES3.new(key, DES3.MODE_ECB)
        plainText = "{}{}".format(plainText, "".join(chr(padDiff) * padDiff))
        # cipher.encrypt - the C function that powers this doesn't accept plain string, rather it accepts byte strings, hence the need for the conversion below
        test = plainText.encode('utf-8')
        encrypted = base64.b64encode(cipher.encrypt(test)).decode("utf-8")
        return encrypted

    def pay_via_card(self):
        data = {
            'PBFPubKey': 'FLWPUBK-e634d14d9ded04eaf05d5b63a0a06d2f-X',
            "cardno": "5531886652142950",
            "cvv": "564",
            "expirymonth": "09",
            "expiryyear": "32",
            "currency": "UGX",
            "country": "UG",
            'suggested_auth': 'pin',
            'pin': '3310',
            "amount": "1000",
            'txRef': 'MC-TESTREF-12345',
            "email": "maliabupatricia@gmail.com",
            # "phonenumber": "+256772971878",
            # "firstname": "patricia",
            # "lastname": "maliabu",
            # "IP": "355426087298442",
            # "device_fingerprint": "69e6b7f0b72037aa8428b70fbe03986c"
        }

        sec_key = 'FLWSECK-bb971402072265fb156e90a3578fe5e6-X'

        # hash the secret key with the get hashed key function
        hashed_sec_key = self.getKey(sec_key)

        # encrypt the hashed secret key and payment parameters with the encrypt function

        encrypt_3DES_key = self.encryptData(hashed_sec_key, json.dumps(data))

        # payment payload
        payload = {
            "PBFPubKey": "FLWPUBK-e634d14d9ded04eaf05d5b63a0a06d2f-X",
            "client": encrypt_3DES_key,
            "alg": "3DES-24"
        }

        # card charge endpoint
        endpoint = "https://ravesandboxapi.flutterwave.com/flwv3-pug/getpaidx/api/charge"

        # set the content type to application/json
        headers = {
            'content-type': 'application/json',
        }

        response = requests.post(
            endpoint, headers=headers, data=json.dumps(payload))
        print(response.json())


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
                    "handler": options.fund_manager.first_name+" "+options.fund_manager.last_name,
                    "fund_manager": options.fund_manager.pk,
                    "minimum_deposit": options.minimum,
                    "interest": options.interest,
                    "description": options.description,
                    "status": options.status,
                    "units": options.units,
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
                # get profile of fund manager then country
                fund_manager_id = options.fund_manager.pk
                fund_manager_country = self.getFundManagerCountry(fund_manager_id)
                investment_options.append({
                    "investment_option_id": options.pk,
                    "investment_option": options.name,
                    "class_type": options.class_type.pk,
                    "fund_manager": options.fund_manager.pk,
                    "handler": options.fund_manager.first_name+" "+options.fund_manager.last_name,
                    "fund_manager_country": fund_manager_country,
                    "minimum_deposit": options.minimum,
                    "interest": options.interest,
                    "status": options.status,
                    "units": options.units,
                    "description": options.description,
                    "created": options.created
                })
            return investment_options
        else:
            return {
                "message": "This investment option is not available",
                "success": False
            }

    def getInvestmentOptionName(self, request, lang, userid, option):
        user = User.objects.filter(pk=userid).exists()
        option = InvestmentOption.objects.filter(name=option)
        investment_options = []
        if user is True:
            for options in option:
                investment_options.append({
                    "investment_option_id": options.pk
                })
            return investment_options
        else:
            return {
                "message": "This investment option is not available",
                "success": False
            }

    def getInvestmentOptionsByClass(self, request, lang, userid, investment_class, fund_manager):
        user = User.objects.filter(pk=userid).exists()
        investment_classes = InvestmentClass.objects.filter(name=investment_class)
        investment_class_id = 0
        for item in investment_classes:
            investment_class_id = item.pk
        option = InvestmentOption.objects.filter(class_type_id=investment_class_id, fund_manager_id=fund_manager)
        investment_options = []
        if user is True:
            for options in option:
                # get profile of fund manager then country
                fund_manager_id = options.fund_manager.pk
                fund_manager_country = self.getFundManagerCountry(fund_manager_id)
                investment_options.append({
                    "investment_option_id": options.pk,
                    "investment_option": options.name,
                    "class_type": options.class_type.pk,
                    "fund_manager": options.fund_manager.pk,
                    "handler": options.fund_manager.first_name+" "+options.fund_manager.last_name,
                    "fund_manager_country": fund_manager_country,
                    "minimum_deposit": options.minimum,
                    "interest": options.interest,
                    "status": options.status,
                    "units": options.units,
                    "description": options.description,
                    "created": options.created
                })
            return investment_options
        else:
            return {
                "message": "This investment option is not available",
                "success": False
            }

    def getInvestmentOptionsByFund(self, request, lang, userid, fid):
        # get all options with fund id
        investment_classes = []
        classes = []
        option = InvestmentOption.objects.filter(fund_manager_id=fid)
        for item in option:
            classes.append(item.class_type.pk)
        unique_classes = set(classes)
        for item in unique_classes:
            # get investment classes by id
            investment_classess = InvestmentClass.objects.filter(pk=int(item))
            for investment_class in investment_classess:
                investment_classes.append({
                    "fund_id": fid,
                    "id": investment_class.pk,
                    "name": investment_class.name,
                    "description": investment_class.description,
                    "logo": f"{webconfig.BASE_URL}media/investmentClasses/{investment_class.logo}"
                })
        return investment_classes

    def getJustInvestmentOptionsByClass(self, request, lang, userid, investment_class):
        user = User.objects.filter(pk=userid).exists()
        investment_classes = InvestmentClass.objects.filter(name=investment_class)
        investment_class_id = 0
        for item in investment_classes:
            investment_class_id = item.pk
        option = InvestmentOption.objects.filter(class_type_id=investment_class_id)
        investment_options = []
        if user is True:
            for options in option:
                if options.fund_manager.is_active == True:
                    investment_options.append({
                        "investment_option_id": options.pk,
                        "investment_option": options.name,
                        "class_type": options.class_type.pk,
                        "fund_manager": options.fund_manager.pk,
                        "handler": options.fund_manager.first_name+" "+options.fund_manager.last_name,
                        "minimum_deposit": options.minimum,
                        "interest": options.interest,
                        "status": options.status,
                        "units": options.units,
                        "description": options.description,
                        "created": options.created
                    })
            return investment_options
        else:
            return {
                "message": "This investment option is not available",
                "success": False
            }

    def getFundManagerCountry(self, fund_manager_id):
        fund_manager_profile = UserProfile.objects.filter(user_id=fund_manager_id)
        if fund_manager_profile.exists():
            for profile in fund_manager_profile:
                country = profile.country
                return country
        else:
            return "No fund manager with this account"

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
                    "handler": options.fund_manager.first_name+" "+options.fund_manager.last_name,
                    "minimum_deposit": options.minimum,
                    "interest": options.interest,
                    "status": options.status,
                    "units": options.units,
                    "description": options.description,
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
            # get option details with highest id
            recent_investment_option = InvestmentPerformance.objects.filter(pk=int(biggest_performance))
            for performance in recent_investment_option:
                biggest_investment_option.append(performance.pk)
                total_units = performance.units
                selling_price = performance.selling
                units_accumulated = int(total_units)/int(selling_price) * int(deposit_amount)
                # now lets update the units for the performance of this investment option(create new performance data)
                new_units = total_units + units_accumulated
                new_units = round(new_units, 2)
                # lets get the biggest investment option and update units
                # biggest_option = InvestmentPerformance.objects.filter(pk=biggest_performance)
                # biggest_option.update( - create new row
                #     units=new_units
                # )
                create_new_performance = InvestmentPerformance.objects.create(
                    units=new_units,
                    selling=performance.selling,
                    bought=performance.bought,
                    management_fee=performance.management_fee,
                    performance_fee=performance.performance_fee,
                    status=performance.status,
                    fund_manager=User(pk=int(performance.fund_manager_id)),
                    investment_option=InvestmentOption(pk=int(performance.investment_option_id))
                )
                create_new_performance.save()
                # performanceid = create_new_performance.pk
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
                    "handler": options.fund_manager.first_name+" "+options.fund_manager.last_name,
                    "minimum_deposit": options.minimum,
                    "interest": options.interest,
                    "status": options.status,
                    "units": options.units,
                    "description": options.description,
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
            # get option details with highest id
            recent_investment_option = InvestmentPerformance.objects.filter(pk=int(biggest_performance))
            for performance in recent_investment_option:
                biggest_investment_option.append(performance.pk)
                total_units = performance.units
                selling_price = performance.selling
                units_accumulated = int(total_units)/int(selling_price) * int(withdraw_amount)
                # now lets update the units for the performance of this investment option(create new performance data)
                new_units = total_units - units_accumulated
                new_units = round(new_units, 2)
                # lets get the biggest investment option and update units
                # biggest_option = InvestmentPerformance.objects.filter(pk=biggest_performance)
                # biggest_option.update( - create new row
                #     units=new_units
                # )
                create_new_performance = InvestmentPerformance.objects.create(
                    units=new_units,
                    selling=performance.selling,
                    bought=performance.bought,
                    management_fee=performance.management_fee,
                    performance_fee=performance.performance_fee,
                    status=performance.status,
                    fund_manager=User(pk=int(performance.fund_manager_id)),
                    investment_option=InvestmentOption(pk=int(performance.investment_option_id))
                )
                create_new_performance.save()
                # performanceid = create_new_performance.pk
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
        # https://api.ravepay.co/flwv3-pug/getpaidx/api/v2/verify
        r = requests.get("https://api.flutterwave.com/v3/transactions/"+transaction_id+"/verify", auth=BearerAuth(BEARER_SAVERS)).json()
        return r["status"]

    def highestId(self, request, lang, userid):
        sub_ids = []
        subscribed = Subscription.objects.filter(user_id=userid)
        if subscribed.exists():
            for subscription in subscribed:
                # now we need the latest subscription - aka highest id
                # lets get all ids sorted and get the last id
                sub_ids.append(subscription.pk)
                sort = sorted(sub_ids)
                lastest_subscription = sort[-1]
            return lastest_subscription
        else:
            return 0

    def getSubscriptionStatus(self, request, lang, userid):
        # account creation date
        account_date = User.objects.filter(pk=userid).get()
        start_date = account_date.date_joined
        startt_date = datetime.datetime.strptime(start_date.strftime("%m/%d"), "%m/%d")
        # date now
        now = datetime.datetime.now()
        noww = datetime.datetime.strptime(now.strftime("%m/%d"), "%m/%d")
        delta = noww - startt_date
        time = delta.days
        # get latest subscription id
        lastest_subscription_id = self.highestId(request, lang, userid)
        subscribed = Subscription.objects.filter(pk=lastest_subscription_id)
        if subscribed.exists():
            for subscription in subscribed:
                display_freq = subscription.was_displayed
                if subscription.is_subscribed is True:
                    # if subscribed
                    # if first time subscription ( time between last subscription and now is less than a year - 366 days)
                    if subscription.days_left <= 366:
                        return {
                            "status": "subscribed",
                            "days_passed": time,
                            "displayed": display_freq,
                            "id": lastest_subscription_id
                        }
                    # else its not the first time ( check and renew subscription every time date today is equal to date user joined)
                    elif subscription.days_left > 366 and noww == startt_date:
                        return {
                            "status": "pending",
                            "days_passed": time,
                            "displayed": display_freq,
                            "id": lastest_subscription_id
                        }
                    elif subscription.days_left > 366 and noww != startt_date:
                        return {
                            "status": "subscribed",
                            "days_passed": time,
                            "displayed": display_freq,
                            "id": lastest_subscription_id
                        }
                elif subscription.is_subscribed is False and subscription.days_left < 30:
                    return {
                        "status": "pending",
                        "days_passed": time,
                        "displayed": display_freq
                    }
                elif subscription.is_subscribed is False and subscription.days_left > 30:
                    return {
                        "status": "overdue",
                        "days_passed": time,
                        "displayed": display_freq
                    }
                else:
                    return {
                        "status": "pending",
                        "days_passed": time,
                        "displayed": display_freq
                    }
        else:
            if time < 30:
                return {
                        "status": "pending",
                        "days_passed": time,
                        "displayed": False
                    }
            else:
                return {
                        "status": "overdue",
                        "days_passed": time,
                        "displayed": False
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
                "message": "Something went wrong. Subscription unsuccessful",
                "success": False,
                "type": "Amount payable"
            })
        else:
            ########## lets not override any data - we need to know how many times a user has paid subscription
            # old_subscription = Subscription.objects.filter(user_id=userid)
            # if old_subscription.exists():
            #     old_subscription.update(
            #         user=User(pk=int(userid)),
            #         days_left=days_remaining,
            #         reference=reference,
            #         reference_id=referenceid,
            #         amount=float(amount),
            #         currency=currency,
            #         txRef=txRef
            #     )
            #     for subscription in old_subscription:
            #         return ({
            #             "message": "You have subscribed successfully",
            #             "success": True,
            #             "user_id": userid,
            #             "subscription_id": subscription.id,
            #             "reference_id": subscription.reference_id,
            #             "subscription_amount": subscription.amount,
            #             "currency": subscription.currency,
            #             "reference": subscription.reference,
            #             "days_left": subscription.days_left,
            #             "created": subscription.created
            #         })
            # else:
            # add new entry for subscription
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


# dont forget to uncomment this for online server
# class Networths:
#     def __init__(self):
#         self.help = Helper()

#     def getDepositNetworth(self, depositid, deposit_amount):
#         interests = []
#         total = 0
#         networths = Networth.objects.filter(deposit_id=depositid)
#         if networths.exists:
#             for item in networths: # clean the strings to django accepted format by removing any special characters
#                 result = ''.join(num for num in item.amount if num.isalnum())
#                 networth = float(result)
#                 # networth = float(item.amount)
#                 interest = networth - deposit_amount
#                 interests.append(interest)
#             total = float(deposit_amount) + sum(interests)
#             if depositid == 1046:
#                 pass
#             else:
#                 pass
#             return total
#         else:
#             return 0


# this will work offline
class Networths:
    def __init__(self):
        self.help = Helper()

    def getDepositNetworth(self, depositid, deposit_amount):
        interests = []
        total = 0
        networths = Networth.objects.filter(deposit_id=depositid)
        if networths.exists:
            for item in networths:
                # clean the strings to django accepted format by removing any special characters
                # result = ''.join(num for num in item.amount if num.isalnum())
                networth = float(item.amount)
                interest = networth - deposit_amount
                interests.append(interest)
            total = float(deposit_amount) + sum(interests)
            return total
        else:
            return 0


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
                # "investment_option": ddeposit.investment_option.name,
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
            new_networth = 0
            getDeposits = []
            totalNetworth = 0
            goal = Goal.objects.filter(pk=goalid)
            for deposit in ddeposit:
                depositid = deposit.pk
                amount = deposit.deposit_amount
                totalNetworth = Networths.getDepositNetworth(Networths, depositid, amount)
                # networth
                # nnetworth = Networth.objects.filter(deposit_id=depositid)
                # for networths in nnetworth:
                #     # get all networths and add to total
                #     interests = float(networths.amount) - amount
                # totalNetworth = amount + interests
                # # networth = deposit.networth
                totalDeposit += amount
                # # totalNetworth += networth
                new_networth = float(totalNetworth) - float(withdraw_list[0])
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
            return totalDeposit, new_networth, getDeposits, totalNetworth
        else:
            return {
                "0"
            }

    def verifyTransaction(self, transaction_id):
        r = requests.get("https://api.flutterwave.com/v3/transactions/"+transaction_id+"/verify", auth=BearerAuth(BEARER_INVESTORS)).json()
        return r["status"]

    def Validate(self, msisdn):
        headers = {
            "Content-Type": "application/json",
            "Accept": 'application/vnd.relworx.v2',
        }
        r = requests.post("https://payments.relworx.com/api/mobile-money/validate", headers=headers, json=msisdn, auth=BearerAuth(BEARER_RLX)).json()
        return r

    def RequestPayment(self, request):
        headers = {
            "Content-Type": "application/json",
            "Accept": 'application/vnd.relworx.v2',
        }
        r = requests.post("https://payments.relworx.com/api/mobile-money/request-payment", headers=headers, json=request, auth=BearerAuth(BEARER_RLX)).json()
        return r

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
        totalNetworthy = 0
        userid = request.user.id
        ddeposits = Deposit.objects.filter(user_id=userid)
        for deposit in ddeposits:
            if deposit.user.id == userid:
                amount = deposit.deposit_amount
                # networth = deposit.networth - before separation
                depositid = deposit.pk
                totalNetworth = Networths.getDepositNetworth(Networths, depositid, amount)
                currency = deposit.currency
                if currency != "USD":
                    totalUGX += amount
                    # totalNetworthy += networthy
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
                    "networth": totalNetworth,
                    "account_type": deposit.account_type.pk,
                    "created": deposit.created.strftime("%d %b")
                })
            else:
                pass
        for amount in ddeposits:
            depositid = amount.pk
            d_amount = amount.deposit_amount
            totalNetworth = Networths.getDepositNetworth(Networths, depositid, d_amount)
            depo.append({"name": amount.investment_option.name, "datas": amount.deposit_amount/1000, "date": amount.created.strftime("%d %b"), "networths": totalNetworth, "id": amount.investment_option.pk, "handler": amount.investment_option.fund_manager.first_name+" "+amount.investment_option.fund_manager.last_name, "logo": f"{webconfig.BASE_URL}media/investmentClasses/{amount.investment_option.class_type.logo}"})
            dates.append(amount.created.strftime("%d %b"))
        goalDepositsUGX = Goals.getAllUserGoals(self, request, lang)['data'][0]
        goalDepositUSD = Goals.getAllUserGoals(self, request, lang)['data'][1]
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
        return {
            "message": "depsoists successful",
            "success": True,
            "data": [totalDepositUGX, totalDepositUSD, totalUGX, totalUSD, depo, dates, deposits, goalDepositsUGX, options, totalNetworthy, grouped_dict, grouping]
        }

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
        units = round(investment, 2)
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
                units=units,
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

    def createDeposit(self, request, lang, txRef, investment, investment_id, deposit_amount, risk_profile):
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
        # make sure the user is verified
        is_verified = request.user.userprofile.is_verified
        # print(userid)
        # # create deposit
        units = round(investment, 2)
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
                units=units,
                available=True
            )
            deposit.save()
            # # get deposit id
            depositid = deposit.id
            # # Get the user making the deposit by id
            # check track table to see if the user deposited in the current
            # option, if not create a new record with zero opening balance
            user_track = InvestmentTrack.objects.filter(
                user_id=userid, investment_option_id=int(investment_id))
            if len(user_track) != 0:
                # create another track record with last
                # investment option record
                # get most recent record with this option - largest id
                record_ids = []
                new_opening_balance = 0
                new_closing_balance = 0
                for record in user_track:
                    record_ids.append(record.investment_option.pk)
                sorted_ids = sorted(record_ids)
                most_recent_investment_option_id = sorted_ids[-1]
                most_recent_investment = InvestmentTrack.objects.filter(
                    investment_option_id=int(most_recent_investment_option_id))
                # we need fees from the investment performance table
                management_fee = 2  # standard
                performance_fee = 0  # fund manager side
                investment_performance = InvestmentPerformance.objects.filter(
                    investment_option_id=int(investment_id))
                for performance in investment_performance:
                    management_fee = performance.management_fee
                    performance_fee = performance.performance_fee
                withdraw_amount = 0
                interest = 0
                # we need interest from investment_option table
                investment_option = InvestmentOption.objects.filter(
                    pk=int(investment_id))
                for option in investment_option:
                    interest = option.interest
                # fees
                for investment in most_recent_investment:
                    new_opening_balance = investment.closing_balance
                    new_closing_balance = (
                        investment.closing_balance + float(deposit_amount) + (
                            interest/100 * float(deposit_amount))) - (
                                (management_fee/100 * float(deposit_amount)) + (
                                    performance_fee/100 * float(deposit_amount)))
                    withdraw_amount = investment.withdraw_amount
                track = InvestmentTrack.objects.create(
                    deposit_amount=deposit_amount,
                    opening_balance=new_opening_balance,
                    closing_balance=new_closing_balance,
                    management_fee=management_fee,
                    interest=interest,
                    performance_fee=performance_fee,
                    withdraw_amount=withdraw_amount,
                    investment_option=InvestmentOption(pk=int(investment_id)),
                    user=User(pk=int(userid)),
                    risk_profile=risk_profile
                )
                track.save()
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
                # new track record for user and option
                # we need fees from the investment performance table
                management_fee = 2  # standard
                performance_fee = 0  # fund manager side
                investment_performance = InvestmentPerformance.objects.filter(
                    investment_option_id=int(investment_id))
                for performance in investment_performance:
                    management_fee = performance.management_fee
                    performance_fee = performance.performance_fee
                withdraw_amount = 0
                interest = 0
                # we need interest from investment_option table
                investment_option = InvestmentOption.objects.filter(
                    pk=int(investment_id))
                for option in investment_option:
                    interest = option.interest
                # claculate opening and closing balance
                # closing balance = deposit + interest ) - (fee% of deposit)
                new_opening_balance = 0
                closing_balance = (float(deposit_amount) + (
                    interest/100 * float(deposit_amount))) - (
                        (management_fee/100 * float(deposit_amount)) + (
                            performance_fee/100 * float(deposit_amount)))
                track = InvestmentTrack.objects.create(
                    deposit_amount=deposit_amount,
                    opening_balance=new_opening_balance,
                    closing_balance=closing_balance,
                    management_fee=management_fee,
                    interest=interest,
                    performance_fee=performance_fee,
                    withdraw_amount=withdraw_amount,
                    investment_option=InvestmentOption(pk=int(investment_id)),
                    user=User(pk=int(userid)),
                    risk_profile=risk_profile
                )
                track.save()
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
        networth = deposit["networth"]
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
                networth=networth,
                reference_id=reference_id,
                investment_option=InvestmentOption(pk=11),
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


class NewDeposits:
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
                # "investment_option": ddeposit.investment_option.name,
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
            new_networth = 0
            getDeposits = []
            totalNetworth = 0
            goal = Goal.objects.filter(pk=goalid)
            for deposit in ddeposit:
                depositid = deposit.pk
                amount = deposit.deposit_amount
                totalNetworth = Networths.getDepositNetworth(Networths, depositid, amount)
                # networth
                # nnetworth = Networth.objects.filter(deposit_id=depositid)
                # for networths in nnetworth:
                #     # get all networths and add to total
                #     interests = float(networths.amount) - amount
                # totalNetworth = amount + interests
                # # networth = deposit.networth
                totalDeposit += amount
                # # totalNetworth += networth
                new_networth = float(totalNetworth) - float(withdraw_list[0])
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
            return totalDeposit, new_networth, getDeposits, totalNetworth
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
        totalNetworthy = 0
        userid = request.user.id
        ddeposits = Deposit.objects.filter(user_id=userid)
        for deposit in ddeposits:
            if deposit.user.id == userid:
                amount = deposit.deposit_amount
                # networth = deposit.networth - before separation
                depositid = deposit.pk
                totalNetworth = Networths.getDepositNetworth(Networths, depositid, amount)
                currency = deposit.currency
                if currency != "USD":
                    totalUGX += amount
                    # totalNetworthy += networthy
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
                    "networth": totalNetworth,
                    "account_type": deposit.account_type.pk,
                    "created": deposit.created.strftime("%d %b")
                })
            else:
                pass
        for amount in ddeposits:
            depositid = amount.pk
            d_amount = amount.deposit_amount
            totalNetworth = Networths.getDepositNetworth(Networths, depositid, d_amount)
            depo.append({"name": amount.investment_option.name, "datas": amount.deposit_amount/1000, "date": amount.created.strftime("%d %b"), "networths": totalNetworth, "id": amount.investment_option.pk, "handler": amount.investment_option.fund_manager.first_name+" "+amount.investment_option.fund_manager.last_name, "logo": f"{webconfig.BASE_URL}media/investmentClasses/{amount.investment_option.class_type.logo}"})
            dates.append(amount.created.strftime("%d %b"))
        goalDepositsUGX = Goals.getAllUserGoals(self, request, lang)['data'][0]
        goalDepositUSD = Goals.getAllUserGoals(self, request, lang)['data'][1]
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
        return totalDepositUGX, totalDepositUSD, totalUGX, totalUSD, depo, dates, deposits, goalDepositsUGX, options, totalNetworthy, grouped_dict, grouping

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
        units = round(investment, 2)
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
                units=units,
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
        units = round(investment, 2)
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
                units=units,
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
        networth = deposit["networth"]
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
                networth=networth,
                reference_id=reference_id,
                investment_option=InvestmentOption(pk=11),
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


class Transactions:
    def __init__(self):
        self.help = Helper()

    def newTransaction(self, request, lang):
        status = request.data["status"]
        message = request.data["message"]
        customer_reference = request.data["customer_reference"]
        internal_reference = request.data["internal_reference"]
        msisdn = request.data["msisdn"]
        amount = request.data["amount"]
        currency = request.data["currency"]
        provider = request.data["provider"]
        charge = request.data["charge"]
        transaction = Transaction.objects.create(
            status=status,
            message=message,
            customer_reference=customer_reference,
            internal_reference=internal_reference,
            msisdn=msisdn,
            amount=amount,
            currency=currency,
            provider=provider,
            charge=charge,
            processed=False
        )
        transaction.save()
        transaction_id = transaction.id
        transactionn = self.getTransactionById(request, lang, transaction_id)
        return {
            "message": "transaction created successfully",
            "success": True,
            "transaction_id": transaction_id,
            "transaction": transaction,
        }

    def getTransactionById(self, request, lang, transaction_id):
        if Transaction.objects.filter(pk=transaction_id).exists():
            transaction = Transaction.objects.filter(pk=transaction_id).get()
            return {
                "success": True,
                "message": "transaction success",
                "processed": transaction.processed,
                "charge": transaction.charge,
                "customer_reference": transaction.customer_reference,
                "internal_reference": transaction.internal_reference,
                "msisdn": transaction.msisdn,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "provider": transaction.provider,
                "status": transaction.status,
                "created": transaction.created.strftime("%d %b")
            }
        else:
            return {
                "success": False,
                "message": "no id found"
            }
    
    def getTransactionByRef(self, request, lang, ref_id):
        if Transaction.objects.filter(internal_reference=ref_id).exists():
            transactionn = Transaction.objects.update(
                processed=True
            )
            transaction = Transaction.objects.filter(internal_reference=ref_id).get()
            return {
                "processed": transaction.processed,
                "charge": transaction.charge,
                "customer_reference": transaction.customer_reference,
                "internal_reference": transaction.internal_reference,
                "msisdn": transaction.msisdn,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "provider": transaction.provider,
                "status": transaction.status,
                "created": transaction.created.strftime("%d %b")
            }
        else:
            return {
                "no id found"
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
        is_active = True
        if is_verified is True:
            goal = Goal.objects.create(
                goal=goalname,
                goal_period=goalperiod,
                goal_amount=goalamount,
                user=User(pk=int(userid)),
                deposit_type=deposittype,
                deposit_reminder_day=dreminderday,
                is_active=is_active
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
                "goal_picture": f"{webconfig.BASE_URL}media/goal/{goal.goal_picture}",
                "created": goal.created.strftime("%d %b")
            }
        else:
            return {
                "no id found"
            }

    def deleteGoalById(self, request, lang, goalid):
        if Goal.objects.filter(pk=goalid).exists():
            Goal.objects.filter(pk=int(goalid)).delete()
            return {
                "message": "goal deleted",
                "success": True
            }
        else:
            return {
                "message": "goal doesnot exist",
                "success": False
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
                    "withdraw": withdraw,
                    "goal_status": goal.is_active,
                    "goal_picture":
                    f"{webconfig.BASE_URL}media/goal/{goal.goal_picture}"
                }
                )
            return {
                "message": "goals fetched successfully",
                "success": True,
                "data": [
                    totalUGX, totalUSD, goals
                ]
            }
        else:
            return {
                "message": "goals fetched successfully",
                "success": True,
                "data": []
            }

    def UpdateGoalPhoto(self, goalid, filename):
        # name = filename.name
        name_id = str(random.random())
        goal_id = str(goalid)
        output = 'goal_picture'+goal_id+name_id+'.jpg'
        #########################
        # let us first delete the other photos of
        # this user before updating a new one
        old_goal_picture = Goal.objects.filter(id=int(goalid)).get()
        old_picture = old_goal_picture.goal_picture
        old_picture_name = old_picture.name
        if old_picture_name != "default_picture.jpg":
            # remove old picture
            os.remove('media/goal/'+old_picture_name)
            destination = open('media/goal/'+output, 'wb+')
            for chunk in filename.chunks():
                destination.write(chunk)
            destination.close()
            Goal.objects.filter(pk=int(goalid)).update(
                goal_picture=output
            )
        else:
            destination = open('media/goal/'+output, 'wb+')
            for chunk in filename.chunks():
                destination.write(chunk)
            destination.close()
            Goal.objects.filter(pk=int(goalid)).update(
                goal_picture=output
            )


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
        riskAnalysis = request.data["risk_analysis"]
        risk_analysis = []
        investment_option = "Automatic Asset Allocation"
        analysis = RiskAnalysis.objects.all()
        is_complete = True
        # get risk analysis from score
        for item in analysis:
            min_value = item.score_min
            max_value = item.score_max + 1
            score_range = range(min_value, max_value)
            if int(score) in score_range:
                # add the analytics id to list
                risk_analysis.append(item.pk)
        # check for exisiting risk profile for the user and update
        rriskprofile = RiskProfile.objects.filter(user_id=userid)
        if rriskprofile.exists():
            # if analysis returns empty list then profile is incomplete
            if len(risk_analysis) != 0:
                # update
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
                    if riskAnalysis == "Incomplete Risk Profile":
                        rrisk_profile.is_complete = False
                        return {
                            "message": "risk profile is incomplete",
                            "success": False,
                            "riskprofile_id": rrisk_profile.id,
                            "status": rrisk_profile.is_complete
                        }
                    else:
                        rrisk_profile.is_complete = True
                        return {
                            "message": "risk profile updated successfully",
                            "success": True,
                            "riskprofile_id": rrisk_profile.id,
                            "status": rrisk_profile.is_complete
                        }
            else:
                return {
                    "message": "Incomplete Risk profile",
                    "success": False,
                }
        else:
            if riskAnalysis != "Incomplete Risk Profile":
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
                    risk_analysis=RiskAnalysis(pk=int(risk_analysis[0])),
                    is_complete=is_complete
                )
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
                    "message": "Incomplete Risk Profile",
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
        risk_profile_status = ""
        # get percentages
        risk_profile = RiskProfile.objects.filter(user_id=userid)
        if risk_profile.exists():
            for item in risk_profile:
                # check score because a zero affects deposit amount
                risk_profile_status = item.is_complete
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
        if risk_profile_status is True:
            return result
        else:
            return []


class Withdraws:
    def __init__(self):
        self.help = Helper()

    def getAllCountryBanks(self, countryCode):
        r = requests.get("https://api.flutterwave.com/v3/banks/"+str(countryCode), auth=BearerAuth(BEARER_INVESTORS)).json()
        return r

    # with transaction transfer initiation
    # def withdraw(self, request, lang, user, transactionid, investment_option_id, units):
    #     withdraw_channel = request.data["withdraw_channel"]
    #     withdraw_amount = request.data["withdraw_amount"]
    #     userid = request.user.id
    #     currency = request.data["currency"]
    #     account_type = request.data["account_type"]
    #     created = datetime.datetime.now()
    #     account_type = AccountType.objects.filter(code_name=account_type).get()
    #     account_bank = request.data["account_bank"]
    #     account_number = request.data["account_number"]
    #     status = "pending"
    #     # cyanase charge 0.2%
    #     charge_amount = float(0.2/100) * float(withdraw_amount)
    #     # claculate units to withdraw
    #     withdraw = Withdraw.objects.create(
    #                 withdraw_channel=withdraw_channel,
    #                 withdraw_amount=float(withdraw_amount),
    #                 currency=currency,
    #                 account_type=account_type,
    #                 user=User(pk=int(userid)),
    #                 transaction=BankTransaction(pk=int(transactionid)),
    #                 status=status,
    #                 investment_option=InvestmentOption(pk=int(investment_option_id)),
    #                 units=units,
    #                 charge_amount=charge_amount,
    #                 account_bank=account_bank,
    #                 account_number=account_number
    #             )
    #     withdrawid = withdraw.id
    #     withdraw.save()
    #     wwithdraw = self.getWithdrawById(request, lang, withdrawid)
    #     return {
    #         "message": "Your withdraw is now pending",
    #         "success": True,
    #         "user_id": userid,
    #         "withdraw_id": withdrawid,
    #         "withdraw": wwithdraw,
    #         "time withdraw was created": created,
    #         "transaction": transactionid
    #     }

    # without transfer
    def withdraw(self, request, lang, user, investment_option_id, units, withdraw_amount):
        withdraw_channel = request.data["withdraw_channel"]
        userid = request.user.id
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        created = datetime.datetime.now()
        account_type = AccountType.objects.filter(code_name=account_type).get()
        account_bank = request.data["account_bank"]
        if withdraw_channel == "mobile money":
            account_number = request.data["phone_number"]
        else:
            account_number = request.data["account_number"]
        status = "pending"
        # cyanase charge 0.2%
        charge_amount = float(0.2/100) * float(withdraw_amount)
        # claculate units to withdraw
        withdraw = Withdraw.objects.create(
            withdraw_channel=withdraw_channel,
            withdraw_amount=float(withdraw_amount),
            currency=currency,
            account_type=account_type,
            user=User(pk=int(userid)),
            status=status,
            investment_option=InvestmentOption(pk=int(investment_option_id)),
            units=round(units, 2),
            created=created,
            charge_amount=charge_amount,
            account_bank=account_bank,
            account_number=account_number
        )
        withdrawid = withdraw.id
        withdraw.save()
        user_track = InvestmentTrack.objects.filter(
                user_id=userid, investment_option_id=int(investment_option_id))
        if len(user_track) != 0:
            # create another track record with last
            # investment option record
            # get most recent record with this option - largest id
            record_ids = []
            new_opening_balance = 0
            new_closing_balance = 0
            for record in user_track:
                record_ids.append(record.investment_option.pk)
            sorted_ids = sorted(record_ids)
            most_recent_investment_option_id = sorted_ids[-1]
            most_recent_investment = InvestmentTrack.objects.filter(
                investment_option_id=int(most_recent_investment_option_id))
            # we need fees from the investment performance table
            management_fee = 0  # standard
            performance_fee = 0
            deposit_amount = 0
            interest = 0
            for investment in most_recent_investment:
                new_opening_balance = investment.closing_balance
                new_closing_balance = (
                    investment.closing_balance - float(withdraw_amount))
            track = InvestmentTrack.objects.create(
                deposit_amount=deposit_amount,
                opening_balance=new_opening_balance,
                closing_balance=new_closing_balance,
                management_fee=management_fee,
                interest=interest,
                performance_fee=performance_fee,
                withdraw_amount=withdraw_amount,
                investment_option=InvestmentOption(
                    pk=int(investment_option_id)),
                user=User(pk=int(userid))
            )
            track.save()
            withdraw = self.getWithdrawById(request, lang, withdrawid)
            return {
                "message": f"You have successfully requested withdraw {currency} {withdraw_amount} to your {account_type} account",
                "success": True,
                "user_id": userid,
                "withdraw_id": withdrawid,
                "withdraw": withdraw
            }
        else:
            # new track record for user and option
            # we need fees from the investment performance table
            management_fee = 2  # standard
            performance_fee = 0  # fund manager side
            investment_performance = InvestmentPerformance.objects.filter(
                investment_option_id=int(investment_option_id))
            for performance in investment_performance:
                management_fee = performance.management_fee
                performance_fee = performance.performance_fee
            withdraw_amount = 0
            interest = 0
            # we need interest from investment_option table
            investment_option = InvestmentOption.objects.filter(
                pk=int(investment_option_id))
            for option in investment_option:
                interest = option.interest
            # claculate opening and closing balance
            # closing balance = deposit + interest ) - (fee% of deposit)
            new_opening_balance = 0
            closing_balance = (float(deposit_amount) + (
                interest/100 * float(deposit_amount))) - (
                    (management_fee/100 * float(deposit_amount)) + (
                        performance_fee/100 * float(deposit_amount)))
            track = InvestmentTrack.objects.create(
                deposit_amount=deposit_amount,
                opening_balance=new_opening_balance,
                closing_balance=closing_balance,
                management_fee=management_fee,
                interest=interest,
                performance_fee=performance_fee,
                withdraw_amount=withdraw_amount,
                investment_option=InvestmentOption(
                    pk=int(investment_option_id)),
                user=User(pk=int(userid))
            )
            track.save()
            withdraw = self.getWithdrawById(request, lang, withdrawid)
            return {
                "message": f"You have successfully requested withdraw {currency} {withdraw_amount} to your {account_type} account",
                "success": True,
                "user_id": userid,
                "withdraw_id": withdrawid,
                "withdraw": withdraw,
                }
    # else:
    #     return {
    #         "message": "your account is not verified, please check your email and verify",
    #         "success": False
    #     }
        # wwithdraw = self.getWithdrawById(request, lang, withdrawid)
        # return {
        #     "message": "Your withdraw is now pending",
        #     "success": True,
        #     "user_id": userid,
        #     "withdraw_id": withdrawid,
        #     "withdraw": wwithdraw,
        #     "time withdraw was created": created
        # }

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
        account_bank = request.data["account_bank"]
        account_number = request.data["account_number"]
        # cyanase charge 0.2%
        charge_amount = float(0.2/100) * float(withdraw_amount)
        withdraw = Withdraw.objects.create(
                    withdraw_channel=withdraw_channel,
                    withdraw_amount=float(withdraw_amount),
                    currency=currency,
                    account_type=account_type,
                    user=User(pk=int(userid)),
                    investment_option=InvestmentOption(pk=11),
                    created=created,
                    status=status,
                    units=0,
                    charge_amount=charge_amount,
                    account_bank=account_bank,
                    account_number=account_number
                )
        withdrawid = withdraw.id
        withdraw.save()
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

    def getWithdrawsByInvestmentOption(self, request, lang, userid, investment_option_id):
        # withdraw_obj = []
        wwithdraws = []
        all_withdraws = []
        total_withdraw = 0
        # get all user withdraws for specific investment option
        withdraws = Withdraw.objects.filter(user_id=userid, investment_option_id=investment_option_id)
        if withdraws.exists():
            for withdraw in withdraws:
                # withdraw_obj.append({"name": withdraw.investment_option.name, "amount": withdraw.withdraw_amount, "date": withdraw.created.strftime("%d %b"), "handler": withdraw.investment_option.fund_manager.first_name + " " + withdraw.investment_option.fund_manager.last_name})
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
            return total_withdraw
            # return withdraw_obj
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
            return [], 0

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
                        "handler": withdraw.investment_option.fund_manager.first_name,
                        "created": withdraw.created.strftime("%d %b")
                    })
            return wwithdraws
        else:
            return []

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

    # with transactions transfers
    # def withdrawFromGoal(self, request, lang, goalid, user, transactionid, investment_option_id, units, withdraw_amount):
    #     withdraw_channel = request.data["withdraw_channel"]
    #     userid = request.user.id
    #     currency = request.data["currency"]
    #     account_type = request.data["account_type"]
    #     created = datetime.datetime.now()
    #     is_verified = request.user.userprofile.is_verified
    #     account_type = AccountType.objects.filter(code_name=account_type).get()
    #     status = "pending"
    #     is_active = False
    #     account_bank = request.data["account_bank"]
    #     account_number = request.data["account_number"]
    #     # cyanase charge 0.2%
    #     charge_amount = float(0.2/100) * float(withdraw_amount)
    #     # remember to verify the user
    #     if is_verified is True:
    #         # create withdraw transaction
    #         withdraw = Withdraw.objects.create(
    #             withdraw_channel=withdraw_channel,
    #             withdraw_amount=withdraw_amount,
    #             currency=currency,
    #             goal=Goal(pk=int(goalid)),
    #             account_type=account_type,
    #             user=User(pk=int(userid)),
    #             status=status,
    #             transaction=BankTransaction(pk=int(transactionid)),
    #             investment_option=InvestmentOption(pk=int(investment_option_id)),
    #             units=units,
    #             charge_amount=charge_amount,
    #             account_bank=account_bank,
    #             account_number=account_number
    #         )
    #         withdrawid = withdraw.id
    #         withdraw.save()
    #         wwithdraw = self.getWithdrawById(request, lang, withdrawid)
    #         # update goal to inactive
    #         Goal.objects.filter(pk=goalid).update(
    #             is_active=is_active
    #         )
    #         goal = Goal.objects.filter(pk=goalid).get()
    #         goalname = goal.goal
    #         goal.save()
    #         return {
    #             "message": f"You have successfully withdrawn {currency} {withdraw_amount} from goal: {goalname}",
    #             "success": True,
    #             "user_id": userid,
    #             "goal_id": goalid,
    #             "withdraw_id": withdrawid,
    #             "withdraw": wwithdraw,
    #             "time of withdraw": created
    #         }
    #     else:
    #         return {
    #             "message": "your account is not verified, please check your email and verify",
    #             "success": False
    #         }

    #without transactions transfers
    def withdrawFromGoal(self, request, lang, goalid, user, investment_option_id, units, withdraw_amount):
        withdraw_channel = request.data["withdraw_channel"]
        userid = request.user.id
        currency = request.data["currency"]
        account_type = request.data["account_type"]
        created = datetime.datetime.now()
        is_verified = request.user.userprofile.is_verified
        account_type = AccountType.objects.filter(code_name=account_type).get()
        status = "pending"
        is_active = False
        account_bank = request.data["account_bank"]
        if withdraw_channel == "mobile money":
            account_number = request.data["phone_number"]
        else:
            account_number = request.data["account_number"]
        # cyanase charge 0.2%
        charge_amount = float(0.2/100) * float(withdraw_amount)
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
                investment_option=InvestmentOption(pk=int(investment_option_id)),
                units=units,
                charge_amount=charge_amount,
                account_bank=account_bank,
                account_number=account_number
            )
            withdrawid = withdraw.id
            withdraw.save()
            wwithdraw = self.getWithdrawById(request, lang, withdrawid)
            # update goal to inactive
            Goal.objects.filter(pk=goalid).update(
                is_active=is_active
            )
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

    def getWithdrawfee(self, request, lang, userid,
                       withdraw_amount, currency, _type):
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


# class Networths:
#     def __init__(self):
#         self.help = Helper()

#     def getNetworth(self, request, lang, user):
#         totalDeposit = 0
#         userid = request.user.id
#         deposit = Deposit.objects.filter(user_id=userid)
#         for ddeposit in deposit:
#             amount = ddeposit.deposit_amount
#             totalDeposit += amount
#         return totalDeposit

#     def getGoalNetworth(self, request, lang, user):
#         # no goals networth
#         # userid = request.user.id
#         # networth = Networth.objects.filter(user_id=userid)
#         # total_networth = 0
#         # for nnetworth in networth:
#         #      total_networth += nnetworth.amount
#         # return total_networth
#         no_goals = 0
#         goals = 0
#         userid = request.user.id
#         # deposit = Deposit.objects.filter(user_id=userid)
#         networth = Networth.objects.filter(user_id=userid)
#         for nnetworth in networth:
#             goal = nnetworth
#             amount = nnetworth.amount
#             if goal.goal is None:
#                 no_goals += amount
#             else:
#                 goals += amount
#         withdraw = Withdraws.getWithdrawNetworths(Withdraws, request, lang,
# user)
#         networth = (no_goals*0.15)+no_goals
#         networths = networth - float(withdraw[1])
#         return goals, no_goals, networths


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
        ttransfer = BankTransactions.getTransferById(self, request, lang,
                                                     transferid)
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


class InvestmentClasses:
    def __init__(self):
        self.help = Helper()

    def getAllInvestmentClasses(self, request, lang, userid):
        user = User.objects.filter(pk=userid).exists()
        option = InvestmentClass.objects.all()
        investment_classes = []
        if user is True:
            for options in option:
                investment_class = options.name
                class_options = InvestmentOptions.getJustInvestmentOptionsByClass(InvestmentOptions, request, lang, userid, investment_class)
                investment_classes.append({
                    "investment_class_id": options.pk,
                    "investment_class": options.name,
                    "description": options.description,
                    "investment_options": class_options,
                    "logo": f"{webconfig.BASE_URL}media/investmentClasses/{options.logo}"
                })
            return investment_classes
        else:
            return {
                "message": "No investment classes available",
                "success": False
            }

    def getInvestmentClassesWithOptions(self, request, lang, userid):
        user = User.objects.filter(pk=userid).exists()
        option = InvestmentClass.objects.all()
        investment_classes = []
        if user is True:
            for options in option:
                investment_class = options.name
                class_options = InvestmentOptions.getJustInvestmentOptionsByClass(self, request, lang, userid, investment_class)
                if len(class_options) > 0:
                    investment_classes.append({
                        "investment_class_id": options.pk,
                        "investment_class": options.name,
                        "description": options.description,
                        "investment_options": class_options,
                        "logo": f"{webconfig.BASE_URL}media/investmentClasses/{options.logo}"
                    })
            return investment_classes
        else:
            return {
                "message": "No user available",
                "success": False
            }


class InvestmentTracks:

    def __init__(self) -> None:
        pass

    def CreateInvestmentTracks(self, request, lang):
        deposit_users = []
        withdraw_users = []
        deposits = Deposit.objects.all()
        withdraw = Withdraw.objects.all()
        # get each user deposit
        for each in deposits:
            # get users
            deposit_users.append(each.user.pk)
        for each in withdraw:
            withdraw_users.append(each.user.pk)
        for user in set(deposit_users):
            # each user deposit
            deposit = Deposit.objects.filter(user_id=user)
            withdraw = Withdraw.objects.filter(user_id=user)
            total_deposit = 0
            total_withdraw = 0
            date_updated = ""
            for each in deposit:
                total_deposit = total_deposit + each.deposit_amount
                date_updated = each.created
            for each in withdraw:
                total_withdraw = total_withdraw + each.withdraw_amount
            # risk_profile is False by default - 0
            # Real estate class for all at the time - Bombo Land, id=40
            investment_option_id = 8  # id=8, localhost, id=40
            investment_option = InvestmentOption.objects.filter(
                pk=investment_option_id)
            # interest for investment option 1
            management_fee = 2  # percntage - standard
            performance_fee = 0  # standard
            # fees are from investment performance
            investment_performance = InvestmentPerformance.objects.filter(investment_option_id=int(investment_option_id))
            for performance in investment_performance:
                management_fee = performance.management_fee
                performance_fee = performance.performance_fee
            interest = 0
            # interest from option
            for option in investment_option:
                interest = (option.interest / 100) * total_deposit
            track = InvestmentTrack.objects.create(
                deposit_amount=total_deposit,
                user=User(pk=int(user)),
                withdraw_amount=total_withdraw,
                investment_option=InvestmentOption(
                    pk=int(investment_option_id)),
                opening_balance=total_deposit,
                interest=interest,
                management_fee=management_fee,
                performance_fee=performance_fee,
                closing_balance=total_deposit,
                date_updated=date_updated
            )
            track.save()
            investment_track_id = track.pk
            track = self.getInvestmenttracksById(request, lang,
                                                 investment_track_id)
        return track

    def getAllInvestmenttracks(self, request, lang):
        tracks = []
        investment_tracks = InvestmentTrack.objects.all()
        if len(investment_tracks) != 0:
            for track in investment_tracks:
                tracks.append({
                    "user": track.user,
                    "deposit_amount": track.deposit_amount,
                    "opening_balance": track.opening_balance,
                    "interest": track.interest,
                    "closing_balance": track.closing_balance,
                    "management_fee": track.management_fee,
                    "investment_option": track.investment_option.name,
                    "performance_fee": track.performance_fee,
                    "withdraw_amount": track.withdraw_amount,
                    "date_updated": track.date_updated,
                    "created": track.created
                })
            return tracks
        else:
            return []

    def getInvestmenttracksById(self, request, lang, investments_track_id):
        tracks = []
        investment_tracks = InvestmentTrack.objects.filter(pk=int(investments_track_id))
        if len(investment_tracks) != 0:
            for track in investment_tracks:
                tracks.append({
                    "user": track.user,
                    "deposit_amount": track.deposit_amount,
                    "opening_balance": track.opening_balance,
                    "interest": track.interest,
                    "closing_balance": track.closing_balance,
                    "management_fee": track.management_fee,
                    "investment_option": track.investment_option.name,
                    "performance_fee": track.performance_fee,
                    "withdraw_amount": track.withdraw_amount,
                    "created": track.created
                })
            return tracks
        else:
            return []

    def getUserInvestmentTrack(self, request, lang, userid):
        tracks = []
        options = []
        final_ids = []
        set_ids = []
        biggest_id = 0
        # get all track records for each user
        investment_tracks = InvestmentTrack.objects.filter(user_id=int(userid))
        if len(investment_tracks) != 0:
            # user has tracks records
            # we need to get a set of all investment ids while picking out most recent track id
            for track in investment_tracks:
                # get a set of all investment option ids
                options.append(track.investment_option_id)
                set_ids = set(options)
            # for each investment id in sorted ids, get the biggest track id associated with it
            for each in set_ids:
                track_sorted_ids = []
                biggest_options = []
                # query all tracks with this investemnt id
                investment_track = InvestmentTrack.objects.filter(user_id=int(userid), investment_option_id=int(each))
                # lets get track ids as we query
                for big_id in investment_track:
                    biggest_options.append(big_id.pk)
                # get biggest id from track sorted ids
                track_sorted_ids = sorted(biggest_options)
                biggest_id = track_sorted_ids[-1]
                final_ids.append(biggest_id)
            # now lets add this track with these ids to our track list
            for each in final_ids:
                investment_recent_track = InvestmentTrack.objects.filter(pk=int(each))
                for this_track in investment_recent_track:
                    tracks.append({
                        "user": this_track.user.pk,
                        "deposit_amount": this_track.deposit_amount,
                        "withdraw_amount": this_track.withdraw_amount,
                        "opening_balance": this_track.opening_balance,
                        "closing_balance": this_track.closing_balance,
                        "investment_option": this_track.investment_option.name,
                        "fund_manager": this_track.investment_option.fund_manager.first_name + " " + this_track.investment_option.fund_manager.last_name,
                        "created": this_track.created
                    })
            return {
                "message": "user track successful",
                "success": True,
                "data": tracks
            }
        else:
            return {
                "message": "User has no tracks",
                "success": True,
                "data": []
            }

    def CreateOrtusUsersTrack(self, request, lang, user_data):
        userid = 1600  # userid
        # change model to temp remove auto datetime setting
        # json data should not have the last null dictionary
        # name of option should match database
        # if user is depositing
        if user_data["Type"] == "Investment":
            deposit_amount = user_data["AMOUNT"]
            withdraw_amount = 0
            interest = 0
            out_performance = 0
            opening_balance = 0
            created = user_data["DATE"]
            management_fee = 0
            investment_option_id = 12  # sampling with venture
            closing_balance = user_data["CLOSING BALANCE"]
            performance_fee = 0
            # upload deposit data as new rows of data
            track = InvestmentTrack.objects.create(
                deposit_amount=deposit_amount,
                user=User(pk=int(userid)),
                withdraw_amount=withdraw_amount,
                investment_option=InvestmentOption(
                    pk=int(investment_option_id)),
                opening_balance=opening_balance,
                interest=interest,
                management_fee=management_fee,
                performance_fee=performance_fee,
                closing_balance=closing_balance,
                out_performance=out_performance,
                created=created
            )
            track.save()
            investment_track_id = track.pk
            track = self.getInvestmenttracksById(request, lang,
                                                 investment_track_id)
            return track
        # if management fees start coming in,
        # we create new data rows but with previous data
        # update by year and month from description
        # first extract year and month from most recent track
        # get most recent input of this user and compare dates
        all_user_track_data = InvestmentTrack.objects.filter(user_id=userid)
        most_recent_track = []
        all_ids = []
        for data in all_user_track_data:
            # get largest track id
            all_ids.append(data.pk)
        most_recent_id = all_ids[-1]
        # get date associated here
        most_recent_track = InvestmentTrack.objects.filter(
            user_id=userid, pk=most_recent_id)
        if user_data["Type"] == "Management fees":
            date_created = 0
            deposit_amount = 0
            withdraw_amount = 0
            out_performance = 0
            performance_fee = 0
            opening_balance = 0
            investment_option_id = 12
            interest = 0
            for data in most_recent_track:
                date_created = data.created
            # compare year and month to update the right data
            # recent_year = date_created.strftime("%Y")
            # recent_month = date_created.strftime("%b")
            # check description for which month and year
            # most recent data to update
            # split description at the dash and split the right
            # hand side at the space btn month and year
            # description = user_data["DESCRIPTION"]
            # month = description.split("-")[1].split(" ")[0]
            # year = description.split("-")[1].split(" ")[1]
            # if str(month)[:3] == str(recent_month) and year == recent_year:
            created = user_data["DATE"]
            management_fee = float(str(user_data["AMOUNT"]).replace("-", ""))
            closing_balance = user_data["CLOSING BALANCE"]
            track = InvestmentTrack.objects.create(
                deposit_amount=deposit_amount,
                user=User(pk=int(userid)),
                withdraw_amount=withdraw_amount,
                investment_option=InvestmentOption(
                    pk=int(investment_option_id)),
                opening_balance=opening_balance,
                interest=interest,
                out_performance=out_performance,
                management_fee=management_fee,
                closing_balance=closing_balance,
                created=created
            )
            track.save()
            investment_track_id = track.pk
            track = self.getInvestmenttracksById(
                request, lang, investment_track_id)
            return track
        if user_data["Type"] == "Interest":
            date_created = 0
            deposit_amount = 0
            withdraw_amount = 0
            out_performance = 0
            performance_fee = 0
            opening_balance = 0
            investment_option_id = 12
            management_fee = 0
            created = user_data["DATE"]
            interest = float(str(user_data["AMOUNT"]).replace("-", ""))
            closing_balance = user_data["CLOSING BALANCE"]
            track = InvestmentTrack.objects.create(
                deposit_amount=deposit_amount,
                user=User(pk=int(userid)),
                withdraw_amount=withdraw_amount,
                investment_option=InvestmentOption(
                    pk=int(investment_option_id)),
                opening_balance=opening_balance,
                interest=interest,
                out_performance=out_performance,
                management_fee=management_fee,
                closing_balance=closing_balance,
                created=created
            )
            track.save()
            investment_track_id = track.pk
            track = self.getInvestmenttracksById(
                request, lang, investment_track_id)
            return track
        if user_data["Type"] == "Outperformance":
            deposit_amount = 0
            withdraw_amount = 0
            interest = 0
            performance_fee = 0
            opening_balance = 0
            investment_option_id = 12
            management_fee = 0
            created = user_data["DATE"]
            out_performance = float(str(user_data["AMOUNT"]).replace("-", ""))
            closing_balance = user_data["CLOSING BALANCE"]
            # update prev deposit data on new row
            track = InvestmentTrack.objects.create(
                deposit_amount=deposit_amount,
                user=User(pk=int(userid)),
                withdraw_amount=withdraw_amount,
                investment_option=InvestmentOption(
                    pk=int(investment_option_id)),
                opening_balance=opening_balance,
                interest=interest,
                out_performance=out_performance,
                management_fee=management_fee,
                closing_balance=closing_balance,
                created=created
                )
            track.save()
            investment_track_id = track.pk
            track = self.getInvestmenttracksById(
                request, lang, investment_track_id)
            return track
        if user_data["Type"] == "Liquidation":
            if user_data["DESCRIPTION"] == "Liquidation" or str(
                user_data["DESCRIPTION"])[:8] == "Interest":
                # means investment option didnt change
                # also means plain old withdraws
                deposit_amount = 0
                interest = 0
                out_performance = 0
                performance_fee = 0
                opening_balance = 0
                investment_option_id = 12
                management_fee = 0
                created = user_data["DATE"]
                withdraw_amount = float(str(user_data["AMOUNT"]).replace("-", ""))
                closing_balance = user_data["CLOSING BALANCE"]
                # update prev deposit data on new row
                track = InvestmentTrack.objects.create(
                    deposit_amount=deposit_amount,
                    user=User(pk=int(userid)),
                    withdraw_amount=withdraw_amount,
                    investment_option=InvestmentOption(
                        pk=int(investment_option_id)),
                    opening_balance=opening_balance,
                    interest=interest,
                    out_performance=out_performance,
                    management_fee=management_fee,
                    closing_balance=closing_balance,
                    created=created
                    )
                track.save()
                investment_track_id = track.pk
                track = self.getInvestmenttracksById(
                    request, lang, investment_track_id)
                return track
            else:
                # means investment option changed
                deposit_amount = 0
                interest = 0
                out_performance = 0
                performance_fee = 0
                opening_balance = 0
                # option indicated
                investment_option = str(user_data["DESCRIPTION"]).split(" to ")[1]
                investment_option_id = 12
                # get option id
                option = InvestmentOptions.getInvestmentOptionName(
                    InvestmentOptions, request, lang, userid, investment_option)
                for this_option in option:
                    # new option id
                    investment_option_id = this_option["investment_option_id"]
                management_fee = 0
                created = user_data["DATE"]
                withdraw_amount = float(str(user_data["AMOUNT"]).replace("-", ""))
                closing_balance = user_data["CLOSING BALANCE"]
                # update prev deposit data on new row
                track = InvestmentTrack.objects.create(
                    deposit_amount=deposit_amount,
                    user=User(pk=int(userid)),
                    withdraw_amount=withdraw_amount,
                    investment_option=InvestmentOption(
                        pk=int(investment_option_id)),
                    opening_balance=opening_balance,
                    interest=interest,
                    out_performance=out_performance,
                    management_fee=management_fee,
                    closing_balance=closing_balance,
                    created=created
                    )
                track.save()
                investment_track_id = track.pk
                track = self.getInvestmenttracksById(
                    request, lang, investment_track_id)
                return track
