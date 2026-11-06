from django.contrib import admin
from .models import AttemptLog, Challenge, UsedToken

admin.site.register(AttemptLog)
admin.site.register(UsedToken)
admin.site.register(Challenge)