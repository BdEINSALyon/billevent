from django.contrib import admin
from .models import *


@admin.register(TransactionMercanet, TransactionRequest)
class BasicAdmin(admin.ModelAdmin):
    pass