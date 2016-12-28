from django import forms
from django.contrib.gis.geos import Point
from api import Bano
from users.models import User, Location
from django.utils.translation import ugettext_lazy as _


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        labels = {
            'email' : _('Email'),
            'first_name' : _('First name'),
            'last_name' : _('Last name'),
        }

    def clean_email(self):
        # Check a user does not already exist for this email
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("User already exist with this email")
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LocationCreationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ('name', 'address', 'city')
        widgets = {
            'address' : forms.TextInput(),
        }
        labels = {
            'name' : _('Name'),
            'address' : _('Address'),
            'city' : _('City'),
        }

    def clean(self, *args, **kwargs):
        address = self.cleaned_data.get('address')
        city = self.cleaned_data.get('city')

        # Lookup through Bano geocoder
        try:
            bano = Bano()
            results = bano.search(address, city.insee_code)
        except Exception as e:
            raise forms.ValidationError('An error occured during address search: {}'.format(e))

        if not results or not results['features']:
            raise forms.ValidationError('Address not found.')

        # Use point
        geom = results['features'][0]['geometry']
        self.point = Point(*geom['coordinates'])

    def save(self, *args, **kwargs):
        obj = super(LocationCreationForm, self).save(*args, **kwargs)
        obj.point = self.point
        return obj
