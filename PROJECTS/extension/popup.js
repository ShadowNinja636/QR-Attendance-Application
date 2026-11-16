document.getElementById("summarize").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  try {
    // Inject content.js manually
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content.js"]
    });

    console.log("Content script injected");

    // Now send message
    chrome.tabs.sendMessage(
      tab.id,
      { type: "TRIGGER_SUMMARY" },
      (response) => {
        if (chrome.runtime.lastError) {
          console.error("Message error:", chrome.runtime.lastError.message);
        }
      }
    );

  } catch (err) {
    console.error("Injection failed:", err);
  }
});