function toggleMenu() {
  var menuContainer = document.querySelector('.menu-container');
  menuContainer.classList.toggle('open');

  if (menuContainer.classList.contains('open')) {
      menuContainer.style.right = '0';
  } else {
      menuContainer.addEventListener('transitionend', function onTransitionEnd() {
          menuContainer.style.right = '';
          menuContainer.removeEventListener('transitionend', onTransitionEnd);
      });
  }
}

function closeMenu() {
  var menuContainer = document.querySelector('.menu-container');
  menuContainer.classList.remove('open');
  menuContainer.style.right = '';
}

function clearAllEntries() {
  var confirmDeleteAll = confirm('Are you sure you want to clear all entries?');

  if (confirmDeleteAll) {
      fetch('/delete_all_entries', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          }
      })
      .then(response => {
          if (response.ok) {
              var tableRows = document.querySelectorAll('table tbody tr');
              tableRows.forEach(row => row.remove());
          } else {
              console.error('Error:', response.statusText);
          }
      })
      .catch(error => console.error('Error:', error));
  }
}

function toggleSummary(button) {
    var summaryRow = button.closest('tr').nextElementSibling;
    var allSummaryRows = document.querySelectorAll('.summary-row');

    if (summaryRow && summaryRow.classList.contains('summary-row')) {
        // Hide all summary rows first
        allSummaryRows.forEach(function(row) {
            if (row !== summaryRow) {
                row.style.display = 'none';
            }
        });

        // Toggle the clicked summary row
        if (summaryRow.style.display === 'table-row') {
            summaryRow.style.display = 'none';
        } else {
            summaryRow.style.display = 'table-row';
        }
    }
}


function deleteEntry(button) {
    var entryForm = button.closest('.action-form');
    var entryId = entryForm.getAttribute('data-entry-id');
    var entryRow = entryForm.closest('tr').previousElementSibling; // Get the previous row with the entry title

    fetch('/delete_data/' + entryId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ entry_id: entryId }),
    })
    .then(response => {
        if (response.ok) {
            entryRow.remove(); // Remove the entry title row
            entryForm.closest('tr').remove(); // Remove the summary row
        } else {
            console.error('Error:', response.statusText);
            alert('Failed to delete entry. Please try again.'); // User feedback
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.'); // User feedback
    });
}

function updateEntry(entryId, button) {
    var updatedCategory = 'UpdatedCategory';
    var updatedTitle = 'UpdatedTitle';
    var updatedMetadata = 'UpdatedMetadata';
    var updatedLink = 'UpdatedLink';
    var updatedSummary = 'UpdatedSummary';

    var entryForm = button.closest('.action-form');
    var entryId = entryForm.getAttribute('data-entry-id');
    var entryRow = entryForm.closest('tr').previousElementSibling; 

    fetch('/update_data/' + entryId, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            category: updatedCategory,
            title: updatedTitle,
            metadata: updatedMetadata,
            link: updatedLink,
            summary: updatedSummary,
        }),
    })
    .then(response => {
        if (response.ok) {
            entryRow.remove(); // Remove the entry title row
            entryForm.closest('tr').remove(); // Remove the summary row
        } else {
            console.error('Error:', response.statusText);
            alert('Failed to delete entry. Please try again.'); // User feedback
        }
    })
    .catch(error => console.error('Error:', error))
    .finally(() => document.activeElement.blur());
}
