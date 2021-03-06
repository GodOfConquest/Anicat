
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import ugettext_lazy as _
from anime.utils.misc import username_for_email, generate_password, mail


class UserCreationFormMail(forms.ModelForm):
    error_messages = {
        'duplicate_email': _("This email is already in use."),
    }

    email = forms.EmailField(label=_("E-mail address"))

    def __init__(self, *args, **kwargs):
        super(UserCreationFormMail, self).__init__(*args, prefix='register', **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.filter(email=email)
        if users.count() > 0:
            raise forms.ValidationError(self.error_messages['duplicate_email'])
        return email

    def save(self, commit=True):
        user = super(UserCreationFormMail, self).save(commit=False)
        password = generate_password()
        self.cleaned_data['password1'] = password
        user.set_password(password)
        user.username = username = username_for_email(self.cleaned_data["email"])
        if commit:
            user.save()
            mail(user.email, {'username': username, 'password': password},
                'anime/user/welcome.txt', 'anime/user/registred_email.html')
        return user

    class Meta:
        model = User
        fields = ('email', )


class UserNamesForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class UserEmailForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', )


class NotActivePasswordResetForm(PasswordResetForm):
    error_messages = {
        'unknown': _("That e-mail address doesn't have an associated "
                "user account. Are you sure you've registered?"),
        'unusable': _("The user account associated with this e-mail "
                "address cannot reset the password."),
    }

    def clean_email(self):
        email = self.cleaned_data["email"]
        self.users_cache = User.objects.filter(email__iexact=email)
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        if any((user.password == UNUSABLE_PASSWORD_PREFIX)
                for user in self.users_cache):
            raise forms.ValidationError(self.error_messages['unusable'])
        return email


class NotActiveAuthenticationForm(AuthenticationForm):
    error_messages = {
        'wrong': _("Please enter a correct username and password. Note that both fields are case-sensitive."),
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise ValidationError(self.error_messages['wrong'])
        return self.cleaned_data
