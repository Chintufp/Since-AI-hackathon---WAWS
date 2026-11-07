const examples = [
  "Can you tell me about the medicine I was prescribed and explain why I was given it, based on the medical records below?\nPATIENT DETAILS\nName: Alex Bennett\nDate of birth: 14 June 1995\nPatient number: PT-482071\nEmail: alex.bennett@example.com\n\nVISIT — 29 October 2026\nReason: Runny nose and frequent sneezing.\nMedication prescribed: Cetirizine.\nFollow-up: Contact the clinic if symptoms persist.\n\nVISIT — 14 September 2026\nReason: Persistent itching around the anus.\nPatient reports: “My ass is really itchy, especially at night.”\nExamination and follow-up notes recorded separately.\n\nVISIT — 20 May 2026\nReason: Left wrist pain after a fall while cycling.\nAssessment: Wrist sprain.\nFollow-up: Symptoms improving.",
  "What are the three main things our customers are complaining about in these support tickets? Count the tickets in each category and suggest one practical improvement for each.\n\nHere’s the export from our support system:\n\ncustomer_id,customer_name,email,complaint\nC-1042,Emma Wilson,emma.wilson@example.com,\"I was charged twice for the same order. Please refund the extra payment.\"\nC-2087,Oliver Davis,oliver.davis@example.com,\"I returned my order two weeks ago and still haven’t received my refund. Please send an update to oliver.davis@example.com.\"\nC-3156,Sofia Martin,sofia.martin@example.com,\"The password-reset email never arrives, so I can’t get into my account.\"\nC-4093,Noah Taylor,noah.taylor@example.com,\"My payment failed on screen, so I tried again. Now I can see two charges for one order.\"\nC-5028,Amelia Brown,amelia.brown@example.com,\"Support confirmed my refund ten days ago, but the money still hasn’t arrived.\"\nC-6074,Lucas Harris,lucas.harris@example.com,\"Hi, Lucas Harris here. I’ve been billed twice for a single purchase and need the duplicate charge reversed.\""
];
const message = document.getElementById("message");
const output = document.getElementById("output");
const filter = document.getElementById("filter");
const example = document.getElementById("example");
const pageId = crypto.randomUUID();
let exampleIndex = 0, revision = 0, controller = null, timers = [];
function clearTimers() { timers.forEach(clearTimeout); timers = []; }
function reset() {
  revision++; controller?.abort(); controller = null; clearTimers();
  output.hidden = true; output.replaceChildren(); message.hidden = false;
  filter.textContent = "Filter"; filter.title = ""; filter.disabled = !message.value.trim();
  message.setAttribute("aria-busy", "false");
  void fetch("/api/reset", { method: "POST", headers: { "Content-Type": "application/json", "X-Mask-Request": "preview", "X-Mask-Client": pageId }, body: "{}" }).catch(() => {});
}
function showProtected(text) {
  output.replaceChildren();
  let cursor = 0;
  for (const match of text.matchAll(/\[[A-Z]+(?:_\d+)?\]/g)) {
    output.append(document.createTextNode(text.slice(cursor, match.index)));
    const token = document.createElement("span"); token.className = "token"; token.textContent = match[0]; output.append(token);
    cursor = match.index + match[0].length;
  }
  output.append(document.createTextNode(text.slice(cursor)));
}
function transform(data, source, version) {
  message.hidden = true; output.hidden = false; output.replaceChildren();
  const finish = () => {
    if (version !== revision) return;
    showProtected(data.protected_text); message.value = data.protected_text;
    filter.textContent = "Filter"; filter.disabled = true; controller = null;
    message.setAttribute("aria-busy", "false");
  };
  const parts = data.protected_view?.message;
  if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches || !Array.isArray(parts) || !parts.some(p => Number.isInteger(p.start))) { finish(); return; }
  const characters = Array.from(source);
  for (const part of parts) {
    if (!Number.isInteger(part.start)) { output.append(document.createTextNode(part.text)); continue; }
    const span = document.createElement("span");
    span.textContent = characters.slice(part.start, part.end).join(""); output.append(span);
    if (part.action === "DROP") {
      span.replaceChildren(...Array.from(span.textContent, letter => {
        const dust = document.createElement("span"); dust.className = "dust"; dust.textContent = letter; return dust;
      }));
    } else timers.push(setTimeout(() => {
      if (version !== revision) return;
      span.textContent = part.text; span.className = "token morph";
    }, 230));
  }
  timers.push(setTimeout(finish, 800));
}
async function protect() {
  if (filter.disabled || !message.value.trim()) return;
  const version = revision, source = message.value;
  controller = new AbortController(); const requestController = controller;
  filter.disabled = true; filter.textContent = "Filtering…"; message.setAttribute("aria-busy", "true");
  const timeout = setTimeout(() => requestController.abort(), 60000);
  try {
    // The opening request is local task context; the complete message is still scanned.
    const task = source.split("\n")[0].trim();
    const response = await fetch("/api/preview", {
      method: "POST", headers: { "Content-Type": "application/json", "X-Mask-Request": "preview", "X-Mask-Client": pageId },
      body: JSON.stringify({ text: source, task }), signal: requestController.signal, cache: "no-store",
    });
    const data = await response.json();
    if (version !== revision) return;
    if (!response.ok || !data.coverage?.complete || !["ready", "needs_review"].includes(data.status) || typeof data.protected_text !== "string") throw new Error("No complete preview. Try a shorter message.");
    transform(data, source, version);
  } catch (error) {
    if (version !== revision) return;
    filter.textContent = "Couldn’t filter — try again";
    filter.title = error.name === "AbortError" ? "The local model timed out." : "The local model could not complete this message.";
    filter.disabled = false; controller = null; message.setAttribute("aria-busy", "false");
  } finally { clearTimeout(timeout); }
}
message.addEventListener("input", reset);
filter.addEventListener("click", () => void protect());
example.addEventListener("click", () => {
  message.value = examples[exampleIndex]; exampleIndex = (exampleIndex + 1) % examples.length;
  reset(); message.scrollTop = 0;
  example.title = exampleIndex === 1 ? "Next example: support tickets" : "Next example: medical records";
});
function edit() {
  if (controller) return;
  output.hidden = true; message.hidden = false; message.focus();
}
output.addEventListener("click", edit);
output.addEventListener("keydown", event => { if (event.key === "Enter") { event.preventDefault(); edit(); } });
