## 1. Implementation

- [x] 1.1 Update `hutech_program/programs/static/admin/js/program_course_dependent_dropdown.js` to use `django.jQuery` for the `change` event listener on the `#id_knowledge_block` input, ensuring compatibility with Django's popup return behavior.

## 2. Testing

- [x] 2.1 Manually verify that selecting a Knowledge Block via the raw_id_fields popup successfully fetches and populates the Course Group dropdown on the Program Course Add/Change admin page.
