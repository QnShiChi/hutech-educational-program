# Design: RBAC Module

## Models

### Department
```python
class DepartmentType(models.TextChoices):
    KHOA = "KHOA", "Khoa"
    VIEN = "VIEN", "Viện"
    PHONG = "PHONG", "Phòng"
    TRUNG_TAM = "TRUNG_TAM", "Trung tâm"
    BAN_GIAM_HIEU = "BAN_GIAM_HIEU", "Ban Giám Hiệu"

class Department(UUIDModel, TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)        # "K.TQH", "PDT", "BGH"
    name = models.CharField(max_length=200)                     # "Khoa Trung Quốc học"
    name_en = models.CharField(max_length=200, blank=True)     
    type = models.CharField(max_length=20, choices=DepartmentType.choices)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['code']
        indexes = [models.Index(fields=['code']), models.Index(fields=['type'])]
```

### Role
```python
class Role(UUIDModel, TimeStampedModel):
    code = models.CharField(max_length=30, unique=True)        # "GIANG_VIEN"
    name = models.CharField(max_length=100)                    # "Giảng viên"
    description = models.TextField(blank=True)
    level = models.IntegerField(default=0)                     # Approval hierarchy
    is_system = models.BooleanField(default=False)             # System roles can't be deleted
    permissions = models.ManyToManyField('Permission', through='RolePermission', blank=True)
    
    class Meta:
        ordering = ['level']
```

### Permission
```python
class PermissionModule(models.TextChoices):
    PROGRAMS = "programs", "Chương trình đào tạo"
    PLO = "plo", "Chuẩn đầu ra"
    SYLLABUS = "syllabus", "Đề cương chi tiết"
    COURSES = "courses", "Học phần"
    RBAC = "rbac", "Quản trị hệ thống"

class Permission(UUIDModel):
    code = models.CharField(max_length=50, unique=True)        # "programs.create"
    name = models.CharField(max_length=100)                    # "Tạo CTĐT"
    module = models.CharField(max_length=20, choices=PermissionModule.choices)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['module', 'code']
```

### RolePermission
```python
class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['role', 'permission']
```

### UserRole
```python
class UserRole(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                             related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,
                                   help_text="Role scope: user has this role in this department")
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, related_name='assigned_roles')
    
    class Meta:
        unique_together = ['user', 'role', 'department']
        indexes = [models.Index(fields=['user', 'role'])]
```

### AuditLog
```python
class AuditAction(models.TextChoices):
    CREATE = "CREATE", "Tạo mới"
    UPDATE = "UPDATE", "Cập nhật"
    DELETE = "DELETE", "Xóa"
    SUBMIT = "SUBMIT", "Nộp duyệt"
    APPROVE = "APPROVE", "Phê duyệt"
    REJECT = "REJECT", "Từ chối"
    ROLLBACK = "ROLLBACK", "Quay lại phiên bản"

class AuditLog(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=AuditAction.choices)
    entity_type = models.CharField(max_length=50)              # "TrainingProgram"
    entity_id = models.UUIDField()
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
```

## Permission Checking

### Custom DRF Permission Class
```python
class HasModulePermission(BasePermission):
    """
    Usage: permission_classes = [HasModulePermission]
    View must define: required_permission = "programs.create"
    Or per-action: permission_map = {"create": "programs.create", "list": "programs.view"}
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        # Admin bypasses all checks
        if user.user_roles.filter(role__code='ADMIN').exists():
            return True
        
        # Get required permission for this action
        perm_code = self._get_required_permission(view)
        if not perm_code:
            return True  # No permission required
        
        # Check if user has permission through any of their roles
        return user.user_roles.filter(
            role__permissions__code=perm_code
        ).exists()
```

### Department-scoped Permission
```python
class DepartmentScopedPermission(HasModulePermission):
    """
    For actions that are scoped to a department.
    Cross-department access only for PHONG_DAO_TAO and ADMIN.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        obj_department = getattr(obj, 'managing_department', 
                        getattr(obj, 'department', None))
        
        if not obj_department:
            return True
        
        # Phòng ĐT and Admin can access all departments
        if user.user_roles.filter(
            role__code__in=['PHONG_DAO_TAO', 'ADMIN']
        ).exists():
            return True
        
        # Others can only access their own department's objects
        return user.user_roles.filter(
            department=obj_department
        ).exists()
```

## Seed Data Management Command
```bash
python manage.py seed_rbac
```
Creates:
1. All permissions (from permission matrix in spec)
2. 6 system roles with correct permission mappings
3. Default departments: BGH, Phòng ĐT, sample Khoa
4. Superuser as ADMIN

## Serializers
- DepartmentSerializer (nested children for tree)
- RoleSerializer (with permissions list)
- PermissionSerializer
- UserRoleSerializer
- UserDetailSerializer (with roles + departments)
- AuditLogSerializer (read-only)
