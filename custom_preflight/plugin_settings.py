from django import forms

from core import models
from utils.install import update_settings_from_plugin
from repository.models import RepositorySetting

PLUGIN_SETTINGS = [
    {
        'name': 'custom_preflight',
        'display_name': 'Custom Preflight',
        'description': 'A plugin that allows for a customizable pre-publication workflow.',
        'author': 'us',
        'author_email': 'us@us.com',
        'install_sql': [],
        'uninstall_sql': [],
    }
]

CUSTOM_PREFLIGHT_SETTINGS = [
    {
        'name': 'confirm_metadata',
        'type': 'boolean',
        'default': True,
        'label': 'Confirm Metadata is Correct',
        'help_text': 'Show the "Confirm Metadata is Correct" step.',
    },
    {
        'name': 'select_issue',
        'type': 'boolean',
        'default': True,
        'label': 'Select an Issue',
        'help_text': 'Show the "Select an Issue" step.',
    },
    {
        'name': 'verify_doi',
        'type': 'boolean',
        'default': True,
        'label': 'Verify DOI',
        'help_text': 'Show the "Verify DOI" step.',
    },
    {
        'name': 'select_open_peer_reviews',
        'type': 'boolean',
        'default': True,
        'label': 'Select open peer reviews to display',
        'help_text': 'Show the "Select open peer reviews to display" step.',
    },
    {
        'name': 'select_galley_for_rendering',
        'type': 'boolean',
        'default': True,
        'label': 'Select a Galley for Rendering',
        'help_text': 'Show the "Select a Galley for Rendering" step.',
    },
    {
        'name': 'set_publication_date',
        'type': 'boolean',
        'default': True,
        'label': 'Set a Publication Date',
        'help_text': 'Show the "Set a Publication Date" step.',
    },
    {
        'name': 'select_article_image',
        'type': 'boolean',
        'default': True,
        'label': 'Select Article Image',
        'help_text': 'Show the "Select Article Image" step.',
    },
    {
        'name': 'send_notifications',
        'type': 'boolean',
        'default': True,
        'label': 'Send Notifications',
        'help_text': 'Show the "Send Notifications" step.',
    },
]

class CustomPreflightSettingsForm(forms.Form):
    confirm_metadata = forms.BooleanField(
        required=False,
        label=CUSTOM_PREFLIGHT_SETTINGS[0]['label'],
        help_text=CUSTOM_PREFLIGHT_SETTINGS[0]['help_text'],
    )
    select_issue = forms.BooleanField(
        required=False,
        label=CUSTOM_PREFLIGHT_SETTINGS[1]['label'],
        help_text=CUSTOM_PREFLIGHT_SETTINGS[1]['help_text'],
    )
    verify_doi = forms.BooleanField(
        required=False,
        label=CUSTOM_PREFLIGHT_SETTINGS[2]['label'],
        help_text=CUSTOM_PREFLIGHT_SETTINGS[2]['help_text'],
    )
    select_open_peer_reviews = forms.BooleanField(
        required=False,
        label=CUSTOM_PREFLIGHT_SETTINGS[3]['label'],
        help_text=CUSTOM_PREFLIGHT_SETTINGS[3]['help_text'],
    )
    select_galley_for_rendering = forms.BooleanField(
        required=False,
        label=CUSTOM_PREFLIGHT_SETTINGS[4]['label'],
        help_text=CUSTOM_PREFLIGHT_SETTINGS[4]['help_text'],
    )
    set_publication_date = forms.BooleanField(
        required=False,
        label=CUSTOM_PREFLIGHT_SETTINGS[5]['label'],
        help_text=CUSTOM_PREFLIGHT_SETTINGS[5]['help_text'],
    )
    select_article_image = forms.BooleanField(
        required=False,
        label=CUSTOM_PREFLIGHT_SETTINGS[6]['label'],
        help_text=CUSTOM_PREFLIGHT_SETTINGS[6]['help_text'],
    )
    send_notifications = forms.BooleanField(
        required=False,
        label=CUSTOM_PREFLIGHT_SETTINGS[7]['label'],
        help_text=CUSTOM_PREFLIGHT_SETTINGS[7]['help_text'],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for setting in CUSTOM_PREFLIGHT_SETTINGS:
            self.fields[setting['name']].initial = RepositorySetting.get_setting(
                'custom_preflight',
                setting['name'],
                setting['default'],
            )

    def save(self):
        for setting in CUSTOM_PREFLIGHT_SETTINGS:
            RepositorySetting.set_setting(
                'custom_preflight',
                setting['name'],
                self.cleaned_data[setting['name']],
            )

def install():
    update_settings_from_plugin(
        'custom_preflight',
        CUSTOM_PREFLIGHT_SETTINGS,
        PLUGIN_SETTINGS,
    )

def uninstall():
    for setting in CUSTOM_PREFLIGHT_SETTINGS:
        try:
            setting_object = models.PluginSetting.objects.get(
                name=setting['name'],
                plugin__name='custom_preflight',
            )
            setting_object.delete()
        except models.PluginSetting.DoesNotExist:
            pass

    plugin = models.Plugin.objects.get(name='custom_preflight')
    plugin.delete()
