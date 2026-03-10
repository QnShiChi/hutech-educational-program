# Proposal: Multi-Level Approval Workflow & Versioning

## Intent
Hiện tại HUTECH chưa có phần mềm quản lý chương trình đào tạo, dẫn đến việc phê duyệt CTĐT, chuẩn đầu ra, đề cương chi tiết được thực hiện thủ công qua email và Google Drive. Cần xây dựng hệ thống quy trình phê duyệt số hóa đa cấp, minh bạch, có theo dõi lịch sử, và tự động hóa thông báo.

## Scope

### In Scope
- Quy trình phê duyệt cho 3 loại tài liệu: CTĐT, Chuẩn đầu ra (PLO), Đề cương chi tiết
- State machine quản lý trạng thái quy trình
- Phản hồi (comment) tại mỗi bước duyệt
- Notification khi có sự kiện phê duyệt
- Version control: snapshot toàn bộ dữ liệu khi BGH phê duyệt
- So sánh giữa các phiên bản (diff)
- Rollback về phiên bản trước
- Audit log cho mọi hành động phê duyệt
- Auto-reminder khi chờ duyệt quá thời gian quy định

### Out of Scope
- WebSocket real-time notification (V2 change-24)
- Email notification (V2 change-24)
- AI-powered approval suggestions
- Batch approval (duyệt nhiều tài liệu cùng lúc)

## Approach

### State Machine
Tất cả 3 loại tài liệu dùng chung 1 workflow engine, khác nhau ở số bước duyệt:

**CTĐT (3 bước):**
```
DRAFT ──submit──► KHOA_REVIEWING ──approve──► PDT_REVIEWING ──approve──► BGH_REVIEWING ──approve──► PUBLISHED
                       │                          │                          │
                    reject                      reject                    reject
                       │                          │                          │
                       └──────────────────────────┴──────────────────────────┘
                                                  │
                                                  ▼
                                         REVISION_REQUIRED ──edit──► DRAFT
```

**PLO (3 bước):** Giống CTĐT.

**Đề cương chi tiết (5 bước):**
```
DRAFT ──submit──► TBM_REVIEWING ──approve──► TK_REVIEWING ──approve──► PDT_REVIEWING ──approve──► BGH_REVIEWING ──approve──► PUBLISHED
                       │                         │                          │                          │
                    reject                     reject                    reject                     reject
                       └─────────────────────────┴──────────────────────────┴──────────────────────────┘
                                                                            │
                                                                            ▼
                                                                   REVISION_REQUIRED ──edit──► DRAFT
```

### Generic Workflow Engine
Thiết kế polymorphic: `ApprovalWorkflow` không phụ thuộc cứng vào model cụ thể. Sử dụng `entity_type` + `entity_id` để liên kết với bất kỳ entity nào. Điều này cho phép mở rộng thêm loại tài liệu trong tương lai mà không sửa engine.

### Versioning Strategy
Sử dụng JSONB snapshot: khi BGH phê duyệt, serialize toàn bộ dữ liệu liên quan thành JSON và lưu vào `EntityVersion.snapshot_data`. Cho phép so sánh diff giữa 2 phiên bản và rollback.

## Impact
- **Models mới:** ApprovalWorkflow, ApprovalStep, ApprovalComment, EntityVersion, Notification
- **Sửa models V1:** Thêm helper methods vào TrainingProgram, PLO (submit, can_edit, etc.)
- **APIs mới:** 15+ endpoints cho workflow, version, notification
- **Permissions mới:** `*.submit`, `*.approve_*`, `*.reject` per entity type
- **Celery tasks:** auto-reminder, version snapshot
- **Dependencies:** Không thêm package mới (dùng Django ORM + signals)

## Rollback Plan
- Workflow là module độc lập (`workflows` app), có thể disable mà không ảnh hưởng CRUD
- Nếu rollback: xóa migrations, revert status field về đơn giản (DRAFT/PUBLISHED)
