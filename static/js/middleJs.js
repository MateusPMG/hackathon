const acceptButton = document.getElementById("accept-form");
const remakeButton = document.getElementById("remake-form");
const exitButton = document.getElementById("exit-form");

const tables = document.getElementsByClassName("test-cases");
const reloadDiv = document.getElementById("reloadDiv");

const titleS = document.getElementById("success-title");
const titleF = document.getElementById("failure-title");

acceptButton.addEventListener("submit", function (event) {
  console.log("Form submitted");
  event.preventDefault();

  // Show the "Page is Reloading" message
  reloadDiv.classList.remove("hidden");

  tables[0].classList.add("hidden");
  tables[1].classList.add("hidden");
  titleS.classList.add("hidden");
  titleF.classList.add("hidden");

  // Submit the form after a short delay (200ms)
  setTimeout(() => {
    acceptButton.submit();
  }, 200);
});

remakeButton.addEventListener("submit", function (event) {
  console.log("Form submitted");
  event.preventDefault();

  // Show the "Page is Reloading" message
  reloadDiv.classList.remove("hidden");

  tables[0].classList.add("hidden");
  tables[1].classList.add("hidden");
  titleS.classList.add("hidden");
  titleF.classList.add("hidden");

  // Submit the form after a short delay (200ms)
  setTimeout(() => {
    remakeButton.submit();
  }, 200);
});

exitButton.addEventListener("submit", function (event) {
  console.log("Form submitted");
  event.preventDefault();

  // Show the "Page is Reloading" message
  reloadDiv.classList.remove("hidden");

  tables[0].classList.add("hidden");
  tables[1].classList.add("hidden");
  titleS.classList.add("hidden");
  titleF.classList.add("hidden");

  // Submit the form after a short delay (200ms)
  setTimeout(() => {
    exitButton.submit();
  }, 200);
});
