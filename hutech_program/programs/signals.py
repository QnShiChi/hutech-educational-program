"""
Signals for the programs app.
Triggers notification when a Course is updated.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Course, ProgramCourse


@receiver(post_save, sender=Course)
def notify_course_change(sender, instance, created, **kwargs):
    """
    When a Course is edited (not created), find all CTĐTs
    using this course and create a notification.
    """
    if created:
        return

    # Find all programs that use this course
    program_courses = ProgramCourse.objects.filter(
        course=instance
    ).select_related("program")

    if not program_courses.exists():
        return

    # Import here to avoid circular imports
    try:
        from hutech_program.notifications.models import Notification
    except ImportError:
        # notifications app not yet implemented — silently skip
        return

    for pc in program_courses:
        # Notify the program creator about the course change
        if pc.program.created_by:
            Notification.objects.create(
                user=pc.program.created_by,
                title="Học phần đã cập nhật",
                message=(
                    f"Học phần {instance.code} - {instance.name_vi} "
                    f"đã được cập nhật trong CTĐT {pc.program.program_code}."
                ),
            )
