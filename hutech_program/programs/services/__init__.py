from django.db import transaction

from hutech_program.programs.models import TrainingProgramVersion
from hutech_program.programs.services.versioning import clone_program_version


class VersioningException(Exception):
    pass

class VersionAlreadyExistsException(VersioningException):
    pass
