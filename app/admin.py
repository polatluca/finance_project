from django.contrib import admin
from .models import Category, Transaction,Pocket



admin.site.register(Pocket)
admin.site.register(Transaction)
admin.site.register(Category)

