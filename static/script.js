// -----------------------------
// Confirm before adding a consultant
// -----------------------------
const consultantForm = document.querySelector('form[action*="add_consultant"]');
if (consultantForm) {
    consultantForm.addEventListener('submit', function (event) {
        const nameInput = consultantForm.querySelector('input[name="name"]');
        if (nameInput && !confirm(`Add consultant "${nameInput.value}"?`)) {
            event.preventDefault();
        }
    });
}

// -----------------------------
// Confirm before adding a role
// -----------------------------
const roleForm = document.querySelector('form[action*="roles"]');
if (roleForm) {
    roleForm.addEventListener('submit', function (event) {
        const roleInput = roleForm.querySelector('input[name="role_name"]');
        if (roleInput && !confirm(`Add role "${roleInput.value}"?`)) {
            event.preventDefault();
        }
    });
}

// -----------------------------
// Highlight input focus
// -----------------------------
const inputs = document.querySelectorAll('input, select');
inputs.forEach(input => {
    input.addEventListener('focus', function () {
        this.style.borderColor = '#3498db';
        this.style.boxShadow = '0 0 5px #3498db';
    });
    input.addEventListener('blur', function () {
        this.style.borderColor = '';
        this.style.boxShadow = '';
    });
});

// -----------------------------
// Highlight top 3 matches by score
// -----------------------------
document.querySelectorAll('.match-list').forEach(ul => {
    const items = Array.from(ul.querySelectorAll('li'));
    if (items.length === 0) return;

    // Sort items by score descending
    const sorted = items.sort((a, b) => parseInt(b.dataset.score) - parseInt(a.dataset.score));

    sorted.forEach((li, index) => {
        li.classList.remove('highest', 'medium', 'lowest');
        if (index === 0) li.classList.add('highest');      // best match
        else if (index === 1) li.classList.add('medium');  // second best
        else if (index === 2) li.classList.add('lowest');  // third
    });
});
