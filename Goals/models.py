# models.py
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='User')
    SAVING_TYPES = (
        ('regular', 'Regular Saving'),
        ('fixed', 'Fixed Saving'),
    )

    name = models.CharField(max_length=1000, blank=True, null=True)
    is_active = models.CharField(max_length=100, default='Yes')
    saving_type = models.CharField(max_length=10, choices=SAVING_TYPES)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_to_save_per_notification = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    target_months = models.PositiveIntegerField(blank=True, null=True)
    reminder_frequency = models.CharField(max_length=10, choices=(
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),
    ), blank=True, null=True)
    payment_frequency = models.CharField(max_length=10, choices=(
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),
    ), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    notification_date = models.DateField(blank=True, null=True)
    goal_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    goal_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def percentage(self):
        try:
            percentage = (self.goal_balance / self.goal_amount) * 100
            if percentage>100:
                return 100
            return int(percentage)
        except:
            return 0

    def calculate_month_difference(self):
        if self.end_date:
            today = timezone.now().date()
            difference = self.end_date - today
            print('Line no 53 at model is:',difference.days)
            #total_months = difference.days
            if difference.days > 0:
                return difference.days
            else:
                return 0


        return 0

class Deposit(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='deposits')
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_withdraw = models.CharField(max_length=10, blank=True, null=True,default= 'No')
    deposit_date = models.DateTimeField(default=timezone.now)

    def calculate_future_value(self):
        # Get the user's wallet
        now = timezone.now()
        interest_value = Interest_Rate.objects.get(pk=1)
        interest_rate = Decimal(0.0)
        if self.goal.saving_type == 'fixed':
            interest_rate = interest_value.fixed_deposit
        if self.goal.saving_type == 'regular':
            interest_rate = interest_value.regular_deposit
        daily_interest_rate = Decimal(interest_rate) / 365


        delta = relativedelta(now, self.deposit_date)

        # Calculate the total months elapsed using floating-point division
        days_difference = delta.years * 365 + delta.months * 30 + delta.days


        # Calculate the future value using Decimal type for more accuracy
        future_value = self.amount * (1 + daily_interest_rate) ** Decimal(days_difference)




        return round(Decimal(future_value)-(self.amount),2)

class Goal_Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    goal_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saving_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saving_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    group_goal_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)





