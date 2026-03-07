# Proposal: RBAC Module (Phân quyền & Vai trò)

## Summary
Xây dựng hệ thống phân quyền dựa trên vai trò (Role-Based Access Control) cho HUTECH Program, quản lý 6 nhóm người dùng với quyền hạn khác nhau theo cấu trúc tổ chức của HUTECH.

## Motivation
Hệ thống HUTECH Program có quy trình phê duyệt đa cấp (Khoa → Phòng ĐT → BGH). Mỗi cấp có quyền hạn khác nhau. RBAC đảm bảo:
- Giảng viên chỉ edit đề cương được phân công
- Lãnh đạo Khoa chỉ quản lý CTĐT của Khoa mình
- Phòng Đào tạo quản lý toàn bộ dữ liệu
- Admin quản lý tài khoản và phân quyền

## 6 Vai trò (Roles)

| # | Role Code | Role Name | Mô tả |
|---|-----------|-----------|-------|
| 1 | GIANG_VIEN | Giảng viên | Nhập/sửa đề cương chi tiết theo phân công |
| 2 | TRUONG_NGANH | Trưởng ngành/bộ môn | Duyệt/phản hồi đề cương chi tiết |
| 3 | LANH_DAO_KHOA | Lãnh đạo Khoa/Viện/TT | Nhập/sửa CTĐT, PLO. Duyệt đề cương |
| 4 | PHONG_DAO_TAO | Phòng Đào tạo | Quản lý toàn bộ, xét duyệt, xuất báo cáo |
| 5 | BAN_GIAM_HIEU | Ban Giám Hiệu | Phê duyệt cuối cùng |
| 6 | ADMIN | Quản trị hệ thống | Quản lý tài khoản, phân quyền, nhật ký |

## What's Changing
- Tạo models: Department, Role, Permission, RolePermission, UserRole
- CRUD APIs cho tất cả entities
- Permission checking middleware/decorator
- Seed data cho 6 roles mặc định
- Department tree (phân cấp)
- Django Admin integration

## What's NOT Changing
- User model (đã tạo ở step 01)
- JWT auth (đã setup ở step 01)
- Frontend (sẽ implement ở step 09)
