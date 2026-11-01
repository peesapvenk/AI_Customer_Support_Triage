const form = document.querySelector("#ticket-form");
const message = document.querySelector("#message");
const submitButton = document.querySelector("#submit-button");
const clearButton = document.querySelector("#clear-button");
const errorBox = document.querySelector("#error");
const statusText = document.querySelector("#status");
const emptyState = document.querySelector("#empty-state");
const result = document.querySelector("#result");
const resultPanel = document.querySelector(".result-panel");

const teamNames = {
  billing: "Billing",
  technical_support: "Technical support",
  account_access: "Account access",
  general_inquiry: "General inquiry",
  feature_request: "Feature request",
};
let busy = false;

function setBusy(value) {
  busy = value;
  submitButton.disabled = value;
  clearButton.disabled = value;
  message.readOnly = value;
  resultPanel.setAttribute("aria-busy", String(value));
  submitButton.textContent = value ? "Classifying…" : "Classify ticket →";
}

message.addEventListener("input", () => message.setCustomValidity(""));
message.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    if (!busy) form.requestSubmit();
  }
});

form.addEventListener("reset", () => {
  message.setCustomValidity("");
  errorBox.hidden = true;
  result.hidden = true;
  emptyState.hidden = false;
  statusText.textContent = "Your classification will appear here.";
  message.focus();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;

  const ticket = message.value.trim();
  if (!ticket) {
    message.setCustomValidity("Please enter a ticket before classifying.");
    message.reportValidity();
    return;
  }

  errorBox.hidden = true;
  result.hidden = true;
  emptyState.hidden = true;
  statusText.textContent = "Classifying your ticket and drafting a reply…";
  setBusy(true);

  try {
    const response = await fetch("/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: ticket }),
    });
    const data = await response.json();
    if (!response.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((issue) => issue.msg).join(" ")
        : data.detail;
      throw new Error(detail || "Could not classify this ticket. Please try again.");
    }

    const classification = data.classification;
    // Model output is displayed as plain text, never as HTML.
    document.querySelector("#team").textContent = teamNames[classification.team] || classification.team;
    const priority = document.querySelector("#priority");
    priority.textContent = classification.priority;
    priority.dataset.priority = classification.priority;
    document.querySelector("#reason").textContent = classification.reason;
    document.querySelector("#reply").textContent = classification.suggested_reply;

    const usageDetails = document.querySelector("#usage-details");
    usageDetails.hidden = !data.usage;
    usageDetails.open = false;
    if (data.usage) {
      document.querySelector("#usage").textContent =
        `Input: ${data.usage.input_tokens} · Output: ${data.usage.output_tokens} · Total: ${data.usage.total_tokens}`;
    }
    result.hidden = false;
    statusText.textContent = "Classification complete.";
  } catch (error) {
    errorBox.textContent = error instanceof TypeError || error instanceof SyntaxError
      ? "Could not get a response from the server. Check that it is running and try again."
      : error.message;
    errorBox.hidden = false;
    statusText.textContent = "Classification could not be completed. Please try again.";
  } finally {
    setBusy(false);
  }
});
