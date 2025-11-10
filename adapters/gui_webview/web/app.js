(() => {
  const simForm = document.querySelector("#simForm");
  const jobsInput = document.querySelector("#jobsInput");
  const algoSelect = document.querySelector("#algoSelect");
  const quantumInput = document.querySelector("#quantumInput");
  const simOutput = document.querySelector("#simOutput");
  const runSimBtn = document.querySelector("#runSimBtn");
  const clearSimBtn = document.querySelector("#clearSimBtn");

  const fsForm = document.querySelector("#fsForm");
  const fsCommandInput = document.querySelector("#fsCommandInput");
  const fsLog = document.querySelector("#fsLog");

  const api = window.pywebview?.api ?? buildMockApi();

  algoSelect.addEventListener("change", () => toggleQuantum(algoSelect.value));
  toggleQuantum(algoSelect.value);

  simForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const jobs = parseJobs(jobsInput.value);
    if (!jobs.length) {
      showSimOutput("Agrega al menos un proceso antes de ejecutar.");
      return;
    }
    const payload = {
      algorithm: algoSelect.value,
      quantum: parseQuantum(),
      jobs,
    };
    await withPendingState(runSimBtn, async () => {
      const response = await api.run_simulation(payload);
      if (!response.ok) {
        showSimOutput(`Error: ${response.error}`);
        return;
      }
      showSimOutput(formatMetrics(response.metrics));
    });
  });

  clearSimBtn.addEventListener("click", () => {
    jobsInput.value = "";
    showSimOutput("Procesos limpiados.");
  });

  fsForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const value = fsCommandInput.value.trim();
    if (!value) {
      return;
    }
    const [command, ...args] = value.split(/\s+/);
    appendFsLog(`fs> ${value}`, "prompt");
    fsCommandInput.value = "";
    const response = await api.execute_fs(command, args);
    if (!response.ok) {
      appendFsLog(response.error, "error");
    } else if (response.output) {
      appendFsLog(response.output);
    }
    fsLog.scrollTop = fsLog.scrollHeight;
  });

  function parseJobs(text) {
    return text
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [pid, arrival, burst, priority] = line.split(",").map((token) => token?.trim());
        return {
          pid: Number(pid ?? 0) || undefined,
          arrival: Number(arrival ?? 0) || 0,
          burst: Number(burst ?? 1) || 1,
          priority: priority === undefined || priority === "" ? null : Number(priority),
        };
      });
  }

  function formatMetrics(metrics) {
    if (!metrics) {
      return "No se recibieron métricas.";
    }
    return JSON.stringify(metrics, null, 2);
  }

  function showSimOutput(message) {
    simOutput.textContent = message;
  }

  function toggleQuantum(algo) {
    const rr = algo === "rr";
    quantumInput.disabled = !rr;
    if (!rr) {
      quantumInput.value = "";
    }
  }

  function parseQuantum() {
    const value = Number(quantumInput.value);
    return Number.isFinite(value) && value > 0 ? value : null;
  }

  function appendFsLog(text, variant = "") {
    const entry = document.createElement("div");
    if (variant) {
      entry.classList.add(variant);
    }
    entry.textContent = text;
    fsLog.appendChild(entry);
  }

  async function withPendingState(button, callback) {
    button.disabled = true;
    button.dataset.originalText = button.dataset.originalText || button.textContent;
    button.textContent = "Procesando...";
    try {
      await callback();
    } finally {
      button.disabled = false;
      button.textContent = button.dataset.originalText;
    }
  }

  function buildMockApi() {
    console.warn("PyWebview API no disponible. Usando stubs para desarrollo.");
    return {
      async run_simulation(payload) {
        return {
          ok: true,
          metrics: {
            payload,
            note: "Stub local. Lanza desde PyWebview para datos reales.",
          },
        };
      },
      async execute_fs(command, args) {
        return {
          ok: true,
          output: `Simulado (${command} ${args.join(" ")})`,
        };
      },
    };
  }
})();
