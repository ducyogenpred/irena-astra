const input = document.querySelector(".chatBoxInput"),
  button = document.querySelector(".btn_submit");

input.addEventListener("keydown", (e) => {
  if (e.key == "Enter") {
    input.value = "";
  }
});

button.addEventListener("click", () => {
  window.location.href = "/aichat.html";
  input.value = "";
});
