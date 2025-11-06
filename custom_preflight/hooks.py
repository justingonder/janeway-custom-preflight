from django.urls import reverse
from core import hooks
from .plugin_settings import install

@hooks.register('stage_context')
def stage_context(context):
    if context['stage'] == 'pre_publication':
        context['template'] = 'custom_preflight/publish_article.html'
        context['url'] = reverse('custom_preflight:publish_article', kwargs={'article_id': context['article'].pk})
    return context

@hooks.register('install_plugins_after')
def install_custom_preflight(plugins):
    if 'custom_preflight' in plugins:
        install()
