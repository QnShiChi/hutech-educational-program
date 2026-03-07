"""
Common base models cho HUTECH Program.
Cung cấp UUIDModel, TimeStampedModel dùng chung cho tất cả apps.
"""

import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract model cung cấp created_at và updated_at.
    Tất cả model nghiệp vụ nên kế thừa từ class này.
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract model cung cấp UUID primary key.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """
    Base model kết hợp UUID pk + timestamps.
    Đây là base class chính cho tất cả business models.
    """

    class Meta:
        abstract = True
