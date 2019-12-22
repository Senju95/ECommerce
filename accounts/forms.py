from django import forms
from django.contrib.auth.models import User


class GuestForm(forms.Form):
    email = forms.EmailField()


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField( widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField(
                    widget=forms.EmailInput(
                        attrs={
                            "class":"form-control", 
                            "placeholder":"Your email"
                            }
                        )
                    )
    password = forms.CharField( widget= forms.PasswordInput())
    password2 = forms.CharField(label = "Confirm password", widget=forms.PasswordInput())


    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username = username)
        if qs.exists():
            raise forms.ValidationError("User is taken!")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email = email)
        if qs.exists():
            raise forms.ValidationError("Email is taken!")
        return email

    def clean(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password != password2:
            raise forms.ValidationError("Password must match.")
        return self.cleaned_data