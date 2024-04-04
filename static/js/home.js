const myForm = document.getElementById("form");
const reloadDiv = document.getElementById("reloadDiv");

myForm.addEventListener("submit", function (event) {
  console.log("Form submitted");
  event.preventDefault();

  // Show the "Page is Reloading" message
  reloadDiv.classList.remove("hidden");

  // Hide the form
  myForm.style.display = "none";

  // Submit the form after a short delay (200ms)
  setTimeout(() => {
    myForm.submit();
  }, 200);
});
