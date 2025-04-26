document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById('toggle-btn')
    const sidebar = document.getElementById('sidebar')

    function toggleSidebar() {
        sidebar.classList.toggle('close')
        toggleButton.classList.toggle('rotate')

        closeAllSubMenus()
    }

    function toggleSubMenu(button) {

        if (!button.nextElementSibling.classList.contains('show')) {
            closeAllSubMenus()
        }

        button.nextElementSibling.classList.toggle('show')
        button.classList.toggle('rotate')

        if (sidebar.classList.contains('close')) {
            sidebar.classList.toggle('close')
            toggleButton.classList.toggle('rotate')
        }
    }

    function closeAllSubMenus() {
        Array.from(sidebar.getElementsByClassName('show')).forEach(ul => {
            ul.classList.remove('show')
            ul.previousElementSibling.classList.remove('rotate')
        })
    }
    window.toggleSubMenu = toggleSubMenu
    window.toggleSidebar = toggleSidebar
    // ====================================================================================================================================
    // Open and close modal for log in and reg popup form
    // Open and close modal for log in and reg popup form
    const modal = document.getElementById("loginModal");
    const loginBtn = document.getElementById("loginBtn");
    const closeBtn = document.querySelector(".close-btn");
    loginBtn.onclick = () => {
        modal.style.display = "flex";
    };

    closeBtn.onclick = () => {
        modal.style.display = "none";
    };

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };

    // Tab functionality 
    function openTab(evt, tabName) {
        const tabcontent = document.getElementsByClassName("tabcontent");
        const tablinks = document.getElementsByClassName("tablinks");

        for (let i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }

        for (let i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }

        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.className += " active";
    }

    window.openTab = openTab;
    // openTab function will be accessible from your inline onclick attributes.

    // AJAX for Login Form
    document.querySelector("#Loginform").onsubmit = async function (event) {
        //  const loginUrl = "{% url 'login' %}";
        event.preventDefault();
        const formData = new FormData(this);
        const response = await fetch(loginUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",

            },
        }).catch((error) => {
            console.error('Fetch error:', error);
            alert('An error occurred. Please try again.');
        });
        console.log("Response received:", response);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        console.log(data)
        if (data.success) {

            alert(data.message); // Display success message
            modal.style.display = "none"; // Close the modal
            // window.location.href = data.redirect_url;
            location.reload(); // Reload page to reflect logged-in state
        } else {
            alert(data.message); // Display error message
        }
    };

    // AJAX for Registration Form
    document.querySelector("#Registerform").onsubmit = async function (event) {
        event.preventDefault();

        const formData = new FormData(this);
        const response = await fetch(registerUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",

            },
        });
        const data = await response.json();
        if (data.success) {
            alert(data.message); // Display success message
            modal.style.display = "none"; // Close the modal
            location.reload(); // Reload page to reflect logged-in state
        } else {
            alert(data.message); // Display error message
        }
    };

    const listItems = document.querySelectorAll("li#action");

    listItems.forEach(item => {
        item.addEventListener("click", function () {
            // Remove "active" class from all list items
            listItems.forEach(li => li.classList.remove("active"));

            // Add "active" class to the clicked list item
            this.classList.add("active");
        });
    });


});