class ExpressSaving(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    evaluation_date = models.DateField(blank=True, null=True)
    is_withdraw = models.CharField(max_length=100, blank=True, null=True)

    # def calculate_future_value_express_saving(self):
    #     # Get the user's wallet
    #     now = timezone.now()
    #     #wallet, _ = Goal_Wallet.objects.get_or_create(user=self.user)
    #
    #     delta = relativedelta(timezone.now(), self.created_at)
    #
    #     # Calculate the total months elapsed
    #     months_difference = delta.years * 12 + delta.months
    #     print('Months difference is:',months_difference)
    #
    #     future_value = self.amount * (1 + Decimal(0.06)) ** Decimal(months_difference/12*12)
    #     print('Line no 67', self.amount, months_difference,future_value)
    #
    #     # fv=1000*(1+0.06/12) ** (1/12*12) + 2000*(1+0.06/12) ** (3/12*12) + 1500*(1+0.06/12) ** (6/12*12) + 2500*(1+0.06/12) ** (9/12*12) + 2000*(1+0.06/12) ** (12/12*12)
    #     #
    #     # print('TESTED FV:',fv)
    #
    #
    #     # Update the user's saving_balance in the wallet
    #     # wallet.saving_balance += future_value
    #     # wallet.save()
    #
    #     return Decimal(future_value)-self.amount

    def calculate_future_value_express_saving(self):
        # Get the user's wallet
        now = timezone.now()
        interest_value = Interest_Rate.objects.get(pk=1)


        delta = relativedelta(now, self.created_at)

        # Calculate the total months elapsed using floating-point division
        days_difference = delta.years * 365 + delta.months * 30 + delta.days
        daily_interest_rate = Decimal(interest_value.regular_deposit) / 365


        # Calculate the future value using Decimal type for more accuracy
        future_value = self.amount * (1 + daily_interest_rate) ** Decimal(days_difference)




        return Decimal(future_value)-(self.amount)



class GroupGoal(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_goals')
    SAVING_TYPES = (
        ('regular', 'Regular Saving'),
        ('fixed', 'Fixed Saving'),
    )
    end_date = models.DateField(blank=True,null=True)
    start_date = models.DateField(blank=True,null=True)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    achieved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    saving_type = models.CharField(max_length=10, choices=SAVING_TYPES)
    goal_name = models.CharField(max_length=100, blank=True,null=True)
    goal_description = models.CharField(max_length=100, blank=True,null=True)
    shareable_link = models.CharField(max_length=100, blank=True,null=True)
    is_active = models.CharField(max_length=100, default='Yes')
    reminder_frequency = models.CharField(max_length=10, choices=(
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),
    ), blank=True, null=True)
    payment_frequency = models.CharField(max_length=10, choices=(
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),
    ), blank=True, null=True)
    status = models.CharField(max_length=20, choices=(('ongoing', 'Ongoing'), ('achieved', 'Achieved')), default='ongoing')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.creator.username}'s Group Goal - {self.target_amount}"

    def percentage(self):
        try:
            percentage = (float(self.achieved_amount) / float(self.target_amount)) * 100
            if percentage>100:
                return 100
            print('Line no 192 from model is:',percentage)
            return int(percentage)

        except Exception as e:
            print('Exception at 196 is:',e)

            return 0

    def calculate_month_difference(self):
        if self.end_date:
            today = timezone.now().date()
            difference = self.end_date - today
            print('Line no 210 at model is:', difference.days)
            # total_months = difference.days
            if difference.days > 0:
                return difference.days
            else:
                return 0
        return 0

class GroupGoalMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group_goal = models.ForeignKey(GroupGoal, on_delete=models.CASCADE)
    #contribution_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.group_goal}"
class GroupGoalActivites(models.Model):

    group_goal = models.ForeignKey(GroupGoal, on_delete=models.CASCADE)
    #contribution_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    content = models.CharField(max_length=1000, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,  null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.group_goal}"


class GroupGoalMember_contribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group_goal = models.ForeignKey(GroupGoal, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    created_at = models.DateTimeField(auto_now_add=True,editable=True)
    evaluation_date = models.DateField(blank=True, null=True)
    is_withdraw = models.CharField(max_length=10, blank=True, null=True, default='No')

    def __str__(self):
        return f"{self.user.username} - {self.group_goal}"
    def calculate_future_value_group_goal(self):
        # Get the user's wallet
        now = timezone.now()


        delta = relativedelta(now, self.created_at)
        interest_value = Interest_Rate.objects.get(pk=1)

        # Calculate the total months elapsed using floating-point division
        days_difference = delta.years * 365 + delta.months * 30 + delta.days
        daily_interest_rate = Decimal(interest_value.fixed_deposit) / 365

        total_amount = 0.0
        # Calculate the future value using Decimal type for more accuracy
        future_value = self.amount * (1 + daily_interest_rate) ** Decimal(days_difference)
        total_amount += Decimal(future_value) - (self.amount)




        return round(total_amount, 2)


class Interest_Rate(models.Model):

    regular_deposit = models.DecimalField(max_digits=10, decimal_places=2,default=0.06)
    fixed_deposit= models.DecimalField(max_digits=10, decimal_places=2,default=0.08)

    def percent_regular_deposit(self):
        return round(self.regular_deposit*100,2)
    def percent_fixed_deposit(self):
        return round(self.fixed_deposit*100,2)
class tax_Rate(models.Model):

    tax_rate_value = models.DecimalField(max_digits=10, decimal_places=2,default=0.20)


