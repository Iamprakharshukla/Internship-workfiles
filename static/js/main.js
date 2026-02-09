function switchView(view) {
    const donorView = document.getElementById('view-donor');
    const recipientView = document.getElementById('view-recipient');

    if (view === 'donor') {
        // View State
        donorView.classList.remove('hidden');
        recipientView.classList.add('hidden');
        // Ensure buttons update correctly (this part was missing explicit ID handling in previous logic if I recall correctly, but existing logic seems to rely on btn-donor/btn-recipient which might not exist in HTML yet. I'll stick to 'tab-donor' and 'tab-recipient' IDs from the HTML file I viewed earlier)
        document.getElementById('tab-donor').classList.add('bg-brand-red', 'text-white', 'border-brand-red');
        document.getElementById('tab-donor').classList.remove('bg-white', 'text-gray-500', 'border-gray-200');

        document.getElementById('tab-recipient').classList.remove('bg-brand-red', 'text-white', 'border-brand-red');
        document.getElementById('tab-recipient').classList.add('bg-white', 'text-gray-500', 'border-gray-200');

        setTimeout(() => {
            donorView.classList.remove('opacity-0');
            recipientView.classList.add('opacity-0');
        }, 10);
    } else {
        // UI State
        // bg.style.transform = 'translateX(100%)'; // Removing 'bg' ref if it doesn't exist or logic is simpler

        // View State
        recipientView.classList.remove('hidden');
        donorView.classList.add('hidden');

        document.getElementById('tab-recipient').classList.add('bg-brand-red', 'text-white', 'border-brand-red');
        document.getElementById('tab-recipient').classList.remove('bg-white', 'text-gray-500', 'border-gray-200');

        document.getElementById('tab-donor').classList.remove('bg-brand-red', 'text-white', 'border-brand-red');
        document.getElementById('tab-donor').classList.add('bg-white', 'text-gray-500', 'border-gray-200');

        setTimeout(() => {
            recipientView.classList.remove('opacity-0');
            donorView.classList.add('opacity-0');
        }, 10);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function handleDonorSubmit(event) {
    event.preventDefault();
    const form = event.target;
    // Map form data to JSON object
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Explicit boolean conversion
    data.consent_given = form.consent_given.checked;

    try {
        const response = await fetch('/blood-request/api/register_donor/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showModal('Success', result.message, true);
            form.reset();
        } else {
            // Format error message
            let errorMsg = 'An error occurred.';
            if (response.status === 500) {
                errorMsg = 'System is undergoing maintenance (Database Reset). Please try again in a few seconds.';
            } else if (result.error) {
                if (Array.isArray(result.error)) {
                    // Pydantic Error
                    errorMsg = result.error.map(e => `${e.loc[0]}: ${e.msg}`).join('\n');
                } else {
                    errorMsg = result.error;
                }
            }
            showModal('Registration Failed', errorMsg, false);
        }
    } catch (error) {
        showModal('System Notification', 'The service is temporarily unavailable. Please try again later.', false);
    }
}

async function handleRecipientSubmit(event) {
    event.preventDefault();
    const form = event.target;
    // Map form data to JSON object
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/blood-request/api/blood_request_create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showModal('Success', result.message, true);
            form.reset();
        } else {
            showModal('Submission Failed', result.error || 'Unknown error', false);
        }
    } catch (error) {
        showModal('System Notification', 'The service is temporarily unavailable. Please try again later.', false);
    }
}

async function searchDonors() {
    const group = document.getElementById('search-group').value;
    const city = document.getElementById('search-city').value;
    const grid = document.getElementById('results-grid');

    grid.innerHTML = '<div class="col-span-full text-center py-12"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-red mx-auto"></div></div>';

    try {
        const url = new URL('/blood-request/api/search_donors/', window.location.origin);
        if (group) url.searchParams.append('blood_group', group);
        if (city) url.searchParams.append('city', city);

        const response = await fetch(url);
        const data = await response.json();

        grid.innerHTML = '';

        if (data.results.length === 0) {
            grid.innerHTML = '<div class="col-span-full text-center py-12 text-gray-500">No donors found matching criteria.</div>';
            return;
        }

        data.results.forEach(donor => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50 transition-colors';
            tr.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${donor.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">${donor.blood_group}</span></td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${donor.city}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${donor.phone}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <a href="tel:${donor.phone}" class="text-brand-red hover:text-red-900">Call</a>
                </td>
            `;
            grid.appendChild(tr);
        });

    } catch (error) {
        grid.innerHTML = '<div class="col-span-full text-center py-12 text-red-500">Error loading results.</div>';
    }
}

function showModal(title, message, isSuccess) {
    const modal = document.getElementById('notification-modal');
    const titleEl = document.getElementById('modal-title');
    const msgEl = document.getElementById('modal-message');
    const iconEl = document.getElementById('modal-icon');

    titleEl.textContent = title;
    msgEl.textContent = message;

    if (isSuccess) {
        iconEl.innerHTML = '<svg class="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>';
        iconEl.className = 'mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-green-100 sm:mx-0 sm:h-10 sm:w-10';
    } else {
        iconEl.innerHTML = '<svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>';
        iconEl.className = 'mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10';
    }

    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('notification-modal').classList.add('hidden');
}


// --- Mobile Navigation Toggle ---
document.addEventListener('DOMContentLoaded', () => {
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileBtn && navMenu) {
        mobileBtn.addEventListener('click', () => {
            mobileBtn.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Close menu when clicking a link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                mobileBtn.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }
});
