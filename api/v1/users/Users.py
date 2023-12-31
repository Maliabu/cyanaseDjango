from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, HttpResponse
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from datetime import datetime
from django.core.validators import validate_email
from django.core.paginator import Paginator
from django.utils import timezone
from api.helper import helper
from api.config import webconfig
# from ...config import webconfig
from api.v1.mailer.Mailer import Mailer
from api.v1.locale.Locale import Locale
from api.models import *
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth.models import User
import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from ...models import UserProfile
from django.urls import resolve, reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from api.helper.Cryptor import Cryptor
import os
import random

# master module class
# master module class
class Users:
    def __init__(self):
        self.help = helper.Helper()
        self.locale = Locale()
        self.mailer = Mailer()
        self.cryptor = Cryptor()

    def getAuthUser(self, request, lang):
        userid = Token.objects.get(key=request.auth).user_id
        user = User.objects.get(pk=userid)
        profile = UserProfile.objects.get(user=User(pk=userid))
        return {
            "token": str(request.auth),  # None
            "user_id": user.pk,
            "username": user.username,  # `django.contrib.auth.User` instance.
            "email": user.email,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile": {
                "profile_id": user.pk,
                "country": profile.country,
                # "country":  None if profile.country == None else profile.country.pk,
                "language": None if profile.language == None else profile.language.pk,
                "time_zone": None if profile.tmz == None else profile.tmz.pk,
                "gender": profile.gender,
                "phoneno": profile.phoneno,
                "user_type": profile.user_type,
                "address": profile.address,
                "birth_date": profile.birth_date,
                "profile_picture": f"{webconfig.BASE_URL}media/profile/{profile.profile_picture}",
                "verification_code": profile.verification_code,
                "is_verified": profile.is_verified,
                "is_deletable": profile.is_verified,
                "is_disabled": profile.is_disabled,
                "created": profile.created,
            },
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
            "message": "",
            "success": True,
        }

    def getAuthUserById(self, request, lang, userid):
        user = User.objects.get(pk=userid)
        profile = UserProfile.objects.get(user=User(pk=userid))
        token, created = Token.objects.get_or_create(user=user)
        return {
            "token": str(token.key),  # None
            "user_id": user.pk,
            "username": user.username,  # `django.contrib.auth.User` instance.
            "email": user.email,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile": {
                "profile_id": user.pk,
                "country": profile.country,
                # "country":  None if profile.country == None else profile.country.pk,
                "language": None if profile.language == None else profile.language.pk,
                "time_zone": None if profile.tmz == None else profile.tmz.pk,
                "gender": profile.gender,
                "phoneno": profile.phoneno,
                "address": profile.address,
                "birth_date": profile.birth_date,
                "profile_picture": f"{webconfig.API_URL}media/profile/{profile.profile_picture}",
                "verification_code": profile.verification_code,
                "is_verified": profile.is_verified,
                "is_deletable": profile.is_verified,
                "is_disabled": profile.is_disabled,
                "created": profile.created,
            },
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
            "message": "",
            "success": True,
        }

    def getAuthUserByEmail(self, request, lang, email):
        user = User.objects.get(email=email)
        profile = UserProfile.objects.get(user=User(pk=user.pk))
        return {
            "token": str(request.auth),  # None
            "user_id": user.pk,
            "username": user.username,  # `django.contrib.auth.User` instance.
            "email": user.email,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile": {
                "profile_id": user.pk,
                "country": profile.country,
                # "country":  None if profile.country == None else profile.country.pk,
                "language": None if profile.language == None else profile.language.pk,
                "time_zone": None if profile.tmz == None else profile.tmz.pk,
                "gender": profile.gender,
                "phoneno": profile.phoneno,
                "address": profile.address,
                "birth_date": profile.birth_date,
                "profile_picture": f"{webconfig.API_URL}media/profile/{profile.profile_picture}",
                "verification_code": profile.verification_code,
                "is_verified": profile.is_verified,
                "is_deletable": profile.is_verified,
                "is_disabled": profile.is_disabled,
                "created": profile.created,
            },
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
            "message": "",
            "success": True,
        }
        
    def getAuthUserByEmailReset(self, request, lang, email):
        user = User.objects.get(email=email)
        profile = UserProfile.objects.get(user=User(pk=user.pk))
        return {
            # "token": str(request.auth),  # None
            "user_id": user.pk,
            "username": user.username,  # `django.contrib.auth.User` instance.
            "email": user.email,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile": {
                "profile_id": user.pk,
                "country": profile.country,
                # "country":  None if profile.country == None else profile.country.pk,
                "language": None if profile.language == None else profile.language.pk,
                "time_zone": None if profile.tmz == None else profile.tmz.pk,
                "gender": profile.gender,
                "phoneno": profile.phoneno,
                "address": profile.address,
                "birth_date": profile.birth_date,
                "profile_picture": f"{webconfig.API_URL}media/profile/{profile.profile_picture}",
                "verification_code": profile.verification_code,
                "is_verified": profile.is_verified,
                "is_deletable": profile.is_verified,
                "is_disabled": profile.is_disabled,
                "created": profile.created,
            },
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
            "message": "",
            "success": True,
        }

    def DirectLoginUser(self, request, lang, username):
        users = User.objects.filter(Q(username=username) | Q(email=username))
        if users.exists():
            user = users.get()
            return self.getAuthUserById(request, lang, user.pk)
        else:
            return {"message": "Invalid login credentials", "success": False}

    #########################################
    def getAllUsers(self, request, lang):
        results = []
        User = get_user_model()
        users = User.objects.all()
        User.objects.update(
            is_active = True
        )
        for user in users:
            userid = user.pk
            profile = UserProfile.objects.get(user=User(pk=userid))
            results.append(
                {
                    "token": str(request.auth),  # None
                    "user_id": user.pk,
                    "username": user.username,  # `django.contrib.auth.User` instance.
                    "email": user.email,
                    "is_superuser": user.is_superuser,
                    "last_login": user.last_login,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile": {
                        "profile_id": user.pk,
                        "country": profile.country,
                        # "country":  None if profile.country == None else profile.country.pk,
                        "language": None
                        if profile.language == None
                        else profile.language.pk,
                        "time_zone": None if profile.tmz == None else profile.tmz.pk,
                        "gender": profile.gender,
                        "phoneno": profile.phoneno,
                        "address": profile.address,
                        "birth_date": profile.birth_date,
                        "profile_picture": f"{webconfig.API_URL}media/profile/{profile.profile_picture}",
                        "verification_code": profile.verification_code,
                        "is_verified": profile.is_verified,
                        "is_deletable": profile.is_verified,
                        "is_disabled": profile.is_disabled,
                        "created": profile.created,
                    },
                    "is_staff": user.is_staff,
                    "is_active": user.is_active,
                    "date_joined": user.date_joined,
                    "message": "",
                    "success": True,
                }
            )
        return results
    
    def getAllUsersEmails(self, request, lang):
        results = []
        User = get_user_model()
        users = User.objects.all()
        for user in users:
            results.append(
                user.email
            )
        return results

    #################################################
    def accountExists(self, request, username, lang):
        user = User.objects.filter(Q(username=username) | Q(email=username))
        if user.exists():
            return True
        else:
            return False

    def userExistsById(self, request, lang, id):
        user = User.objects.filter(pk=int(id))
        if user.exists():
            return True
        else:
            return False

    def isVerificationTokenValid(self, request, lang, id, token):
        print(token)
        user_prof = UserProfile.objects.filter(user=User(pk=int(id))).filter(
            verification_code=token
        )
        if user_prof.exists():
            return True
        else:
            return False

    def isAccounVerified(self, request, lang, userid, token):
        user_prof = (
            UserProfile.objects.filter(user=User(pk=int(userid)))
            .filter(verification_code=token)
            .filter(is_verified=True)
        )
        if user_prof.exists():
            return True
        else:
            return False
        
    def isUserAccountVerified(self, request, lang, id):
        user_prof = (
            UserProfile.objects.filter(user=User(pk=int(id)))
            .filter(is_verified=True)
        )
        if user_prof.exists():
            return True
        else:
            return False

    def isAccounVerifiedByID(self, request, lang, userid):
        user_prof = UserProfile.objects.filter(user=User(pk=userid)).filter(
            is_verified=True
        )
        if user_prof.exists():
            return True
        else:
            return False

    def emailExists(self, request, lang, email):
        user = User.objects.filter(email=email)
        if user:
            return True
        else:
            return False

    def emailIsVerified(self, request, lang, email):
        user = self.emailExists(request, lang, email)
        if user:
            get_user = self.getAuthUserByEmail(request, lang, email)
            user_id = get_user["user_id"]
            profile = UserProfile.objects.filter(user_id=user_id)
            for profiles in profile:
                is_verified = profiles.is_verified
                if is_verified is True:
                    return True
                else:
                    return False
        else:
            return False

    def resendVerificationEmail(self, request, lang, email):
        user = self.emailExists(request, lang, email)
        if user:
            get_user = self.getAuthUserByEmail(request, lang, email)
            userid = get_user["user_id"]
            user = self.getAuthUserById(request, lang, userid)
            current_site = get_current_site(request)
            profile = UserProfile.objects.filter(user_id=userid)
            for profiles in profile:
                verificationcode = profiles.verification_code
            ###############
            encrypted_verification_code = self.cryptor.encrypt(verificationcode)
            encrypted_userid = self.cryptor.encrypt(userid)
            content = self.mailer.getEMailTemplateContent(
                "verify_account_email_template.html",
                {
                    "user": user,
                    "encrypted_verification_code": encrypted_verification_code,
                    "encrypted_userid": encrypted_userid,
                    "verificationcode": verificationcode,
                    "domain": current_site,
                },
            )
            #######################################
            self.mailer.sendHTMLEmail(email, "Please verify your account", content)
            return {
                "message": "Verification Email sent",
                "success": True
            }
        else:
            return {
                "message": "User doesnot exist",
                "success": False
            }

    def phoneExists(self, request, lang, phoneno):
        user_prof = UserProfile.objects.filter(phoneno=phoneno)
        if user_prof:
            return True
        else:
            return False

    def createAuthUser(self, request, lang):
        current_datetime = datetime.datetime.now()
        # allusers = User.objects.all().count()
        ##########################
        first_name = request.data["first_name"]
        email = request.data["email"]
        if email:
            username = email
        # pkg_id = request.data["pkg_id"]
        last_name = request.data["last_name"]
        password = request.data["password"]
        # confirmpassword = request.data["confirmpassword"]
        #### profile
        # default_language = self.locale.getDefaultLanguages(request, lang)
        profile = request.data["profile"]
        gender = profile["gender"]
        birth_date = profile["birth_date"]
        country = profile["country"]
        # PROFILE
        profile = request.data["profile"]
        gender = profile["gender"]
        phoneno = profile["phone_no"]
        birth_date = profile["birth_date"] if profile["birth_date"] else None
        profile_picture = "default_picture.jpg"
        verificationcode = str(self.help.getRandom())
        # package = self.package.getPackageByCodeName(request, lang, "free")
        # defaultpkgid = package["id"]
        # defaultlangid = default_language["id"]
        # create user
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = False
        user.is_staff = False
        user.is_active = True
        user.save()
        # get saved user
        userid = user.pk
        # Get the user add update the available profile data
        uuser = User.objects.get(pk=userid)
        uuser.userprofile.gender = None if not gender else gender
        uuser.userprofile.phoneno = None if not phoneno else phoneno
        uuser.userprofile.birth_date = None if not birth_date else birth_date
        uuser.userprofile.country = None if not country else country
        # uuser.userprofile.country = None if not str(country) else SupportedCountry(pk=int(country))
        # uuser.userprofile.package = Package(pk=int(defaultpkgid))
        # uuser.userprofile.language = SupportedLanguage(pk=int(defaultlangid))
        uuser.userprofile.verification_code = verificationcode
        uuser.userprofile.profile_picture = profile_picture
        uuser.userprofile.last_modified = current_datetime
        uuser.save()
        # get Token
        #############
        user = self.getAuthUserById(request, lang, userid)
        current_site = get_current_site(request)
        ###############
        encrypted_verification_code = self.cryptor.encrypt(verificationcode)
        encrypted_userid = self.cryptor.encrypt(userid)
        content = self.mailer.getEMailTemplateContent(
            "verify_account_email_template.html",
            {
                "user": user,
                "encrypted_verification_code": encrypted_verification_code,
                "encrypted_userid": encrypted_userid,
                "verificationcode": verificationcode,
                "domain": current_site,
            },
        )
        #######################################
        self.mailer.sendHTMLEmail(email, "Please verify your account", content)
        return {
            "message": f"Your Account has been created successfuly, please take time and verify it with the link sent to {email} or use verification code {verificationcode}",
            "success": True,
            "user": user,
            "verificationcode": verificationcode,
        }

    def createApiUser(self, request, lang):
        current_datetime = datetime.datetime.now()
        # allusers = User.objects.all().count()
        first_name = request.data["first_name"]
        email = request.data["email"]
        if email:
            username = email
        last_name = request.data["last_name"]
        password = request.data["password"]
        company_category = request.data["company_category"]
        user_type = request.data["user_type"]
        country = request.data["country"]
        phoneno = request.data["phone"]
        logo = "default_logo.jpg"
        verificationcode = str(self.help.getRandom())
        # create user
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = False
        user.is_staff = False
        user.is_active = True
        user.save()
        # get saved user
        userid = user.pk
        moa = request.data["moa"]
        if moa:
            name = "moa"
            self.UploadProfileFiles(request, lang, userid, name, moa)
        coi = request.data["coi"]
        if coi:
            name = "coi"
            self.UploadProfileFiles(request, lang, userid, name, coi)
        # Get the user add update the available profile data
        uuser = User.objects.get(pk=userid)
        uuser.userprofile.company_category = None if not company_category else company_category
        uuser.userprofile.phoneno = None if not phoneno else phoneno
        uuser.userprofile.user_type = None if not user_type else user_type
        uuser.userprofile.country = None if not country else country
        uuser.userprofile.verification_code = verificationcode
        uuser.userprofile.logo = logo
        uuser.userprofile.last_modified = current_datetime
        uuser.userprofile.moa = moa
        uuser.userprofile.coi = coi
        uuser.userprofile.website = last_name
        uuser.save()
        # get Token
        #############
        user = self.getAuthUserById(request, lang, userid)
        current_site = get_current_site(request)
        ###############
        encrypted_verification_code = self.cryptor.encrypt(verificationcode)
        encrypted_userid = self.cryptor.encrypt(userid)
        content = self.mailer.getEMailTemplateContent(
            "verify_account_email_template.html",
            {
                "user": user,
                "encrypted_verification_code": encrypted_verification_code,
                "encrypted_userid": encrypted_userid,
                "verificationcode": verificationcode,
                "domain": current_site,
            },
        )
        #######################################
        self.mailer.sendHTMLEmail(email, "Please verify your account", content)
        return {
            "message": f"Your Account has been created successfuly, please take time and verify it with the link sent to {email} or use verification code {verificationcode}",
            "success": True,
            "user": user,
            "verificationcode": verificationcode,
        }
    
    def UpdateUserPhoneNumber(self, request, lang, userid, phone_number):
        UserProfile.objects.filter(user=User(pk=int(userid))).update(
            phoneno=phone_number
        )
        
    def UpdateProfilePhoto(self, request, lang, userid, filename):
        # name = filename.name
        name_id = str(random.random())
        user_id = str(userid)
        output = 'profile_picture'+user_id+name_id+'.jpg'
        #########################
        # let us first delete the other photos of this user before updating a new one
        old_profile_pictures = UserProfile.objects.filter(user=User(pk=int(userid))).get()
        old_picture = old_profile_pictures.profile_picture
        old_picture_name = old_picture.name
        if old_picture_name != "default_picture.jpg":
            ######### remove old picture
            os.remove('media/profile/'+old_picture_name)
            destination = open('media/profile/'+output, 'wb+')
            for chunk in filename.chunks():
                destination.write(chunk)
            destination.close()
            UserProfile.objects.filter(user=User(pk=int(userid))).update(
                profile_picture=output
            )
        else:
            destination = open('media/profile/'+output, 'wb+')
            for chunk in filename.chunks():
                destination.write(chunk)
            destination.close()
            UserProfile.objects.filter(user=User(pk=int(userid))).update(
                profile_picture=output
            )

    def UploadProfileFiles(self, request, lang, userid, fieldname, filename):
        api_user = User.objects.get(pk=userid)
        name_id = api_user.first_name
        output = fieldname+name_id+'.pdf'
        destination = open('media/file/'+output, 'wb+')
        for chunk in filename.chunks():
            destination.write(chunk)
        destination.close()
        if fieldname == "moa":
            UserProfile.objects.filter(user=User(pk=int(userid))).update(
                moa=output
            )
        else:
            UserProfile.objects.filter(user=User(pk=int(userid))).update(
                coi=output
            )

    def ResendVerificationCode(self, request, lang, email):
        verificationcode = str(self.help.getRandom())
        user = self.getAuthUserByEmail(request, lang, email)
        userid = user["user_id"]
        verification_link = (
            f"{webconfig.WEB_APP_URL}auth/{userid}/verify/?code={verificationcode}"
        )
        content = self.mailer.getEMailTemplateContent(
            "verify_account_email_template.html",
            {
                "verification_link": verification_link,
                "user": user,
                "verificationcode": verificationcode,
            },
        )
        if self.mailer.sendHTMLEmail(email, "Please verify your account", content):
            user = UserProfile.objects.filter(user=User(pk=int(user["user_id"])))
            user.update(verificationcode=verificationcode)
            return {
                "message": f"A verification code has been send to {email}, please check your inbox or spam emails",
                "success": True,
            }
        else:
            return {
                "message": f"Something went wrong and we failed to send your emnail, please try again laiter",
                "success": False,
            }

    def InitPasswordReset(self, request, lang, email):
        verificationcode = str(self.help.getRandom())
        user = self.getAuthUserByEmail(request, lang, email)
        userid = user["user_id"]
        encrypted_verification_code = self.cryptor.encrypt(verificationcode)
        encrypted_userid = self.cryptor.encrypt(userid)
        content = self.mailer.getEMailTemplateContent(
            "password_reset_email_template.html",
            {
                "user": user,
                "encrypted_verification_code": encrypted_verification_code,
                "encrypted_userid": encrypted_userid,
                "email":email
            },
        )
        if self.mailer.sendHTMLEmail(email, "Password Reset", content):
            self.updateUserVerificationToken(
                request, lang, int(user["user_id"]), verificationcode
            )
            return {
                "message": f"A password reset link and code has been sent to {email}, please check your Email inbox or spam",
                "success": True,
            }
        else:
            return {
                "message": f"Something went wrong and we failed to send your email, please try again laiter",
                "success": False,
            }

    def updateUserVerificationToken(self, request, lang, userid, verificationcode=None):
        verificationcode = (
            str(self.help.getRandom())
            if (verificationcode == None)
            else verificationcode
        )
        user = UserProfile.objects.filter(user=User(pk=userid))
        user.update(verification_code=verificationcode)

    def VerifyAccount(self, request, lang, id, token):
        UserProfile.objects.filter(user=User(pk=int(id))).filter(
            verification_code=token
        ).update(is_verified=True)
        return True

    def UpdateAuthUser(self, request, lang, userid, data):
        current_datetime = datetime.datetime.now()
        old_user = User.objects.filter(pk=userid).get()
        old_usergroup = UserGroup.objects.filter(user=User(pk=userid)).get()
        # print(idzerofilling)
        username = data["username"] if data["username"] else old_user.username
        first_name = data["first_name"] if data["first_name"] else old_user.first_name
        email = data["email"] if data["email"] else old_user.email
        last_name = data["last_name"] if data["last_name"] else old_user.last_name
        is_staff = data["is_staff"] if str(data["is_staff"]) else old_user.is_staff
        is_superuser = (
            data["is_superuser"] if str(data["is_superuser"]) else old_user.is_superuser
        )
        is_active = data["is_active"] if str(data["is_active"]) else old_user.is_active
        # PROFILE
        profile_id = data["profile_id"]
        gender = data["gender"] if data["gender"] else old_user.userprofile.gender
        phoneno = data["phoneno"] if data["phoneno"] else old_user.userprofile.phoneno
        title = data["title"] if data["title"] else old_user.userprofile.title
        bio = data["bio"] if data["bio"] else old_user.userprofile.bio
        location = (
            data["location"] if data["location"] else old_user.userprofile.location
        )
        birth_date = (
            data["birth_date"]
            if data["birth_date"]
            else old_user.userprofile.birth_date
        )
        profile_picture = (
            data["profile_picture"]
            if data["profile_picture"]
            else old_user.userprofile.profile_picture
        )
        usignature = (
            data["usignature"]
            if data["usignature"]
            else old_user.userprofile.usignature
        )
        security_group_id = (
            data["security_group_id"]
            if str(data["security_group_id"])
            else old_usergroup.security_group.pk
        )
        uuser = User.objects.get(pk=userid)
        uuser.username = username
        uuser.first_name = first_name
        uuser.email = email
        uuser.last_name = last_name
        uuser.is_staff = is_staff
        uuser.is_superuser = is_superuser
        uuser.is_active = is_active
        uuser.userprofile.has_been_modified = True
        uuser.userprofile.gender = gender
        uuser.userprofile.phoneno = phoneno
        uuser.userprofile.title = title
        uuser.userprofile.bio = bio
        uuser.userprofile.location = location
        uuser.userprofile.birth_date = birth_date
        uuser.userprofile.profile_picture = profile_picture
        uuser.userprofile.last_modified = current_datetime
        uuser.save()
        # create user
        usergroup = UserGroup.objects.filter(user=User(pk=userid))
        usergroup.update(
            security_group=SecurityGroup(pk=security_group_id),
            has_been_modified=True,
            last_modified=current_datetime,
        )
        return True

    def UpdateAuthUserPassword(self, request, lang, password, userid):
        password = make_password(str(password))
        old_user = User.objects.filter(pk=userid)
        old_user.update(password=password)
        return True

    def DeleteAccount(self, request, lang):
        userid = Token.objects.get(key=request.auth).user_id
        user = User.objects.get(pk=userid)
        user.delete()
        return True
    
    def onboardUsers(self, request, lang, user):
        current_datetime = user["profile"]["created"]
        first_name = user["first_name"]
        email = user["email"]
        username = user["email"]
        last_name = user["last_name"]
        password = user["password"]
        is_deleted = False
        is_verified = user["profile"]["is_verified"]
        gender = user["profile"]["gender"]
        birth_date = user["profile"]["birth_date"]
        country = user["profile"]["country"]
        gender = user["profile"]["gender"]
        phoneno = user["profile"]["phoneno"]
        profile_picture = "photo.png"
        users = User.objects.create_user(username, email, password)
        users.first_name = first_name
        users.last_name = last_name
        users.is_superuser = False
        users.is_staff = False
        users.is_active = True
        users.save()
        userid = users.pk
        uuser = User.objects.get(pk=userid)
        uuser.userprofile.gender = None if not gender else gender
        uuser.userprofile.phoneno = None if not phoneno else phoneno
        uuser.userprofile.birth_date = None if not birth_date else birth_date
        uuser.userprofile.country = None if not country else country
        uuser.userprofile.profile_picture = profile_picture
        uuser.userprofile.last_modified = current_datetime
        uuser.userprofile.is_verified = is_verified
        uuser.userprofile.is_deleted = is_deleted
        uuser.save()
        userss = self.getAuthUserById(request, lang, userid)
        return {
            "message": f"user has been added",
            "success": True,
            "user": userss
        }
