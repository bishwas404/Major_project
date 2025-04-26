# Register your models here
from django.contrib import admin

from .models import MCQ, Profile

admin.site.register(MCQ)
admin.site.register(Profile)