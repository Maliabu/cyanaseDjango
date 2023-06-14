from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date


class SupportedLanguage(models.Model):
    lang_name = models.CharField(max_length=255)
    lang_iso_code = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.lang_name

#######################################


class SupportedCountry(models.Model):
    coutry_name = models.CharField(max_length=255)
    coutry_flag = models.CharField(max_length=255)
    country_code = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.coutry_name


class TimeZone(models.Model):
    country = models.ForeignKey(
        SupportedCountry, on_delete=models.CASCADE, null=True, blank=True)
    dispaly_name = models.CharField(max_length=255)
    code_name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    has_been_modified = models.BooleanField(default=False)
    last_modified = models.DateTimeField()

    def __str__(self):
        return "%s" % self.dispaly_name


class UserType(models.Model):
    type_name = models.CharField(max_length=255)
    code_name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.type_name

# User Profile


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=200, default="personal", null=True)
    # country = models.ForeignKey(SupportedCountry, on_delete=models.CASCADE, null=True, blank=True)
    country = models.CharField(max_length=200, default="uganda", null=True)
    language = models.ForeignKey(
        SupportedLanguage, on_delete=models.CASCADE, null=True, blank=True)
    tmz = models.ForeignKey(
        TimeZone, on_delete=models.CASCADE, null=True, blank=True)
    bussiness_name = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    phoneno = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=30, null=True, blank=True)
    verification_code = models.CharField(max_length=30, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=True)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.user


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class NextOfKin(models.Model):
    first_name = models.CharField(verbose_name="first name",default="first name", max_length=200)
    last_name = models.CharField(verbose_name="last name", default="last name", max_length=200)
    phone = models.IntegerField(verbose_name="phone", default="+256 000 000 000")
    email = models.EmailField(verbose_name="email", default="nextofkin@gmail.com")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "%s" % self.first_name
    

class RiskProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qn1 = models.CharField(max_length=200, default="saving", verbose_name="objectives")
    qn2 = models.CharField(max_length=200, default="less_than_year", verbose_name="horizon")
    qn3 = models.CharField(max_length=200, default="treasuries", verbose_name="past investing")
    qn4 = models.CharField(max_length=200, default="less_ten_percent", verbose_name="portfolio max loss")
    qn5 = models.CharField(max_length=200, default="least", verbose_name="capital")
    qn6 = models.CharField(max_length=200, default="employment", verbose_name="funds source")
    qn7 = models.CharField(max_length=200, default="guaranteed_returns", verbose_name="goals")
    qn8 = models.CharField(max_length=200, default="A", verbose_name="profit or loss")
    qn9 = models.CharField(max_length=200, default="no", verbose_name="risk")
    qn10 = models.CharField(max_length=200, default="no", verbose_name="future investing")
    qn11 = models.CharField(max_length=200, default="comfortable", verbose_name="inflation impact")
    created = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(verbose_name="score", default=0)
    risk_analysis = models.CharField(max_length=200, verbose_name="analysis",default="Incomplete Risk profile")
    investment_option = models.CharField(max_length=200,verbose_name="investment option", default="Tbills")
    is_complete = models.BooleanField(default=False, verbose_name="status")
    
    def __str__(self):
        return "%s" % self.user.first_name

class MerchantApp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app_name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s | %s| %s" % (str(self.user), self.app_name, self.api_key)
    
class Currency(models.Model):
    country = models.ForeignKey(
        SupportedCountry, on_delete=models.CASCADE, null=True, blank=True)
    currency_locale = models.CharField(max_length=255)
    currency_code = models.CharField(max_length=255)
    currency_symbol = models.CharField(max_length=255)
    exchange_rate = models.FloatField(max_length=500)
    is_indented = models.BooleanField(default=False)
    is_infront = models.BooleanField(default=True)
    decimal_points = models.IntegerField(default=2)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.currency_locale

# Main Application Modules


class Module(models.Model):
    module_name = models.CharField(max_length=255)
    code_name = models.CharField(max_length=255)
    route_name = models.CharField(max_length=255)
    is_a_sub_module = models.BooleanField(default=False)
    has_children = models.BooleanField(default=False)
    main_module_id = models.IntegerField(null=True, blank=True)
    sort_value = models.IntegerField()
    depth = models.IntegerField()
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.module_name

# Side Menu Modules


class SideMenu(models.Model):
    module = models.ForeignKey(Module, on_delete=models.DO_NOTHING)
    sort_value = models.IntegerField()
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.module

# Dashboard menu model


class DashboardMenu(models.Model):
    module = models.ForeignKey(Module, on_delete=models.DO_NOTHING)
    sort_value = models.IntegerField()
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.module.module_name


class NavigationMenu(models.Model):
    module = models.ForeignKey(Module, on_delete=models.DO_NOTHING)
    sort_value = models.IntegerField()
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.module.module_name


class PaymentType(models.Model):
    payment_name = models.CharField(max_length=200)
    code_name = models.CharField(max_length=200)
    payment_logo = models.CharField(max_length=200, null=True, blank=True)
    sort_value = models.IntegerField(default=0)
    has_standarded_charge = models.BooleanField(default=False)
    payment_charge = models.FloatField(default=0, blank=True, null=True)
    charge_in_percentage = models.BooleanField(default=True)
    charge_fees_on_user = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.payment_name


class PaymentMethod(models.Model):
    en_payment_method_name = models.CharField(max_length=200)
    code_name = models.CharField(max_length=200)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.en_payment_method_name


