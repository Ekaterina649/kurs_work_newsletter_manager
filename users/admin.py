from django.contrib import admin
from users.forms import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','email')
