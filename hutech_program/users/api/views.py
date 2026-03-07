from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from hutech_program.users.models import User

from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    """ViewSet cho User API."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self):
        """Lọc users theo quyền."""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)

    @action(detail=False)
    def me(self, request):
        """Trả về thông tin user hiện tại."""
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)
