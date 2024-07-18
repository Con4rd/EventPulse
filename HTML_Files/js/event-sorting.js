document.addEventListener('DOMContentLoaded', function() {
    const sortingSelect = document.getElementById('sortingOption');
    const eventsContainer = document.getElementById('eventsContainer');

    if (sortingSelect && eventsContainer) {
        sortingSelect.addEventListener('change', function() {
            const sortOption = this.value;
            if (sortOption === 'newest') {
                sortEventsByProximity();
            } else {
                // Reset to default order
                location.reload();
            }
        });
    }

    function sortEventsByProximity() {
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Set to beginning of today

        const events = Array.from(eventsContainer.children);
        events.sort((a, b) => {
            const dateA = new Date(a.querySelector('.tc_content [data-datetime]').dataset.datetime);
            const dateB = new Date(b.querySelector('.tc_content [data-datetime]').dataset.datetime);

            // Calculate the difference in days
            const diffA = Math.abs(dateA - today) / (1000 * 60 * 60 * 24);
            const diffB = Math.abs(dateB - today) / (1000 * 60 * 60 * 24);

            // Sort by proximity to today
            return diffA - diffB;
        });

        // Reorder the events in the DOM
        events.forEach(event => eventsContainer.appendChild(event));
    }
});