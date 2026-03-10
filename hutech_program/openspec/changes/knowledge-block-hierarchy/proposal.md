# Proposal: Knowledge Block Hierarchy Display

## 1. What are we building?
We are modifying the Django Admin change list view for Knowledge Blocks (`/admin/programs/knowledgeblock/`) to display data in a visual hierarchical tree structure rather than a flat table. 
The hierarchy will show:
1. **Parent Knowledge Blocks** (Level 1)
2. **Child Knowledge Blocks** (Level 2)
3. **Course Groups** (Level 3 - leaf nodes belonging to their respective Knowledge Blocks)

## 2. Why are we building this?
The current flat table view makes it difficult to understand the complex, nested structure of a training program's knowledge blocks and how course groups fit into them. A hierarchical tree view will provide curriculum designers and administrators with an intuitive, unified view of the program structure, significantly improving usability and comprehension.

## 3. How will it work?
- **Backend:** The `KnowledgeBlockAdmin.changelist_view` will be modified to retrieve all `KnowledgeBlock` and `CourseGroup` instances associated with the `active_program`. This data will be structured into a nested Python dictionary/list representing the true hierarchy and passed to a custom template via `extra_context`.
- **UI:** A custom template (`programs/templates/admin/programs/knowledgeblock/change_list.html`) extending the default `admin/change_list.html` will be created. It will replace the standard result list with custom HTML/CSS to render the tree using semantic nested lists (`<ul>`, `<li>`), styled to look like an administrative tree control.
- **Interactions:** Standard Django Admin functionalities (Add, Edit, Delete) will be preserved. The UI will render explicit action buttons/links next to each node (e.g., "Add Child Block", "Add Course Group", "Edit", "Delete") pointing to standard Django Admin URLs, pre-filling parent IDs via URL parameters where appropriate.

## 4. What is out of scope?
- Drag-and-drop reordering is out of scope for this initial implementation.
- Modifying the underlying models (`KnowledgeBlock`, `CourseGroup`) is not required as the necessary relationships (`parent`, `knowledge_block`) already exist.
- Changing the presentation of other admin pages.

## 5. Success Criteria
- The Knowledge Block list view correctly displays a three-level hierarchy (Parent Block -> Child Block -> Course Group).
- The hierarchy accurately reflects the data for the currently selected `active_program`.
- Users can click links on each node to Add, Edit, or Delete items, maintaining the standard admin workflow.
- Visual styling is clean and intuitive, following Django Admin aesthetics.