class PaymentOption(models.Model):
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.DO_NOTHING)
    en_payment_option_name = models.CharField(max_length=200)
    code_name = models.CharField(max_length=200)
    payment_option_logo = models.CharField(
        max_length=200, null=True, blank=True)
    sort_value = models.IntegerField(default=0)
    has_standarded_charge = models.BooleanField(default=False)
    payment_charge = models.FloatField(default=0, blank=True, null=True)
    charge_in_percentage = models.BooleanField(default=True)
    charge_fees_on_user = models.BooleanField(default=True)
    has_pre_inputs = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s [%s]" % (self.en_payment_option_name, self.code_name)


class PaymentOptionField(models.Model):
    payment_option = models.ForeignKey(
        PaymentOption, on_delete=models.DO_NOTHING)
    en_entry_name = models.CharField(max_length=500)
    entry_code_name = models.CharField(max_length=255)
    has_entry_value = models.BooleanField(default=False)
    entry_value = models.CharField(max_length=500, null=True, blank=True)
    is_a_float = models.BooleanField(default=False)
    is_a_int = models.BooleanField(default=False)
    is_a_string = models.BooleanField(default=True)
    is_required = models.BooleanField(default=True)
    is_default = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "[%s] %s : %s" % (str(self.payment_option), self.en_entry_name, str(self.entry_value))


class PaymentOptionSetting(models.Model):
    payment_option = models.ForeignKey(
        PaymentOption, on_delete=models.DO_NOTHING)
    en_entry_name = models.CharField(max_length=500)
    entry_code_name = models.CharField(max_length=255)
    has_entry_value = models.BooleanField(default=False)
    entry_value = models.CharField(max_length=500, null=True, blank=True)
    is_required = models.BooleanField(default=True)
    is_default = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "[%s] %s : %s" % (str(self.payment_option), self.en_entry_name, str(self.entry_value))


class PaymentOptionSupport(models.Model):
    payment_type = models.ForeignKey(PaymentType, on_delete=models.DO_NOTHING)
    payment_option = models.ForeignKey(
        PaymentOption, on_delete=models.DO_NOTHING)
    country = models.ForeignKey(SupportedCountry, on_delete=models.DO_NOTHING)
    is_disabled = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s (%s)" % (self.payment_option, self.country)


class PaymentTypeOption(models.Model):
    payment_type = models.ForeignKey(PaymentType, on_delete=models.DO_NOTHING)
    payment_option = models.ForeignKey(
        PaymentOption, on_delete=models.DO_NOTHING)
    is_disabled = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s (%s)" % (self.payment_option, self.payment_option)


class RegionalPaymentType(models.Model):
    payment_type = models.ForeignKey(PaymentType, on_delete=models.DO_NOTHING)
    country = models.ForeignKey(SupportedCountry, on_delete=models.DO_NOTHING)
    sort_value = models.IntegerField()
    is_disabled = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    has_been_modified = models.BooleanField(default=False)
    last_modified = models.DateTimeField()

    def __str__(self):
        return "%s (%s)" % (self.payment_type, self.country)


class PaymentTypeSetting(models.Model):
    payment_type = models.ForeignKey(PaymentType, on_delete=models.DO_NOTHING)
    entry_name = models.CharField(max_length=500)
    entry_code_name = models.CharField(max_length=255)
    has_entry_value = models.BooleanField(default=False)
    entry_value = models.CharField(max_length=500, null=True, blank=True)
    is_required = models.BooleanField(default=True)
    is_default = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "[%s] %s : %s" % (str(self.payment_type), self.entry_name, str(self.entry_value))


class AccountType(models.Model):
    type_name = models.CharField(max_length=200)
    code_name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    sort_value = models.IntegerField(default=0)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.type_name



class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.CharField(max_length=200, null=True)
    goal_period = models.IntegerField(default="1", null=True)
    goal_amount = models.BigIntegerField(default=0)
    deposit_type = models.CharField(max_length=200, null=True)
    deposit_reminder_day = models.CharField(max_length=200, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s - %s" % (self.user, self.goal, self.goal_amount)


class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_means = models.CharField(max_length=200, null=True)
    deposit_category = models.CharField(max_length=200, null=True)
    deposit_amount = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=200, default='UGX')
    account_type = models.ForeignKey(AccountType, on_delete=models.DO_NOTHING)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.user, self.deposit_amount)

class DepositType(models.Model):
    type_name = models.CharField(max_length=200)
    code_name = models.CharField(max_length=200)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.type_name


class DepositTime(models.Model):
    time_name = models.CharField(max_length=200)
    code_name = models.CharField(max_length=200)
    is_default = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.time_name


class Account(models.Model):
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=500)
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE)  # Default currency
    opening_balance = models.FloatField(default=0)
    account_no = models.CharField(max_length=300)
    is_operational_account = models.BooleanField(default=False)
    is_cash_account = models.BooleanField(default=False)
    is_reconcilable = models.BooleanField(default=False)
    allow_over_drafts = models.BooleanField(default=False)
    narration = models.CharField(max_length=3000, null=True, blank=True)
    is_disabled = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)
    is_deletable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.account_name


# Ledger Entries or Account Entries or Account Ledgers
class LedgerEntry(models.Model):
    ledger_no = models.IntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    entry_type = models.CharField(max_length=255)
    is_adjusting_entry = models.BooleanField(default=False)
    amount = models.FloatField(default=0)
    narration = models.CharField(max_length=5000, null=True, blank=True)
    is_disabled = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.account, self.amount)


class TopUp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topup_amount = models.BigIntegerField(default=0)
    account_type = models.ForeignKey(AccountType, on_delete=models.DO_NOTHING)
    transactioncode = models.CharField(max_length=200, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.topup_amount
