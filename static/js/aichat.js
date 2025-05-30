const body = document.querySelector("body"),
  aichat = document.querySelector(".aichat"),
  chatToggle = document.querySelector(".aichat header .toggle");
(messageInput = document.querySelector(".message-input")),
  (chatBody = document.querySelector(".chat-body")),
  (sendMessage = document.querySelector(".send-message"));

const userData = {
  message: null,
};

const createMessageElement = (content, ...classes) => {
  const div = document.createElement("div");
  div.classList.add("message", ...classes);
  div.innerHTML = content;
  return div;
};

const generateBotResponse = async (incomingMessageDiv) => {
  const messageElement = incomingMessageDiv.querySelector(".message-text");

  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userData.message }),
  };

  try {
    const response = await fetch("/aichatapi", requestOptions);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error.message);
    const apiResponseText = data.response;
    messageElement.innerText = apiResponseText;
  } catch (error) {
    console.log(error);
  }
};

const handleOutgoingMessage = (e) => {
  e.preventDefault();
  userData.message = messageInput.value.trim();
  messageInput.value = "";

  const messageContent = `<div class="message-text"></div>`;

  const outgoingMessageDiv = createMessageElement(messageContent, "user-message", "thinking");
  outgoingMessageDiv.querySelector(".message-text").textContent = userData.message;
  chatBody.appendChild(outgoingMessageDiv);

  setTimeout(() => {
    const messageContent = `<i class="bx bx-bot icon"></i>
                    <div class="message-text">
                        <div class="thinking-indicator">
                            <div class="dot"></div>
                            <div class="dot"></div>
                            <div class="dot"></div>
                        </div>
                    </div>`;

    const incomingMessageDiv = createMessageElement(messageContent, "bot-message");
    chatBody.appendChild(incomingMessageDiv);
    generateBotResponse(incomingMessageDiv);
  }, 600);
};

messageInput.addEventListener("keydown", (e) => {
  const userMessage = e.target.value.trim();
  if (e.key == "Enter" && userMessage) {
    handleOutgoingMessage(e);
  }
});

sendMessage.addEventListener("click", (e) => handleOutgoingMessage(e));
