"""
Celery tasks for approval workflow.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from hutech_program.notifications.models import Notification
from hutech_program.workflows.models import ApprovalStep, StepStatus
from hutech_program.workflows.services import NotificationService


@shared_task
def check_overdue_approvals():
    """
    Find IN_REVIEW steps older than APPROVAL_OVERDUE_DAYS (default 7).
    Send reminder notifications to approvers.
    Schedule: daily at 08:00 AM.
    """
    from django.conf import settings

    overdue_days = getattr(settings, "APPROVAL_OVERDUE_DAYS", 7)
    threshold = timezone.now() - timedelta(days=overdue_days)

    overdue_steps = ApprovalStep.objects.filter(
        status=StepStatus.IN_REVIEW,
        updated_at__lt=threshold,
        workflow__status="IN_PROGRESS",
    ).select_related("workflow", "required_role")

    count = 0
    for step in overdue_steps:
        entity = step.workflow.get_entity()
        if not entity:
            continue

        days_waiting = (timezone.now() - step.updated_at).days

        NotificationService.notify_step_approvers(step, entity)
        count += 1

    return f"Sent {count} overdue reminders"


@shared_task
def cleanup_old_notifications():
    """
    Delete read notifications older than 90 days.
    Schedule: weekly.
    """
    threshold = timezone.now() - timedelta(days=90)
    deleted_count, _ = Notification.objects.filter(
        is_read=True,
        created_at__lt=threshold,
    ).delete()

    return f"Deleted {deleted_count} old notifications"
