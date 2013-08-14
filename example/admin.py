from django import forms
from django.contrib import admin

### Unregsiter  and Groups ###
from django.contrib.auth.models import Group

admin.site.unregister(Group)   # Since we don't use groups