import json
import subprocess
import threading
import time
import webbrowser
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from factory.benchmark import evaluate_models
from factory.generator import synthesize_tasks
from factory.validator import validate_task

HOST = "127.0.0.1"
PORT = 8765

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Coding Task Factory — Innodata Frontier AI Hackathon 2026</title>
  <style>
    :root {
      --bg: #0b0f19;
      --panel: #121826;
      --panel-alt: #182032;
      --border: #263147;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.2);
      --green: #10b981;
      --amber: #f59e0b;
      --red: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
      background: var(--bg);
      color: var(--text);
      padding: 24px;
      line-height: 1.5;
    }
    .container { max-width: 1280px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 22px;
    }
    .title-group h1 { font-size: 1.55rem; font-weight: 700; letter-spacing: -0.02em; }
    .subtitle { color: var(--muted); font-size: 0.9rem; margin-top: 4px; }
    .badge {
      display: inline-block;
      background: rgba(56, 189, 248, 0.12);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.35);
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 600;
      margin-right: 8px;
    }
    .controls {
      display: flex;
      align-items: center;
      gap: 12px;
      background: var(--panel);
      padding: 10px 14px;
      border-radius: 12px;
      border: 1px solid var(--border);
    }
    .controls label { font-size: 0.82rem; color: var(--muted); }
    .controls input, .controls select {
      background: var(--panel-alt);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 6px 10px;
      font-size: 0.88rem;
      width: 78px;
    }
    button.run-btn {
      background: linear-gradient(135deg, #0284c7, #38bdf8);
      color: #06101d;
      font-weight: 700;
      border: none;
      border-radius: 8px;
      padding: 9px 18px;
      font-size: 0.9rem;
      cursor: pointer;
      box-shadow: 0 0 18px var(--accent-glow);
      transition: transform 0.12s ease;
    }
    button.run-btn:hover { transform: translateY(-1px); }
    button.run-btn:disabled { opacity: 0.6; cursor: wait; }

    .stages {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin-bottom: 20px;
    }
    .stage-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: border-color 0.25s ease;
    }
    .stage-card.active { border-color: var(--accent); box-shadow: 0 0 14px var(--accent-glow); }
    .stage-card.done { border-color: var(--green); }
    .stage-title { font-weight: 600; font-size: 0.92rem; }
    .stage-desc { font-size: 0.8rem; color: var(--muted); }
    .status-pill {
      font-size: 0.75rem;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--panel-alt);
      color: var(--muted);
    }
    .stage-card.done .status-pill { background: rgba(16, 185, 129, 0.15); color: var(--green); }
    .stage-card.active .status-pill { background: rgba(56, 189, 248, 0.18); color: var(--accent); }

    .kpis {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 20px;
    }
    .kpi {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
    }
    .kpi-label { font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
    .kpi-val { font-size: 1.7rem; font-weight: 700; margin-top: 6px; color: #fff; }
    .kpi-sub { font-size: 0.78rem; color: var(--green); margin-top: 2px; }

    .grid-main {
      display: grid;
      grid-template-columns: 1fr 1.35fr;
      gap: 18px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px;
    }
    .panel h2 { font-size: 1.02rem; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; }
    table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid var(--border); }
    th { color: var(--muted); font-weight: 600; font-size: 0.78rem; text-transform: uppercase; }
    .bar-bg { width: 100%; height: 8px; background: var(--panel-alt); border-radius: 999px; overflow: hidden; margin-top: 6px; }
    .bar-fill { height: 100%; border-radius: 999px; transition: width 0.5s ease; }

    .task-selector {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 14px;
      max-height: 86px;
      overflow-y: auto;
    }
    .task-chip {
      background: var(--panel-alt);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 5px 10px;
      border-radius: 8px;
      font-size: 0.78rem;
      cursor: pointer;
    }
    .task-chip.selected { border-color: var(--accent); background: rgba(56, 189, 248, 0.15); color: var(--accent); font-weight: 600; }
    .meta-row { display: flex; gap: 8px; margin-bottom: 10px; font-size: 0.8rem; }
    .tag { padding: 2px 8px; border-radius: 6px; background: var(--panel-alt); border: 1px solid var(--border); }
    .prompt-box {
      background: var(--panel-alt);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      font-size: 0.86rem;
      margin-bottom: 12px;
    }
    pre {
      background: #080b12;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      font-family: "SF Mono", Menlo, monospace;
      font-size: 0.79rem;
      overflow-x: auto;
      color: #cbd5e1;
      max-height: 210px;
    }
    .code-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .code-label { font-size: 0.76rem; color: var(--muted); margin-bottom: 4px; font-weight: 600; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="title-group">
        <div>
          <span class="badge">Coding Task Factory</span>
          <span class="badge">Innodata Frontier AI Hackathon 2026</span>
        </div>
        <h1 style="margin-top:8px;">Automated Synthetic Coding Benchmark &amp; Sandbox Factory</h1>
        <div class="subtitle">Author: Bharath Kumar R &bull; Repository: github.com/itsmerbk/coding-task-factory</div>
      </div>
      <div class="controls">
        <div>
          <label>Tasks</label><br/>
          <input type="number" id="taskCount" value="15" min="3" max="60" />
        </div>
        <div>
          <label>Seed</label><br/>
          <input type="number" id="taskSeed" value="2026" />
        </div>
        <button class="run-btn" id="runBtn" onclick="runPipeline()">&#9654; Run Live Pipeline</button>
      </div>
    </header>

    <div class="stages">
      <div class="stage-card" id="st1">
        <div>
          <div class="stage-title">1. Task Synthesizer</div>
          <div class="stage-desc">Parameterized multi-domain generation</div>
        </div>
        <span class="status-pill" id="st1-pill">READY</span>
      </div>
      <div class="stage-card" id="st2">
        <div>
          <div class="stage-title">2. AST &amp; Sandbox Gate</div>
          <div class="stage-desc">Isolated -I runner + anti-stub check</div>
        </div>
        <span class="status-pill" id="st2-pill">READY</span>
      </div>
      <div class="stage-card" id="st3">
        <div>
          <div class="stage-title">3. Frontier Model Eval</div>
          <div class="stage-desc">Automated pass@1 benchmark harness</div>
        </div>
        <span class="status-pill" id="st3-pill">READY</span>
      </div>
    </div>

    <div class="kpis">
      <div class="kpi">
        <div class="kpi-label">Generated Tasks</div>
        <div class="kpi-val" id="kpiGen">—</div>
        <div class="kpi-sub">Algorithms &bull; Security &bull; Data Structures</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Sandbox Verified</div>
        <div class="kpi-val" id="kpiVer">—</div>
        <div class="kpi-sub">100% Reference Pass + Stub Rejected</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Top Model pass@1</div>
        <div class="kpi-val" id="kpiTop">—</div>
        <div class="kpi-sub">frontier-model-alpha</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Execution Time</div>
        <div class="kpi-val" id="kpiTime">—</div>
        <div class="kpi-sub">Subprocess isolation (2.0s cap)</div>
      </div>
    </div>

    <div class="grid-main">
      <div class="panel">
        <h2>Frontier Model Benchmark (pass@1) <span style="font-size:0.78rem;color:var(--muted);">results/benchmark_results.json</span></h2>
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>Passed</th>
              <th>pass@1</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody id="benchBody"></tbody>
        </table>
        <div style="margin-top:18px;">
          <div class="code-label">Validation Gate Telemetry (results/validation_report.json)</div>
          <pre id="valLogBox">Click "Run Live Pipeline" to inspect validation telemetry...</pre>
        </div>
      </div>

      <div class="panel">
        <h2>Verified Task Inspector <span style="font-size:0.78rem;color:var(--muted);">results/verified_tasks.jsonl</span></h2>
        <div class="task-selector" id="taskChips"></div>
        <div class="meta-row" id="taskMeta"></div>
        <div class="prompt-box" id="taskPrompt">Loading synthesized task...</div>
        <div class="code-grid">
          <div>
            <div class="code-label">Reference Solution (AST Checked)</div>
            <pre id="taskRef"></pre>
          </div>
          <div>
            <div class="code-label">Adversarial Unit Test Harness</div>
            <pre id="taskTests"></pre>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    let currentTasks = [];

    function setStage(id, state, label) {
      const card = document.getElementById(id);
      const pill = document.getElementById(id + '-pill');
      card.className = 'stage-card ' + state;
      pill.textContent = label;
    }

    function selectTask(idx) {
      const t = currentTasks[idx];
      if (!t) return;
      document.querySelectorAll('.task-chip').forEach((el, i) => {
        el.classList.toggle('selected', i === idx);
      });
      document.getElementById('taskMeta').innerHTML =
        `<span class="tag">ID: <b>${t.task_id}</b></span>` +
        `<span class="tag">Domain: <b>${t.domain}</b></span>` +
        `<span class="tag">Difficulty: <b>${t.difficulty.toUpperCase()}</b></span>` +
        `<span class="tag" style="color:var(--green);border-color:var(--green);">VERIFIED</span>`;
      document.getElementById('taskPrompt').textContent = t.prompt;
      document.getElementById('taskRef').textContent = t.reference_solution;
      document.getElementById('taskTests').textContent = t.test_code;
    }

    async function runPipeline() {
      const btn = document.getElementById('runBtn');
      btn.disabled = true;
      const count = parseInt(document.getElementById('taskCount').value || '15', 10);
      const seed = parseInt(document.getElementById('taskSeed').value || '2026', 10);

      setStage('st1', 'active', 'SYNTHESIZING...');
      setStage('st2', '', 'QUEUED');
      setStage('st3', '', 'QUEUED');

      const t0 = performance.now();
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count, seed })
      });
      const data = await res.json();
      const elapsed = ((performance.now() - t0) / 1000).toFixed(2) + 's';

      setStage('st1', 'done', `${data.generated_count} TASKS`);
      await new Promise(r => setTimeout(r, 220));
      setStage('st2', 'done', `${data.verified_tasks.length} VERIFIED`);
      await new Promise(r => setTimeout(r, 220));
      setStage('st3', 'done', 'COMPLETE');

      document.getElementById('kpiGen').textContent = data.generated_count;
      document.getElementById('kpiVer').textContent = `${data.verified_tasks.length}/${data.generated_count}`;
      document.getElementById('kpiTime').textContent = elapsed;

      const tbody = document.getElementById('benchBody');
      tbody.innerHTML = '';
      let topScore = 0;
      for (const [model, stats] of Object.entries(data.benchmark)) {
        if (stats.pass_at_1 > topScore) topScore = stats.pass_at_1;
        const color = stats.pass_at_1 >= 90 ? 'var(--green)' : (stats.pass_at_1 >= 50 ? 'var(--amber)' : 'var(--red)');
        const failCount = stats.failures.length;
        tbody.innerHTML += `
          <tr>
            <td><b>${model}</b></td>
            <td>${stats.passed} / ${stats.total}</td>
            <td style="width:34%;">
              <b>${stats.pass_at_1}%</b>
              <div class="bar-bg"><div class="bar-fill" style="width:${stats.pass_at_1}%;background:${color};"></div></div>
            </td>
            <td style="font-size:0.78rem;color:${failCount === 0 ? 'var(--green)' : 'var(--muted)'};">
              ${failCount === 0 ? '0 failures' : failCount + ' assertion fails'}
            </td>
          </tr>`;
      }
      document.getElementById('kpiTop').textContent = topScore + '%';

      document.getElementById('valLogBox').textContent = JSON.stringify(data.validation.slice(0, 6), null, 2);

      currentTasks = data.verified_tasks;
      const chips = document.getElementById('taskChips');
      chips.innerHTML = currentTasks.map((t, i) =>
        `<button class="task-chip" onclick="selectTask(${i})">${t.task_id}</button>`
      ).join('');
      selectTask(0);
      btn.disabled = false;
    }

    window.addEventListener('DOMContentLoaded', runPipeline);
  </script>
