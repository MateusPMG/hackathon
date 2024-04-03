const exitButton = document.getElementsByClassName("button-exit")[0];

exitButton.addEventListener("click", function (e) {
  // Redirect to a new page
  e.preventDefault();
  window.location.href = "/"; // Replace with your desired URL
});
