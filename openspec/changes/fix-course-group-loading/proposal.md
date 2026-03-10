## Why

The "Nhóm học phần" (Course Group) dependent dropdown currently fails to load when a "Khối kiến thức" (Knowledge Block) is selected on the `programcourse/add/` admin page. This occurs because the JavaScript event listener in `program_course_dependent_dropdown.js` uses a native `addEventListener('change', ...)` which fails to intercept the jQuery-triggered `change` events dispatched by Django's `dismissRelatedLookupPopup` when a user selects an item from the related object popup. Fixing this ensures the dependent dropdown functions correctly.

## What Changes

- Update `hutech_program/programs/static/admin/js/program_course_dependent_dropdown.js` to attach the `change` event listener to the `knowledge_block` input using `django.jQuery`, ensuring compatibility with Django admin's popup behavior.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- None (Bug fix only, no requirement changes)

## Impact

- `hutech_program/programs/static/admin/js/program_course_dependent_dropdown.js`
- Course Group dependent dropdown behavior on the Program Course add/change admin pages.
