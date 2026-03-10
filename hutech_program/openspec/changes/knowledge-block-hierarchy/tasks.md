# Implementation Tasks: Knowledge Block Hierarchy Display

## Phase 1: Backend Data Preparation

- [x] **Task 1.1**: Override `changelist_view` in `KnowledgeBlockAdmin`.
  - **File**: `programs/admin.py`
  - **Action**: Add/modify `changelist_view` method in the `KnowledgeBlockAdmin` class.
  - **Details**:
    - Retrieve all `KnowledgeBlock` and `CourseGroup` instances related to the `active_program`. Use `prefetch_related` for optimization if appropriate.
    - Write a helper utility (e.g., inside the view or a separate service function) to build the hierarchical tree structure (Roots -> Children -> Course Groups).
    - Inject this structured tree into the template context via `extra_context['hierarchy_tree']`.
    - Ensure `active_program` is still passed or available in the template.

## Phase 2: Custom Template Creation

- [x] **Task 2.1**: Create custom change list template.
  - **File**: `programs/templates/admin/programs/knowledgeblock/change_list.html`
  - **Action**: Create new template extending `admin/change_list.html`.
  - **Details**:
    - Override the `{% block result_list %}`.
    - Write the HTML/template logic to render the `hierarchy_tree` passed from the backend.
    - Use nested `<ul>` and `<li>` elements to represent the 3 levels (Parent Block -> Child Block -> Course Group).
    - Add basic CSS classes (built-in Django Admin classes or inline/custom CSS) to make the tree look presentable (indentation, bullet points, etc.).

## Phase 3: Integrate Admin Actions

- [x] **Task 3.1**: Add action links to the template nodes.
  - **File**: `programs/templates/admin/programs/knowledgeblock/change_list.html`
  - **Action**: Update the template to include standard Django Admin action links next to each item.
  - **Details**:
    - For Level 1 Blocks: Add "Edit", "Delete", "Add Child Block" (linking to `KnowledgeBlock` add page with `parent` pre-filled if possible), "Add Course Group" (linking to `CourseGroup` add page with `knowledge_block` pre-filled).
    - For Level 2 Blocks: Add "Edit", "Delete", "Add Course Group".
    - For Level 3 Course Groups: Add "Edit", "Delete".
    - Ensure all links correctly respect the standard Django admin URLs for the respective models.

## Phase 4: Testing & Verification

- [x] **Task 4.1**: Manual UI Verification.
  - **Action**: Run the local server and navigate to `http://localhost:8000/admin/programs/knowledgeblock/`.
  - **Details**:
    - Verify the list view is replaced by the tree view.
    - Verify data matches the currently selected `active_program`.
    - Verify that the 3 levels are displayed correctly.
    - Test clicking on "Edit", "Add" links to ensure they route to the correct Django Admin forms.
