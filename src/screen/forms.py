from django import forms
from screen.models import Screen
from users.models import Location
from django.utils.translation import ugettext_lazy as _


class ScreenCreationForm(forms.ModelForm):
    """
    Create a new screen
    """
    location = forms.ModelChoiceField(queryset=Location.objects.none())
    screen_template = forms.ModelChoiceField(queryset=Screen.objects.filter(is_template=True))

    class Meta:
        model = Screen
        fields = (
            'name',
        )
        labels = {
            'name' : _('Name'),
            'location' : _('Location'),
            'screen_template' : _('Screen template'),
        }

    def __init__(self, user, *args, **kwargs):
        super(ScreenCreationForm, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = user.locations.all()