</body>
</html>
"""

class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True

class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    def do_POST(self):
        if self.path != "/api/run":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
        count = max(3, min(60, int(payload.get("count", 15))))
        seed = int(payload.get("seed", 2026))

        raw_tasks = synthesize_tasks(count=count, seed=seed)
        verified = []
        validation = []
        for task in raw_tasks:
            ok, status = validate_task(task)
            validation.append({
                "task_id": task.task_id,
                "domain": task.domain,
                "difficulty": task.difficulty,
                "status": status,
            })
            if ok:
                verified.append(task)

        models = ["frontier-model-alpha", "frontier-model-beta", "baseline-model-lite"]
        benchmark = evaluate_models(verified, models)

        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        with (results_dir / "verified_tasks.jsonl").open("w", encoding="utf-8") as f:
            for t in verified:
                f.write(json.dumps(asdict(t)) + "\n")
        (results_dir / "validation_report.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
        (results_dir / "benchmark_results.json").write_text(json.dumps(benchmark, indent=2), encoding="utf-8")

        response = {
            "generated_count": len(raw_tasks),
            "verified_tasks": [asdict(t) for t in verified],
            "validation": validation,
            "benchmark": benchmark,
        }
        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def open_browser_and_recorder():
    time.sleep(0.8)
    webbrowser.open(f"http://{HOST}:{PORT}")
    time.sleep(1.0)
    subprocess.run(["open", "-a", "Screenshot"], check=False)

if __name__ == "__main__":
    print(f"Serving Coding Task Factory Dashboard at http://{HOST}:{PORT}")
    print("Press Ctrl+C in Terminal after you finish recording your screen.")
    threading.Thread(target=open_browser_and_recorder, daemon=True).start()
    server = ReusableHTTPServer((HOST, PORT), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard server stopped.")
