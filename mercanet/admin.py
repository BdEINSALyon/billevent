from django.contrib import admin
from .models import *


@admin.register(TransactionMercanet, TransactionRequest, MercanetToken)
class BasicAdmin(admin.ModelAdmin):
    pass