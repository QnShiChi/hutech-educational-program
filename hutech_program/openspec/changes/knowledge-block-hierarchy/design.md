# Design: Knowledge Block Hierarchy Display

## 1. Context and Approach
We need to change the Django Admin list view for Knowledge Blocks to a hierarchical tree to represent the parent-child relationship between blocks and their associated course groups. This will involve intercepting the standard query, rebuilding it into a tree in Python, and passing this to a custom HTML template. 

The approach is fully backend-driven rendering, maintaining standard Django Admin patterns where possible (using `__str__` representations and standard URLs for actions) but overriding the specific list markup.

## 2. Core Architecture

### Backend: `KnowledgeBlockAdmin.changelist_view`
We will override `changelist_view` in `programs/admin.py` for `KnowledgeBlockAdmin`.
1. **Data Fetching:** Fetch all `KnowledgeBlock` instances belonging to `active_program`. Optionally, use `.prefetch_related('children', 'course_groups')` for efficiency.
2. **Tree Building:** Construct a hierarchical data structure.
    - Find root blocks (`parent=None`).
    - Recurse or iterate to attach child blocks.
    - Attach `CourseGroup` instances to their respective `KnowledgeBlock`.
3. **Context Injection:** Pass this structured tree to the template via `extra_context['hierarchy_tree']`.

### Frontend: Custom Template
We will create `programs/templates/admin/programs/knowledgeblock/change_list.html`.
- It will `{% extends "admin/change_list.html" %}`.
- It will override `{% block result_list %}`.
- We will write a recursive template mechanism (using `{% include %}` with `with` variables) or a simple nested loop structure to render `<ul>` and `<li>` elements down to 3 levels:
    - Level 1: Root Knowledge Blocks
    - Level 2: Child Knowledge Blocks
    - Level 3: Course Groups

## 3. Data Models
No changes to existing models. We rely on:
- `KnowledgeBlock` (`parent` FK to self, `program` FK)
- `CourseGroup` (`knowledge_block` FK)

## 4. API Design
*N/A - This is a server-side rendered Django Admin view.*

## 5. Security & Permissions
- Standard Django Admin permissions apply. Only users with view/edit permissions on `KnowledgeBlock` or `CourseGroup` should see/interact with the respective links.
- `ProgramContextMixin` ensures we only load data for the currently active program.

## 6. Edge Cases & Risks
- **Performance:** Deep nesting or huge numbers of blocks could cause N+1 query issues. *Mitigation: Use `prefetch_related` when fetching the initial queryset.*
- **Orphaned Course Groups:** Groups without a `KnowledgeBlock` should probably be displayed in a top-level "Unassigned Groups" section or handled gracefully.
- **Deep Nesting:** The UI might break if blocks are nested more than 2 levels deep. *Mitigation: We assume a max depth of 2 for Knowledge Blocks based on requirements, but the recursive template can handle N depth safely if needed.*

## 7. Migration Plan
*N/A - No database migrations required.*
