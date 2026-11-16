console.log("Content script loaded");

// ---------------- TEXT CLEANING ----------------
function cleanText(text) {
  return text
    .replace(/[*#\-]/g, "")
    .replace(/\d+\./g, "")
    .replace(/\n+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}


// ---------------- TEXT TO SPEECH ----------------
function speak(text) {
  const cleaned = cleanText(text);

  const utterance = new SpeechSynthesisUtterance(cleaned);

  const voices = speechSynthesis.getVoices();

  // 🔥 CHANGE THIS NAME based on what you see in console
  const selectedVoice = voices.find(
    voice => voice.name === "Google UK English Female"
  );

  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }

  utterance.rate = 1;
  utterance.pitch = 1;
  utterance.volume = 1;

  speechSynthesis.cancel();
  speechSynthesis.speak(utterance);
}


// ---------------- PAGE STRUCTURE ----------------
function getPageStructure() {
  const headings = [...document.querySelectorAll("h1, h2, h3")]
    .map(h => h.innerText.trim())
    .filter(Boolean);

  const buttons = [...document.querySelectorAll("button, input[type=submit]")]
    .map(b => (b.innerText || b.value || "").trim())
    .filter(Boolean);

  const links = [...document.querySelectorAll("a")]
    .map(a => a.innerText.trim())
    .filter(text => text.length > 0)
    .slice(0, 20);

  return { headings, buttons, links };
}


// ---------------- SUMMARIZATION ----------------
function sendForSummary() {
  const text = document.body.innerText.slice(0, 5000);
  const structure = getPageStructure();

  chrome.runtime.sendMessage(
    {
      type: "SUMMARIZE",
      text: text,
      structure: structure
    },
    (response) => {
      if (chrome.runtime.lastError) {
        console.error("Error:", chrome.runtime.lastError.message);
        return;
      }

      if (response && response.summary) {
        console.log("Summary:", response.summary);
        speak(response.summary);
      } else {
        console.log("No response received");
      }
    }
  );
}


// ---------------- MESSAGE LISTENER ----------------
chrome.runtime.onMessage.addListener((request) => {
  if (request.type === "TRIGGER_SUMMARY") {
    sendForSummary();
  }
});


// ---------------- SMART INPUT FILL ----------------
function findBestInputField(keyword) {
  const inputs = document.querySelectorAll("input, textarea");

  for (let input of inputs) {
    const label = input.labels?.[0]?.innerText?.toLowerCase() || "";
    const name = input.name?.toLowerCase() || "";
    const placeholder = input.placeholder?.toLowerCase() || "";

    if (
      label.includes(keyword) ||
      name.includes(keyword) ||
      placeholder.includes(keyword)
    ) {
      return input;
    }
  }

  return null;
}


// ---------------- NAVIGATION (NEW FEATURE) ----------------
function findElementByText(keyword) {
  const synonyms = {
    login: ["login", "sign in", "log in"],
    signup: ["sign up", "register", "create account"],
    submit: ["submit", "continue", "next"]
  };

  const words = synonyms[keyword] || [keyword];

  const elements = document.querySelectorAll(
    "a, button, input[type=button], input[type=submit]"
  );

  for (let el of elements) {
    const text = (el.innerText || el.value || "").toLowerCase();

    for (let word of words) {
      if (text.includes(word)) {
        return el;
      }
    }
  }

  return null;
}

function scrollToElement(el) {
  el.scrollIntoView({ behavior: "smooth", block: "center" });

  el.style.outline = "3px solid red";
  el.style.backgroundColor = "yellow";

  setTimeout(() => {
    el.style.outline = "";
    el.style.backgroundColor = "";
  }, 3000);
}


// ---------------- COMMAND HANDLER ----------------
function handleCommand(command) {

  if (command.includes("summarize")) {
    sendForSummary();
  }

  else if (command.includes("scroll down")) {
    window.scrollBy(0, 500);
    speak("Scrolling down");
  }

  else if (command.includes("scroll up")) {
    window.scrollBy(0, -500);
    speak("Scrolling up");
  }

  else if (command.includes("click submit")) {
    const btn = document.querySelector("button[type=submit], input[type=submit]");
    if (btn) {
      btn.click();
      speak("Submitting form");
    } else {
      speak("Submit button not found");
    }
  }

  else if (command.includes("enter name")) {
    const value = command.replace("enter name", "").trim();
    const field = findBestInputField("name");

    if (field) {
      field.value = value;
      speak("Name entered");
    } else {
      speak("Name field not found");
    }
  }

  else if (command.includes("enter email")) {
    const value = command.replace("enter email", "").trim();
    const field = findBestInputField("email");

    if (field) {
      field.value = value;
      speak("Email entered");
    } else {
      speak("Email field not found");
    }
  }

  // 🔥 NEW: NAVIGATION COMMAND
  else if (command.includes("go to")) {
    const target = command.replace("go to", "").trim();

    const element = findElementByText(target);

    if (element) {
      scrollToElement(element);
      speak(`Navigating to ${target}`);
    } else {
      speak(`Could not find ${target}`);
    }
  }

  else {
    console.log("Unknown command:", command);
  }
}


// ---------------- VOICE RECOGNITION ----------------
let recognition;

function startVoiceRecognition() {
  if (!("webkitSpeechRecognition" in window)) {
    alert("Speech recognition not supported in this browser");
    return;
  }

  recognition = new webkitSpeechRecognition();
  recognition.continuous = true;
  recognition.lang = "en-IN";

  recognition.onresult = function(event) {
    const command =
      event.results[event.results.length - 1][0].transcript.toLowerCase().trim();

    console.log("Voice Command:", command);
    handleCommand(command);
  };

  recognition.onerror = function(event) {
    console.error("Speech recognition error:", event.error);
  };

  recognition.start();
}


// ---------------- START AFTER USER INTERACTION ----------------
document.addEventListener("click", () => {
  if (!recognition) {
    startVoiceRecognition();
    console.log("Voice recognition started");
  }
});