from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from submission import models as submission_models
from journal import models as journal_models, issue_forms as journal_issue_forms, forms as journal_forms, logic as journal_logic
from submission import forms as submission_forms
from utils import shared
from events import logic as event_logic


def publish_article(request, article_id):
    """
    View allows user to set an article for publication
    :param request: request object
    :param article_id: Article PK
    :return: contextualised django template
    """
    article = get_object_or_404(
        submission_models.Article,
        Q(stage=submission_models.STAGE_READY_FOR_PUBLICATION)
        | Q(stage=submission_models.STAGE_PUBLISHED),
        pk=article_id,
        journal=request.journal,
    )
    journal_models.FixedPubCheckItems.objects.get_or_create(article=article)

    doi_data, doi = journal_logic.get_doi_data(article)
    issues = request.journal.issues
    new_issue_form = journal_issue_forms.NewIssue(journal=article.journal)
    pub_date_form = submission_forms.PubDateForm(instance=article)
    notification_form_kwargs = {
        "email_context": {
            "article": article,
        },
        "request": request,
    }
    notification_initial = journal_logic.get_initial_for_prepub_notifications(
        request,
        article,
    )
    notification_formset = journal_forms.PrepubNotificationFormSet(
        form_kwargs=notification_form_kwargs,
        initial=notification_initial,
    )
    modal = request.GET.get("m", None)

    if request.POST:
        if "assign_issue" in request.POST:
            try:
                issue = journal_models.Issue.objects.get(
                    pk=request.POST["assign_issue"],
                )
                journal_logic.handle_assign_issue(request, article, issue)
            except journal_models.Issue.DoesNotExist:
                messages.add_message(
                    request,
                    messages.WARNING,
                    ("Issue not in this journal’s issue list."),
                )

            return redirect(
                "{0}?m=issue".format(
                    reverse(
                        "custom_preflight:publish_article",
                        kwargs={"article_id": article.pk},
                    )
                )
            )

        if "unassign_issue" in request.POST:
            journal_logic.handle_unassign_issue(request, article, issues)
            return redirect(
                "{0}?m=issue".format(
                    reverse(
                        "custom_preflight:publish_article",
                        kwargs={"article_id": article.pk},
                    )
                )
            )

        if "new_issue" in request.POST:
            new_issue_form, modal, new_issue = journal_logic.handle_new_issue(request)
            if new_issue:
                return redirect(
                    "{0}?m=issue".format(
                        reverse(
                            "custom_preflight:publish_article",
                            kwargs={"article_id": article.pk},
                        )
                    )
                )

        if "pubdate" in request.POST:
            pub_date_form = submission_forms.PubDateForm(
                request.POST,
                instance=article,
            )
            if pub_date_form.is_valid():
                article = pub_date_form.save()
                if article.date_published:
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        (
                            f"Publication date set to {article.date_published.strftime('%Y-%m-%d %H:%M %Z')} "
                            f"({(article.date_published)})"
                        ),
                    )
                else:
                    messages.add_message(
                        request, messages.SUCCESS, ("Publication date unset")
                    )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    (
                        f"Something went wrong when trying to save the form. "
                        f"Please try again."
                    ),
                )

        if "notifications" in request.POST:
            notification_formset = journal_forms.PrepubNotificationFormSet(
                request.POST,
                form_kwargs=notification_form_kwargs,
                initial=notification_initial,
            )
            if notification_formset.is_valid():
                journal_logic.handle_prepub_notifications(
                    request,
                    article,
                    notification_formset,
                )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Something went wrong. Please try again.",
                )

        if "galley" in request.POST:
            journal_logic.set_render_galley(request, article)
            return redirect(
                reverse(
                    "custom_preflight:publish_article",
                    kwargs={"article_id": article.pk},
                )
            )

        if "image" in request.POST or "delete_image" in request.POST:
            journal_logic.set_article_image(request, article)
            shared.clear_cache()
            return redirect(
                "{0}{1}".format(
                    reverse(
                        "custom_preflight:publish_article",
                        kwargs={"article_id": article.pk},
                    ),
                    "?m=article_image",
                )
            )

        if "open_reviews" in request.POST:
            journal_logic.set_open_reviews(request, article)
            reverse(
                "custom_preflight:publish_article",
                kwargs={"article_id": article.pk},
            )

        if "publish" in request.POST:
            article.stage = submission_models.STAGE_PUBLISHED
            article.close_core_workflow_objects()

            if not article.date_published:
                article.date_published = timezone.now()

            article.save()

            # Fire publication event
            kwargs = {"article": article, "request": request}
            event_logic.Events.raise_event(
                event_logic.Events.ON_ARTICLE_PUBLISHED,
                task_object=article,
                **kwargs,
            )

            # Attempt to register xref DOI
            for identifier in article.identifier_set.all():
                if identifier.id_type == "doi":
                    status, error = identifier.register()
                    messages.add_message(
                        request, messages.INFO if not error else messages.ERROR,
 status
                    )

            messages.add_message(
                request,
                messages.SUCCESS,
                ("Article set for publication."),
            )

            # clear the cache
            shared.clear_cache()

            if request.journal.element_in_workflow(
                element_name="prepublication",
            ):
                workflow_kwargs = {
                    "handshake_url": "publish",
                    "request": request,
                    "article": article,
                    "switch_stage": True,
                }
                return event_logic.Events.raise_event(
                    event_logic.Events.ON_WORKFLOW_ELEMENT_COMPLETE,
                    task_object=article,
                    **workflow_kwargs,
                )

        return redirect(
            reverse(
                "custom_preflight:publish_article",
                kwargs={"article_id": article.pk},
            )
        )

    template = "custom_preflight/publish_article.html"
    context = {
        "article": article,
        "doi_data": doi_data,
        "doi": doi,
        "issues": issues,
        "new_issue_form": new_issue_form,
        "modal": modal,
        "pub_date_form": pub_date_form,
        "notification_formset": notification_formset,
    }

    return render(request, template, context)


def settings(request):
    from . import plugin_settings

    form = plugin_settings.CustomPreflightSettingsForm()
    if request.POST:
        form = plugin_settings.CustomPreflightSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Settings saved.")

    template = "custom_preflight/settings.html"
    context = {
        "form": form,
    }
    return render(request, template, context)
