from django.test import TestCase
from django.urls import reverse
from unittest.mock import MagicMock

from .hooks import stage_context

class CustomPreflightHooksTest(TestCase):
    def test_stage_context_hook(self):
        article = MagicMock()
        article.pk = 1
        context = {
            'stage': 'pre_publication',
            'article': article,
        }

        updated_context = stage_context(context)

        self.assertEqual(updated_context['template'], 'custom_preflight/publish_article.html')
        self.assertEqual(updated_context['url'], reverse('custom_preflight:publish_article', kwargs={'article_id': 1}))

    def test_stage_context_hook_other_stage(self):
        article = MagicMock()
        article.pk = 1
        context = {
            'stage': 'other_stage',
            'article': article,
            'template': 'original_template.html',
            'url': '/original/url/',
        }

        updated_context = stage_context(context)

        self.assertEqual(updated_context['template'], 'original_template.html')
        self.assertEqual(updated_context['url'], '/original/url/')
