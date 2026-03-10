## Why

Django admin form cho `ApprovalWorkflow` hiện tại không sử dụng được trong thực tế:

1. **`entity_id` yêu cầu nhập UUID thủ công** — không có entity picker để chọn TrainingProgram/PLO/Syllabus
2. **`total_steps` mặc định = 0** — admin phải tự nhập, dễ bị sai so với WORKFLOW_CONFIGS
3. **Approval Steps phải thêm inline thủ công** — trong khi `WorkflowService.submit()` đã tự động tạo steps
4. **Không có readonly protection** — admin có thể tự sửa `status`, `current_step_number` gây hỏng state machine

Tóm lại: admin form không leverage service layer, dễ tạo dữ liệu sai, và UX kém.

## What Changes

- **Cải thiện `ApprovalWorkflowAdmin`**: thêm autocomplete/raw_id cho entity, readonly fields cho computed fields, custom admin action để submit workflow đúng qua service layer
- **Cải thiện `ApprovalStepInline`**: readonly hoàn toàn (steps chỉ nên tạo qua service), hiển thị thông tin đầy đủ
- **Cải thiện `EntityVersionAdmin`**: thêm filters và readonly fields phù hợp
- **Thêm admin actions**: "Submit for approval" action trên TrainingProgram admin

## Capabilities

### Modified Capabilities

- `approval`: Cải thiện Django admin UX cho approval workflow — readonly protection, autocomplete entity picker, service-layer integration

## Impact

- **Admin UX**: Improvement only — admin sẽ thấy thông tin đầy đủ hơn, không thể tạo dữ liệu sai
- **Không ảnh hưởng API/Frontend**: Chỉ thay đổi admin.py
- **Backward compatible**: Không thay đổi models hay services
