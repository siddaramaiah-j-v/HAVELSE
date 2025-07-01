document.addEventListener("DOMContentLoaded", function() {
    // Simulate loading delay
    setTimeout(function() {
        // Hide the skeleton loader and show the actual content
        const card = document.getElementById("card");
        const content = document.getElementById("content");
          if (card) { // Check if the 'card' element exists
            card.style.display = "none";
        }
        if (content) { // Check if the 'content' element exists
            content.style.display = "block";
        }
    }, 2000); // Adjust the delay as needed
});

//**************************************** password eye visibility *********************************************
    function togglePasswordVisibility(passwordFieldId, toggleIconId) {
        const passwordField = document.getElementById(passwordFieldId);
        const toggleIcon = document.getElementById(toggleIconId);

        if (toggleIcon){
        toggleIcon.addEventListener("click", function () {
            if (passwordField.type === "password") {
                passwordField.type = "text";  // Show password
                toggleIcon.src ='/static/users/images/openeye.png';
            } else {
                passwordField.type = "password";  // Hide password
                toggleIcon.src = '/static/users/images/hidden.png';
            }
        });
        }
    }

    // Initialize toggle for each password field
    togglePasswordVisibility("password1", "togglePassword1");
    togglePasswordVisibility("password2", "togglePassword2");
    togglePasswordVisibility("password", "toggleLogin");

//**************************************** password eye visibility *********************************************

