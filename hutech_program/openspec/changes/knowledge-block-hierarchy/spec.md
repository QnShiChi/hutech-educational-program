# Knowledge Block Hierarchy Display

## Goal
Modify the Django Admin change list view for Knowledge Blocks (`http://localhost:8000/admin/programs/knowledgeblock/`) to display data in a visual hierarchical tree structure rather than a flat table. The hierarchy will show:
1. **Parent Knowledge Blocks** (Level 1)
2. **Child Knowledge Blocks** (Level 2)
3. **Course Groups** (Level 3 - leaf nodes belonging to their respective Knowledge Blocks)

This feature aims to provide curriculum designers and administrators with an intuitive, unified view of the program structure, making it easier to see how Course Groups fit within Knowledge Blocks.

## Technical Approach

### 1. Data Retrieval and Structuring (Backend)
- Modify `KnowledgeBlockAdmin.changelist_view` to intercept the standard view.
- Retrieve all `KnowledgeBlock` and `CourseGroup` instances associated with the `active_program`.
- Construct a nested Python dictionary or list structure representing the true hierarchy.
- Pass this structured data to a custom template via standard Django Admin `extra_context`.

### 2. Custom Template (UI)
- Overwrite or extend the change list template explicitly for the Knowledge Block admin (`programs/templates/admin/programs/knowledgeblock/change_list.html`).
- The template will inherit from `admin/change_list.html`.
- Replace the `{% block result_list %}` block with custom HTML/CSS to render the tree using semantic nested lists (`<ul>`, `<li>`), styled to look like an administrative tree control.

### 3. Preserving Admin Actions
- Ensure standard Django Admin functionalities (Add, Edit, Delete) are preserved.
- The UI will render explicit action buttons/links next to each node (e.g., "Add Child Block", "Add Course Group", "Edit", "Delete") pointing to standard Django Admin URLs, pre-filling parent IDs via URL parameters where appropriate.
- Maintain compatibility with the `ProgramContextMixin` which scopes all data to the currently edited `TrainingProgram`.
