const exitButton = document.getElementById("exitButton");

exitButton.addEventListener('click', function(e) {
    // Redirect to a new page
    e.preventDefault()
    window.location.href = '/'; // Replace with your desired URL
});
