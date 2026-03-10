## Context

The `programcourse` add/edit form in Django Admin has a dependent dropdown where selecting a Knowledge Block populates the Course Group options via an AJAX fetch request. Currently, the dependent dropdown logic fails to fire when a Knowledge Block is selected via Django's related object lookup popup (the magnifying glass icon).

## Goals / Non-Goals

**Goals:**

- Fix the dependent dropdown so that selecting a Knowledge Block via the popup correctly triggers the fetching of related Course Groups and populates the dropdown.

**Non-Goals:**

- Refactoring the entire dependent dropdown logic.
- Modifying the backend API (`get_course_groups`) for fetching course groups.

## Decisions

- **Use `django.jQuery` to attach the change event listener:** Django's `dismissRelatedLookupPopup` (used when returning a value from the popup window) triggers a jQuery `change` event on the input field. The native `addEventListener('change', ...)` currently used in `program_course_dependent_dropdown.js` fails to intercept this jQuery-triggered event. By replacing the native listener with `django.jQuery('#id_knowledge_block').on('change', ...)`, we ensure that the event is correctly captured whether it's triggered manually by typing or via the Django admin popup.

## Risks / Trade-offs

- **Risk:** `django.jQuery` might not be loaded when the script runs.
  **Mitigation:** The script will be wrapped in `(function($) { ... })(django.jQuery);` and use `$(document).ready()` to ensure that the Django admin's jQuery instance is fully loaded and available before attaching the event listener.
