from django.db import models
from chamas.models import *

# Create your models here.
class BotContribution(models.Model):
    submitted_contribution = models.TextField()
    retrieved_contribution = models.ForeignKey(Contribution,on_delete = models.CASCADE,related_name='_botrecords')
    date_created = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10,decimal_places=2)
    submitted_member = models.TextField()
    submitted_chama = models.TextField()
    retrieved_chama = models.ForeignKey(Chama,on_delete=models.SET_NULL,related_name='bot_contribution_records',  null=True, blank=True)

    def __str__(self):
        return f'{self.submitted_member} - {self.date_created}'
    


class BotFine(models.Model):
    member = models.TextField()
    amount_paid = models.DecimalField(max_digits=10,decimal_places=2)
    submitted_chama = models.TextField()
    retrieved_chama = models.ForeignKey(Chama,on_delete=models.SET_NULL,related_name='bot_fine_records',  null=True, blank=True)
    edited_fine = models.ForeignKey(FineItem,on_delete=models.SET_NULL,related_name='bot_updates',null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.member} - {self.date_created}'
    
class BotLoan(models.Model):
    member = models.TextField()
    amount_paid = models.DecimalField(max_digits=10,decimal_places=2)
    submitted_chama = models.TextField()
    retrieved_chama = models.ForeignKey(Chama,on_delete=models.SET_NULL,related_name='bot_loan_records',  null=True, blank=True)
    updated_loan = models.ForeignKey(LoanItem,on_delete=models.SET_NULL,related_name='bot_updates',null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.member} - {self.date_created}'
