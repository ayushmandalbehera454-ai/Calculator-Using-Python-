(() => {
  const LAYOUT = [
    ["C", "⌫", "(", ")"],
    ["7", "8", "9", "÷"],
    ["4", "5", "6", "×"],
    ["1", "2", "3", "-"],
    ["0", ".", "^", "+"],
    ["√", "%", "ANS", "="],
  ];
  const STORAGE_KEY = "calculator-history";

  const expr = document.getElementById("expr");
  const out = document.getElementById("out");
  const keys = document.getElementById("keys");
  const tapeList = document.getElementById("tape-list");
  const tapeEmpty = document.getElementById("tape-empty");
  let lastAnswer = "0";
  let history = loadHistory();

  function loadHistory() {
    try {
      const data = JSON.parse(localStorage.getItem(STORAGE_KEY));
      return Array.isArray(data) ? data : [];
    } catch (_) { return []; }
  }
  function saveHistory() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(-50))); } catch (_) {}
  }

  function renderHistory() {
    tapeList.textContent = "";
    history.slice().reverse().forEach((item) => {
      const li = document.createElement("li");
      li.tabIndex = 0;
      li.textContent = item.expression;
      const strong = document.createElement("strong");
      strong.textContent = "= " + item.result;
      li.appendChild(strong);
      const reuse = () => { expr.value = item.expression; expr.focus(); };
      li.addEventListener("click", reuse);
      li.addEventListener("keydown", (e) => { if (e.key === "Enter") reuse(); });
      tapeList.appendChild(li);
    });
    tapeEmpty.hidden = history.length > 0;
  }

  function showMessage(text, isError) {
    out.textContent = text;
    out.classList.toggle("error", Boolean(isError));
  }

  async function equals() {
    const expression = expr.value.trim();
    if (!expression) return;
    try {
      const res = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ expression }),
      });
      const data = await res.json();
      if (!res.ok) { showMessage(data.error || "Something went wrong", true); return; }
      lastAnswer = data.result;
      history.push({ expression, result: data.result });
      saveHistory();
      renderHistory();
      expr.value = data.result;
      showMessage("", false);
    } catch (_) {
      showMessage("Can't reach the server. Check your connection.", true);
    }
  }

  function press(label) {
    if (label === "=") return equals();
    if (label === "C") { expr.value = ""; showMessage("", false); }
    else if (label === "⌫") expr.value = expr.value.slice(0, -1);
    else if (label === "√") expr.value += "sqrt(";
    else if (label === "ANS") expr.value += lastAnswer;
    else expr.value += label;
    expr.focus();
  }

  LAYOUT.flat().forEach((label) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = label;
    if ("÷×-+^%√".includes(label)) b.classList.add("op");
    if (label === "=") b.classList.add("eq");
    if (label === "C") b.classList.add("clear");
    b.addEventListener("click", () => press(label));
    keys.appendChild(b);
  });

  expr.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); equals(); }
    if (e.key === "Escape") press("C");
  });
  document.getElementById("clear-tape").addEventListener("click", () => {
    history = []; saveHistory(); renderHistory();
  });

  renderHistory();
  expr.focus();
})();
