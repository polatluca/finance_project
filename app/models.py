from django.db import models
from django.contrib.auth.models import User




class Category(models.Model):
    name = models.CharField(max_length=100,unique=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Pocket(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_credit = models.FloatField(default=0.0)

class Transaction(models.Model):
    pocket = models.ForeignKey(Pocket, on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=500,blank=True,null=True)
    actuell_payment_date = models.DateField(blank=True,null=True)
    planed_payment_date = models.DateField(blank=True,null=True)
    file = models.FileField(upload_to='files/',blank=True,null=True)
    # category = models.ForeignKey(Category,on_delete=models.SET_NULL,blank=True,null=True)
    amount = models.FloatField()
    payment_recurring = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, 
                                 choices=[
                                     ('daily', 'Daily'), 
                                     ('weekly', 'Weekly'), 
                                     ('monthly', 'Monthly')
                                    ],
                                    blank=True,null=True)
    # type = models.CharField(max_length=20, 
    #                                 choices=[
    #                                     ('daily', 'Daily'), 
    #                                     ('weekly', 'Weekly'), 
    #                                     ('monthly', 'Transfar')
    #                                     ],
    #                                     blank=True,null=True)
    recurring_date = models.DateField(blank=True,null=True)# bis wann wiederkehrend zahlung
    categories = models.ManyToManyField(Category, blank=True)  # Allow multiple categories


