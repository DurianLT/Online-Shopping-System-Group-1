from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from users.models import Address  # Import Address model
from django.contrib.auth import authenticate
from users.models import CustomUser  # Import custom user model

CustomUser = get_user_model()  # Get the custom user model

class CustomUserCreationForm(forms.ModelForm):
    first_name = forms.CharField(label="First Name", max_length=150, required=False)
    last_name = forms.CharField(label="Last Name", max_length=150, required=False)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    shipping_address = forms.CharField(
        label="Shipping Address",
        widget=forms.Textarea,
        required=True,
        error_messages={"required": "Shipping address is required."}
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. Please use a different email.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose a different username.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise ValidationError("The passwords do not match. Please re-enter them.")
        if password1 and password1 == self.cleaned_data.get('username'):
            raise ValidationError("Your password cannot be the same as your username. Please choose a different password.")
        return password2

    def clean_shipping_address(self):
        shipping_address = self.cleaned_data.get("shipping_address")
        if not shipping_address or not shipping_address.strip():
            raise ValidationError("Shipping address cannot be empty.")
        return shipping_address

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password1"])
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
            shipping_address = self.cleaned_data.get("shipping_address")
            Address.objects.create(user=user, address=shipping_address, is_default=True)
        return user

class CustomAuthenticationForm(forms.Form):
    username = forms.CharField(label="Username or Email", max_length=255)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Retrieve the request parameter
        super().__init__(*args, **kwargs)  # Call the parent class's initialization method

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not username or not password:
            raise ValidationError("Both username/email and password are required.")

        # Try to find the user via email (if '@' is present)
        user = None
        if '@' in username:  # If the input is an email
            try:
                user = CustomUser.objects.get(email=username)
            except CustomUser.DoesNotExist:
                try:
                    user = CustomUser.objects.get(username=username)
                except CustomUser.DoesNotExist:
                    raise ValidationError("User does not exist.")

        else:
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                raise ValidationError("User does not exist.")

        # If user is found, check the password
        if user and not user.check_password(password):
            raise ValidationError("Incorrect password.")

        if user is None:
            raise ValidationError("Username or email and password do not match.")

        self.user = user
        return self.cleaned_data

    def get_user(self):
        """
        Returns the authenticated user object
        """
        return self.user
