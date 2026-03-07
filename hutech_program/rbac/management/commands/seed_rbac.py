"""
Management command to seed RBAC data: permissions, roles, departments, test users.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from hutech_program.rbac.models import (
    Department,
    DepartmentType,
    Permission,
    PermissionModule,
    Role,
    RolePermission,
    UserRole,
)

User = get_user_model()

# ────────────────── Permission definitions ──────────────────

PERMISSIONS = [
    # programs
    ("programs.view", "Xem CTĐT (published)", PermissionModule.PROGRAMS),
    ("programs.view_draft", "Xem CTĐT draft", PermissionModule.PROGRAMS),
    ("programs.create", "Tạo CTĐT", PermissionModule.PROGRAMS),
    ("programs.edit", "Sửa CTĐT", PermissionModule.PROGRAMS),
    ("programs.delete", "Xóa CTĐT draft", PermissionModule.PROGRAMS),
    ("programs.submit", "Nộp CTĐT để duyệt", PermissionModule.PROGRAMS),
    ("programs.approve_khoa", "Duyệt CTĐT cấp Khoa", PermissionModule.PROGRAMS),
    ("programs.approve_pdt", "Duyệt CTĐT cấp Phòng ĐT", PermissionModule.PROGRAMS),
    ("programs.approve_bgh", "Duyệt CTĐT cấp BGH", PermissionModule.PROGRAMS),
    ("programs.export", "Xuất báo cáo", PermissionModule.PROGRAMS),
    ("programs.manage_all", "Quản lý toàn bộ (cross-department)", PermissionModule.PROGRAMS),
    # plo
    ("plo.view", "Xem chuẩn đầu ra", PermissionModule.PLO),
    ("plo.create", "Tạo chuẩn đầu ra", PermissionModule.PLO),
    ("plo.edit", "Sửa chuẩn đầu ra", PermissionModule.PLO),
    ("plo.delete", "Xóa chuẩn đầu ra", PermissionModule.PLO),
    ("plo.approve_khoa", "Duyệt CĐR cấp Khoa", PermissionModule.PLO),
    ("plo.approve_pdt", "Duyệt CĐR cấp Phòng ĐT", PermissionModule.PLO),
    ("plo.approve_bgh", "Duyệt CĐR cấp BGH", PermissionModule.PLO),
    # syllabus
    ("syllabus.view", "Xem đề cương", PermissionModule.SYLLABUS),
    ("syllabus.create", "Tạo đề cương", PermissionModule.SYLLABUS),
    ("syllabus.edit", "Sửa đề cương", PermissionModule.SYLLABUS),
    ("syllabus.delete", "Xóa đề cương", PermissionModule.SYLLABUS),
    ("syllabus.submit", "Nộp đề cương", PermissionModule.SYLLABUS),
    ("syllabus.approve_truong_nganh", "Duyệt ĐC cấp Trưởng ngành", PermissionModule.SYLLABUS),
    ("syllabus.approve_khoa", "Duyệt ĐC cấp Khoa", PermissionModule.SYLLABUS),
    ("syllabus.approve_pdt", "Duyệt ĐC cấp Phòng ĐT", PermissionModule.SYLLABUS),
    ("syllabus.approve_bgh", "Duyệt ĐC cấp BGH", PermissionModule.SYLLABUS),
    # courses
    ("courses.view", "Xem học phần", PermissionModule.COURSES),
    ("courses.create", "Tạo học phần", PermissionModule.COURSES),
    ("courses.edit", "Sửa học phần", PermissionModule.COURSES),
    ("courses.delete", "Xóa học phần", PermissionModule.COURSES),
    # rbac
    ("rbac.manage_users", "Quản lý người dùng", PermissionModule.RBAC),
    ("rbac.manage_roles", "Quản lý vai trò", PermissionModule.RBAC),
    ("rbac.manage_departments", "Quản lý đơn vị", PermissionModule.RBAC),
    ("rbac.view_audit_logs", "Xem nhật ký hệ thống", PermissionModule.RBAC),
]

# ────────────────── Role → Permission mappings ──────────────────

GIANG_VIEN_PERMS = [
    "programs.view", "plo.view", "syllabus.view", "courses.view",
    "syllabus.create", "syllabus.edit", "syllabus.submit",
]

TRUONG_NGANH_PERMS = GIANG_VIEN_PERMS + [
    "syllabus.approve_truong_nganh",
]

LANH_DAO_KHOA_PERMS = TRUONG_NGANH_PERMS + [
    "programs.create", "programs.edit", "programs.submit", "programs.view_draft",
    "plo.create", "plo.edit",
    "syllabus.approve_khoa",
    "programs.approve_khoa", "plo.approve_khoa",
]

PHONG_DAO_TAO_PERMS = LANH_DAO_KHOA_PERMS + [
    "programs.manage_all", "programs.export",
    "programs.approve_pdt", "plo.approve_pdt", "syllabus.approve_pdt",
    "courses.create", "courses.edit",
]

BAN_GIAM_HIEU_PERMS = [
    "programs.view", "programs.view_draft",
    "programs.approve_bgh", "plo.approve_bgh", "syllabus.approve_bgh",
]

ROLES = [
    ("GIANG_VIEN", "Giảng viên", 1, GIANG_VIEN_PERMS),
    ("TRUONG_NGANH", "Trưởng ngành", 2, TRUONG_NGANH_PERMS),
    ("LANH_DAO_KHOA", "Lãnh đạo Khoa", 3, LANH_DAO_KHOA_PERMS),
    ("PHONG_DAO_TAO", "Phòng Đào tạo", 4, PHONG_DAO_TAO_PERMS),
    ("BAN_GIAM_HIEU", "Ban Giám Hiệu", 5, BAN_GIAM_HIEU_PERMS),
    ("ADMIN", "Quản trị viên", 99, None),  # None = all permissions
]

# ────────────────── Departments ──────────────────

DEPARTMENTS = [
    ("BGH", "Ban Giám Hiệu", DepartmentType.BAN_GIAM_HIEU, None),
    ("PDT", "Phòng Đào tạo", DepartmentType.PHONG, None),
    ("K.CNTT", "Khoa Công nghệ thông tin", DepartmentType.KHOA, None),
    ("K.NN", "Khoa Ngoại ngữ", DepartmentType.KHOA, None),
    ("K.QT", "Khoa Quản trị Kinh doanh", DepartmentType.KHOA, None),
]

# ────────────────── Test users ──────────────────

TEST_USERS = [
    ("gv_test", "Nguyễn Văn A", "GIANG_VIEN", "K.CNTT"),
    ("tn_test", "Trần Thị B", "TRUONG_NGANH", "K.CNTT"),
    ("ldk_test", "Lê Văn C", "LANH_DAO_KHOA", "K.CNTT"),
    ("pdt_test", "Phạm Thị D", "PHONG_DAO_TAO", "PDT"),
    ("bgh_test", "Hoàng Văn E", "BAN_GIAM_HIEU", "BGH"),
]


class Command(BaseCommand):
    help = "Seed RBAC data: permissions, roles, departments, test users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing RBAC data before seeding",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write("Resetting RBAC data...")
            UserRole.objects.all().delete()
            RolePermission.objects.all().delete()
            Role.objects.all().delete()
            Permission.objects.all().delete()
            Department.objects.all().delete()

        self._seed_permissions()
        self._seed_roles()
        self._seed_departments()
        self._seed_test_users()
        self._assign_admin_superuser()

        self.stdout.write(self.style.SUCCESS("✓ RBAC seed complete"))

    def _seed_permissions(self):
        created = 0
        for code, name, module in PERMISSIONS:
            _, was_created = Permission.objects.get_or_create(
                code=code,
                defaults={"name": name, "module": module},
            )
            if was_created:
                created += 1
        self.stdout.write(f"  Permissions: {created} created, {len(PERMISSIONS)} total")

    def _seed_roles(self):
        all_perms = {p.code: p for p in Permission.objects.all()}
        created = 0

        for code, name, level, perm_codes in ROLES:
            role, was_created = Role.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "level": level,
                    "is_system": True,
                },
            )
            if was_created:
                created += 1

            # Assign permissions
            if perm_codes is None:
                # ADMIN gets all permissions
                perms_to_assign = list(all_perms.values())
            else:
                perms_to_assign = [all_perms[c] for c in perm_codes if c in all_perms]

            for perm in perms_to_assign:
                RolePermission.objects.get_or_create(role=role, permission=perm)

        self.stdout.write(f"  Roles: {created} created, {len(ROLES)} total")

    def _seed_departments(self):
        created = 0
        for code, name, dept_type, parent_code in DEPARTMENTS:
            parent = None
            if parent_code:
                parent = Department.objects.filter(code=parent_code).first()

            _, was_created = Department.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "type": dept_type,
                    "parent": parent,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(f"  Departments: {created} created, {len(DEPARTMENTS)} total")

    def _seed_test_users(self):
        created = 0
        for username, name, role_code, dept_code in TEST_USERS:
            user, was_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "name": name,
                    "is_active": True,
                },
            )
            if was_created:
                user.set_password("testpass123")
                user.save()
                created += 1

            # Assign role
            role = Role.objects.get(code=role_code)
            department = Department.objects.get(code=dept_code)
            UserRole.objects.get_or_create(
                user=user,
                role=role,
                department=department,
            )

        self.stdout.write(f"  Test users: {created} created, {len(TEST_USERS)} total")

    def _assign_admin_superuser(self):
        """Assign ADMIN role to all superusers."""
        admin_role = Role.objects.filter(code="ADMIN").first()
        if not admin_role:
            return

        # Use PDT department as default for admin role scope
        dept = Department.objects.filter(code="PDT").first()
        if not dept:
            dept = Department.objects.first()
        if not dept:
            return

        for su in User.objects.filter(is_superuser=True):
            UserRole.objects.get_or_create(
                user=su,
                role=admin_role,
                department=dept,
            )
        self.stdout.write("  Superusers assigned ADMIN role")
