from django import forms
from screen.models import Screen
from users.models import Location


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

    def __init__(self, user, *args, **kwargs):
        super(ScreenCreationForm, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = user.locations.all()
