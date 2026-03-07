"""
Import views: upload, status, preview, confirm.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hutech_program.rbac.models import Department
from hutech_program.rbac.permissions import HasModulePermission

from .models import ImportStatus, ImportTask
from .serializers import (
    ImportTaskPreviewSerializer,
    ImportTaskSerializer,
    ImportTaskUploadSerializer,
)
from .tasks import confirm_import_task, import_training_program_task


class ImportViewSet(viewsets.GenericViewSet):
    """
    Upload .docx file → parse → preview → confirm → save to DB.
    """

    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "upload": "programs.create",
        "status_check": "programs.view",
        "preview": "programs.view",
        "confirm": "programs.create",
    }

    def get_queryset(self):
        return ImportTask.objects.filter(uploaded_by=self.request.user)

    @action(detail=False, methods=["post"], url_path="training-program")
    def upload(self, request):
        """Upload a .docx file and start async parsing."""
        ser = ImportTaskUploadSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        department = get_object_or_404(
            Department, pk=ser.validated_data["department_id"]
        )
        uploaded_file = ser.validated_data["file"]

        task = ImportTask.objects.create(
            file_name=uploaded_file.name,
            file=uploaded_file,
            department=department,
            uploaded_by=request.user,
            status=ImportStatus.PENDING,
        )

        # Trigger async parsing
        import_training_program_task.delay(str(task.id))

        return Response(
            ImportTaskSerializer(task).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["get"], url_path="status")
    def status_check(self, request, pk=None):
        """Poll import task status."""
        task = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(ImportTaskSerializer(task).data)

    @action(detail=True, methods=["get"])
    def preview(self, request, pk=None):
        """Get parsed data preview before confirming."""
        task = get_object_or_404(self.get_queryset(), pk=pk)
        if task.status not in (ImportStatus.PREVIEW, ImportStatus.COMPLETED):
            return Response(
                {"detail": "Dữ liệu chưa sẵn sàng để xem trước."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(ImportTaskPreviewSerializer(task).data)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        """Confirm and save parsed data to DB."""
        task = get_object_or_404(self.get_queryset(), pk=pk)
        if task.status != ImportStatus.PREVIEW:
            return Response(
                {"detail": "Chỉ có thể xác nhận tác vụ đang ở trạng thái xem trước."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        confirm_import_task.delay(str(task.id))

        return Response(
            {"detail": "Đang xử lý xác nhận.", "task_id": str(task.id)},
            status=status.HTTP_202_ACCEPTED,
        )
