window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('hideNav');
    const form = document.getElementById('deleteAccountForm');
    const errorContainer = document.getElementById('errorContainer');
    const successContainer = document.getElementById('successContainer');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const deactivateBtn = document.getElementById('deactivateBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const passwordField = document.getElementById('passwordField');
    if (!mainNav) return;
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove('is-visible');
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });


   function showError(message) {
        errorMessage.textContent = message;
        errorContainer.classList.remove('d-none');
        successContainer.classList.add('d-none');
    }

    // Function to show success message
    function showSuccess(message) {
        successMessage.textContent = message;
        successContainer.classList.remove('d-none');
        errorContainer.classList.add('d-none');
    }

    // Function to hide all messages
    function hideMessages() {
        errorContainer.classList.add('d-none');
        successContainer.classList.add('d-none');
    }

    // Function to toggle loading state
    function setLoading(isLoading) {
        if (isLoading) {
            loadingSpinner.classList.remove('d-none');
            deactivateBtn.disabled = true;
            deactivateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        } else {
            loadingSpinner.classList.add('d-none');
            deactivateBtn.disabled = false;
            deactivateBtn.innerHTML = 'Deactivate';
        }
    }

    // Function to get CSRF token
    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
    }


    document.getElementById('deleteModal').addEventListener('show.bs.modal', function() {
        hideMessages();
        passwordField.value = '';
        setLoading(false);
    });

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const password = passwordField.value.trim();

        if (!password) {
            showError('Password is required.');
            return;
        }

        // Hide previous messages and show loading
        hideMessages();
        setLoading(true);

        try {
            const csrfToken = getCSRFToken();

            const formData = new FormData();
            formData.append('password', password);
            formData.append('csrfmiddlewaretoken', csrfToken);

            const response = await fetch('/account/delete/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (response.ok) {
                if (data.success) {
                    showSuccess(data.message || 'Account deactivated successfully. You will be redirected shortly.');

                    // Redirect after showing success message
                    setTimeout(() => {
                        if (data.redirect_url) {
                            window.location.href = data.redirect_url;
                        } else {
                            window.location.href = '/';
                        }
                    }, 2000);
                } else {
                    showError(data.message || 'An error occurred while deactivating your account.');
                }
            } else {
                // Handle HTTP error responses
                if (data.errors) {
                    // Handle form validation errors
                    if (typeof data.errors === 'object') {
                        const errorMessages = Object.values(data.errors).flat();
                        showError(errorMessages.join(' '));
                    } else {
                        showError(data.errors);
                    }
                } else if (data.message) {
                    showError(data.message);
                } else {
                    showError('An error occurred. Please try again.');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Network error. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    });

    passwordField.addEventListener('input', function() {
        if (!errorContainer.classList.contains('d-none')) {
            hideMessages();
        }
    });


});