from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.forms import widgets
from django.contrib.auth.models import User
from .models import ProfileModel
from django.utils.translation import gettext_lazy as _

class LoginForm(forms.Form):
    email = forms.EmailField(widget = widgets.EmailInput(attrs = {
        'placeholder' : 'Email',
        'id' : 'typeEmailX',
        'class' : 'form-control form-control-lg',
    }))

    password = forms.CharField(validators = [MinLengthValidator(8, _('Minimum length of password should be 8!'))],widget = widgets.PasswordInput(attrs = {
        'placeholder' : _('Password'),
        'id' : 'typePasswordX',
        'class' : 'form-control form-control-lg'
    }))

    remember_me = forms.BooleanField(initial = False, required = False, widget = forms.CheckboxInput(attrs = {
        'class' : 'form-check-input',
        'id' : 'rememberMe'
    }))

    labels = {
        'email' : 'Email',
        'password' : 'Password',
        'remember_me' : _('Remember Me')
    }


class RegisterForm(forms.Form):
    username = forms.CharField(validators = [MinLengthValidator(7, _('The minimum length of username should be 7!'))],widget = widgets.TextInput(attrs = {
        'id' : 'typeUsernameX',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('Username')
    }))
    

    first_name = forms.CharField(widget = widgets.TextInput(attrs = {
        'id' : 'typeFirstNameX',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('First Name')
    }))


    last_name = forms.CharField(widget = widgets.TextInput(attrs = {
        'id' : 'typeLastNameX',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('Last Name')
    }))


    email = forms.EmailField(widget = widgets.EmailInput(attrs = {
        'id' : 'typeEmailX',
        'class' : 'form-control form-control-lg',
        'placeholder' : 'Email'
    }))


    password1 = forms.CharField(validators = [MinLengthValidator(8, _('The minimum length of password should be 8!'))],widget = widgets.PasswordInput(attrs = {
        'id' : 'typePasswordX',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('Password')
    }))


    password2 = forms.CharField(validators = [MinLengthValidator(8, _('The minimum length of password should be 8!'))],widget = widgets.PasswordInput(attrs = {
        'id' : 'typePasswordX2',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('Confirm Password')
    }))


    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if User.objects.filter(email = email).exists():
            self.add_error('email', _('The user with this email already exists!'))

        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data.get('password2', '')

        if password1 != password2:
            self.add_error('password2', _("The passwords don't match!"))

        return password2
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '')

        if User.objects.filter(username = username).exists():
            self.add_error('username', _('The user with this username already exists!'))

        return username
    

class InputEmailForm(forms.Form):
    email = forms.EmailField(widget = widgets.EmailInput(attrs = {
        'id' : 'typeEmailX',
        'class' : 'form-control form-control-lg',
        'placeholder' : 'Email'
    }))

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if not User.objects.filter(email = email).exists():
            self.add_error('email', _("User with this email doesn't exist!"))

        return email
    
class EmailVerificationForm(forms.Form):
    code = forms.CharField(max_length = 5, validators = [MinLengthValidator(5, _('The length of code must be 5!')), MaxLengthValidator(5, 'The length of code must be 5!')], widget = widgets.TextInput(attrs = {
        'id' : 'verificationCode',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('Input the code')
    }))


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EmailVerificationForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data.get('code', '')
        if self.request:
            if len(code) == 5 and code != self.request.session.get('verification_code', None):
                self.add_error(None, _('Input the code that was sent to your email!'))
                verification_attempt = self.request.session.get('verification_attempt', 0)
                verification_attempt += 1
                self.request.session['verification_attempt'] = verification_attempt

        return code
    

class ChangePasswordEmailForm(forms.Form):
    password1 = forms.CharField(validators = [MinLengthValidator(8, _('The minimum length of password should be 8!'))],widget = widgets.PasswordInput(attrs = {
        'id' : 'typePasswordX',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('New Password')
    }))


    password2 = forms.CharField(validators = [MinLengthValidator(8, _('The minimum length of password should be 8!'))],widget = widgets.PasswordInput(attrs = {
        'id' : 'typePasswordX2',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('Confirm Password')
    }))


    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data.get('password2', '')

        if password1 != password2:
            self.add_error('password2', _("The passwords don't match!"))

        return password2
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget = widgets.TextInput(attrs = {
            'class' : 'form-control form-control-lg',
            'placeholder' : _('Username')
        })

        self.fields['first_name'].widget = widgets.TextInput(attrs = {
            'class' : 'form-control form-control-lg',
            'placeholder' : _('First Name')
        })

        self.fields['last_name'].widget = widgets.TextInput(attrs = {
            'class' : 'form-control form-control-lg',
            'placeholder' : _('Last Name')
        })


class ProfileForm(forms.ModelForm):
    class Meta:
        model = ProfileModel
        fields = ('avatar',)

        error_messages = {
            'avatar' :{
                'required' : _('Input Picture!')
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['avatar'].widget = widgets.FileInput(attrs = {
            'type' : 'file',
            'class' : 'custom-file-input',
            'id' : 'customFile'
        })

        self.fields['avatar'].required = False


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(validators = [MinLengthValidator(8, _('The minim password length must be 8!'))], widget = widgets.PasswordInput(attrs = {
        'id' : 'oldPassword',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('Old Password')
    }))


    password1 = forms.CharField(validators = [MinLengthValidator(8, _('The minim password length must be 8!'))], widget = widgets.PasswordInput(attrs = {
        'id' : 'Password1',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('New Password')
    }))


    password2 = forms.CharField(validators = [MinLengthValidator(8, _('The minim password length must be 8!'))], widget = widgets.PasswordInput(attrs = {
        'id' : 'Password2',
        'class' : 'form-control form-control-lg',
        'placeholder' : _('Confirm New Password')
    }))


    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data.get('password2', '')
        
        if password1 != password2:
            self.add_error('password2', _("The passwords don't match!"))

        return password2