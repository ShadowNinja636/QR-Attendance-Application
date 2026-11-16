// ---------------- GEMINI API KEY ----------------
const GEMINI_API_KEY = "AIzaSyDRkuABARU4LJfhCPk64ULa40qUF5ojQsc";


// ---------------- SUMMARIZATION FUNCTION ----------------
async function summarizeText(text, structure) {
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: `
You are a voice assistant for visually impaired users.

Explain this webpage naturally like a human would speak.

Rules:
- Do NOT use bullet points
- Do NOT use numbers
- Do NOT use special characters like *, -, #
- Do NOT repeat the question
- Speak conversationally

Keep it short, clear, and natural.

Page details:
Headings: ${structure?.headings?.join(", ") || "None"}
Buttons: ${structure?.buttons?.join(", ") || "None"}
Links: ${structure?.links?.join(", ") || "None"}

Content:
${text}
`
                }
              ]
            }
          ]
        })
      }
    );

    const data = await response.json();

    console.log("FULL GEMINI RESPONSE:", data);

    return (
      data.candidates?.[0]?.content?.parts?.[0]?.text ||
      JSON.stringify(data.error) ||
      "No summary available."
    );

  } catch (error) {
    console.error("Gemini error:", error);
    return "Sorry, I could not generate a summary.";
  }
}


// ---------------- MESSAGE LISTENER ----------------
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "SUMMARIZE") {
    summarizeText(request.text, request.structure)
      .then(summary => sendResponse({ summary }))
      .catch(() => sendResponse({ summary: "Error generating summary." }));

    return true; // required for async
  }
});