document.addEventListener('DOMContentLoaded', function () {
    const kbInput = document.querySelector('input[name="knowledge_block"]');
    const cgSelect = document.querySelector('select[name="course_group"]');

    if (!kbInput || !cgSelect) return;

    // Preserve the originally selected course group ID if any
    let initialCgId = cgSelect.value;

    function fetchCourseGroups(kbId, selectedCgId) {
        cgSelect.innerHTML = '<option value="">---------</option>';
        cgSelect.disabled = true;

        if (!kbId) {
            return;
        }

        // Determine base URL dynamically depending on whether it's an add or change page
        const parts = window.location.pathname.split('programs/programcourse/');
        if (parts.length < 2) return;
        const baseUrl = parts[0] + 'programs/programcourse/';

        fetch(`${baseUrl}get-course-groups/?kb_id=${kbId}`)
            .then(response => response.json())
            .then(data => {
                cgSelect.innerHTML = '<option value="">---------</option>';
                data.results.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = item.name;
                    if (selectedCgId && selectedCgId == item.id) {
                        option.selected = true;
                    }
                    cgSelect.appendChild(option);
                });
                cgSelect.disabled = false;
            })
            .catch(error => console.error('Error fetching course groups:', error));
    }

    // Run on initial load
    if (kbInput.value) {
        fetchCourseGroups(kbInput.value, initialCgId);
    } else {
        cgSelect.innerHTML = '<option value="">---------</option>';
        cgSelect.disabled = true;
    }

    // Listen to changes on the raw id field
    // Django's dismissRelatedLookupPopup uses jQuery to trigger the 'change' event
    const $ = (typeof django !== 'undefined' && django.jQuery) ? django.jQuery : null;
    if ($) {
        $(kbInput).on('change', function () {
            fetchCourseGroups(this.value, null);
        });
    }
    // Also add native listener as a fallback
    kbInput.addEventListener('change', function () {
        fetchCourseGroups(this.value, null);
    });
});
