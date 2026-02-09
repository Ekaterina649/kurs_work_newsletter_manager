from django import forms
from .models import Client, Message, Mailing
from django.utils import timezone

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email клиента'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия Имя Отчество'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Комментарий по клиенту'
            }),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема письма'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Текст письма'
            }),
        }


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
            'message': forms.Select(attrs={
                'class': 'form-select',
            }),
            'recipients': forms.SelectMultiple(attrs={
                'class': 'form-select',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and not user.groups.filter(name='Менеджеры').exists():
            # Обычный пользователь видит только своих клиентов
            self.fields['recipients'].queryset = Client.objects.filter(owner=user)
            # Только свои сообщения
            self.fields['message'].queryset = Message.objects.filter(owner=user)
        else:
            # Менеджер видит всех
            self.fields['recipients'].queryset = Client.objects.all()
            self.fields['message'].queryset = Message.objects.all()

    def clean_start_time(self):
        start = self.cleaned_data['start_time']
        if start < timezone.now():
            raise forms.ValidationError("Дата начала не может быть в прошлом")
        return start

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        if start and end and start >= end:
            raise forms.ValidationError("Дата начала должна быть раньше даты окончания")
