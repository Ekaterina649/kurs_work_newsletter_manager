from django.contrib import admin
from mailings.models import Client, Message, Mailing, Attempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email','full_name','comment')
    search_fields = ('full_name','email')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject','body')
    search_fields = ('subject',)

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'message', 'get_recipients', 'status')
    list_filter = ('start_time', 'end_time')
    readonly_fields = ('status',)

    def get_recipients(self, obj):
        return ", ".join([client.email for client in obj.recipients.all()])

    get_recipients.short_description = 'Получатели'

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('attempt_time','status','server_response','mailing',)
