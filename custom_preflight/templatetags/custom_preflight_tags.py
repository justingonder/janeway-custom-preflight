from django import template
from core.models import SettingValue

register = template.Library()

@register.simple_tag
def custom_preflight_settings():
    from .. import plugin_settings

    settings = {}
    for setting in plugin_settings.CUSTOM_PREFLIGHT_SETTINGS:
        settings[setting['name']] = {
            'value': SettingValue.get_setting(
                'custom_preflight',
                setting['name'],
                setting['default'],
            ),
            'label': setting['label'],
        }
    return settings
