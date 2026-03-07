"""
Audit logging mixin and utilities.
"""

from django.forms.models import model_to_dict

from hutech_program.rbac.models import AuditAction, AuditLog


class AuditLogMixin:
    """
    Mixin for DRF ViewSets to automatically create audit logs.

    Usage:
        class MyViewSet(AuditLogMixin, ModelViewSet):
            audit_entity_type = "TrainingProgram"
    """

    audit_entity_type: str = ""

    def _get_entity_type(self):
        if self.audit_entity_type:
            return self.audit_entity_type
        return self.get_queryset().model.__name__

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def _serialize_instance(self, instance):
        """Serialize a model instance to dict for audit logging."""
        try:
            data = model_to_dict(instance)
            # Convert non-serializable types
            result = {}
            for key, value in data.items():
                if hasattr(value, "pk"):
                    result[key] = str(value.pk)
                elif hasattr(value, "__iter__") and not isinstance(value, (str, dict)):
                    result[key] = [str(v) for v in value]
                else:
                    result[key] = str(value) if value is not None else None
            return result
        except Exception:
            return {"id": str(instance.pk)}

    def _create_audit_log(self, request, action, instance, old_data=None, new_data=None):
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=action,
            entity_type=self._get_entity_type(),
            entity_id=instance.pk,
            old_data=old_data,
            new_data=new_data,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self._create_audit_log(
            self.request,
            AuditAction.CREATE,
            instance,
            new_data=self._serialize_instance(instance),
        )

    def perform_update(self, serializer):
        old_data = self._serialize_instance(serializer.instance)
        instance = serializer.save()
        new_data = self._serialize_instance(instance)
        self._create_audit_log(
            self.request,
            AuditAction.UPDATE,
            instance,
            old_data=old_data,
            new_data=new_data,
        )

    def perform_destroy(self, instance):
        old_data = self._serialize_instance(instance)
        entity_id = instance.pk
        entity_type = self._get_entity_type()
        instance.delete()
        AuditLog.objects.create(
            user=self.request.user if self.request.user.is_authenticated else None,
            action=AuditAction.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            old_data=old_data,
            ip_address=self._get_client_ip(self.request),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
        )


def get_user_permissions(user):
    """
    Return a set of permission codes for a user across all their roles.
    """
    if not user.is_authenticated:
        return set()

    if user.is_superuser:
        from hutech_program.rbac.models import Permission
        return set(Permission.objects.values_list("code", flat=True))

    return set(
        user.user_roles.values_list(
            "role__permissions__code", flat=True
        ).distinct()
    ) - {None}
