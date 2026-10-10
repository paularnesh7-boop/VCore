<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>VCore</title>
    <style>
      :root {
        --bg-1: #0d0718;
        --bg-2: #1a1030;
        --panel: rgba(27, 19, 43, 0.88);
        --panel-alt: rgba(44, 31, 72, 0.95);
        --primary: #b88cff;
        --primary-2: #7c5cff;
        --secondary: #f7d4ff;
        --text: #f5eefe;
        --muted: #c2b5d9;
        --success: #74f3b0;
        --alert: #ffb37d;
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: Inter, "Segoe UI", sans-serif;
        background: radial-gradient(circle at top, rgba(143, 111, 255, 0.28), transparent 20%), linear-gradient(135deg, var(--bg-1), var(--bg-2));
        color: var(--text);
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .vcore-shell {
        position: relative;
        width: min(1180px, 92vw);
        min-height: 760px;
        background: rgba(18, 12, 29, 0.72);
        border: 1px solid rgba(184, 140, 255, 0.25);
        border-radius: 28px;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(180, 143, 255, 0.1);
        backdrop-filter: blur(12px);
        overflow: hidden;
        animation: fadeRise 0.8s ease-out forwards;
      }

      @keyframes fadeRise {
        from {
          opacity: 0;
          transform: translateY(20px) scale(0.98);
        }
        to {
          opacity: 1;
          transform: translateY(0px) scale(1);
        }
      }

      .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 18px 26px;
        background: rgba(17, 10, 26, 0.6);
        border-bottom: 1px solid rgba(184, 140, 255, 0.12);
      }

      .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }

      .brand-mark {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary), var(--primary-2));
        box-shadow: 0 0 18px rgba(184, 140, 255, 0.8);
      }

      .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(116, 243, 176, 0.12);
        color: var(--success);
        border: 1px solid rgba(116, 243, 176, 0.3);
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      .content {
        display: grid;
        grid-template-columns: 1.2fr 0.8fr;
        gap: 20px;
        padding: 20px;
      }

      .board-panel, .controls-panel {
        background: var(--panel);
        border: 1px solid rgba(184, 140, 255, 0.14);
        border-radius: 22px;
      }

      .board-panel {
        padding: 20px;
      }

      .board {
        position: relative;
        width: 100%;
        aspect-ratio: 1;
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(29, 16, 48, 0.9), rgba(13, 9, 24, 0.9));
        border: 1px solid rgba(184, 140, 255, 0.18);
        overflow: hidden;
      }

      .board:before {
        content: "";
        position: absolute;
        inset: 14px;
        border-radius: 18px;
        border: 2px solid rgba(243, 212, 255, 0.12);
        background: radial-gradient(circle at center, rgba(76, 50, 105, 0.35), rgba(17, 10, 23, 0.9));
      }

      .coin {
        position: absolute;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        box-shadow: inset 0 0 12px rgba(255,255,255,0.18), 0 0 22px rgba(184,140,255,0.2);
      }

      .coin.black { background: #111; }
      .coin.red { background: #d8475a; }
      .coin.white { background: #f7f7ff; }
      .coin.striker { border: 2px solid rgba(255,255,255,0.7); }

      .pocket {
        position: absolute;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: rgba(0,0,0,0.8);
        transform: translate(-50%, -50%);
        border: 2px solid rgba(255,255,255,0.12);
      }

      .chip-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 18px;
      }

      .metric {
        flex: 1;
        padding: 12px 16px;
        border-radius: 14px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(184, 140, 255, 0.12);
      }

      .metric-label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; }
      .metric-value { font-size: 26px; font-weight: 700; margin-top: 8px; }

      .controls-panel {
        padding: 18px;
      }

      .panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
      }

      .panel-header h2 {
        margin: 0;
        font-size: 16px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--muted);
      }

      .toggle {
        width: 54px;
        height: 28px;
        border-radius: 999px;
        background: rgba(255,255,255,0.05);
        position: relative;
        border: 1px solid rgba(184,140,255,0.22);
      }

      .toggle span {
        position: absolute;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary), var(--primary-2));
        left: 6px;
        top: 4px;
      }

      .button-cluster {
        display: flex;
        gap: 10px;
        margin: 18px 0;
      }

      button {
        border: none;
        border-radius: 12px;
        padding: 12px 16px;
        font-weight: 700;
        letter-spacing: 0.04em;
        cursor: pointer;
      }

      .start-btn {
        flex: 1;
        background: linear-gradient(135deg, var(--primary), var(--primary-2));
        color: white;
      }

      .stop-btn {
        flex: 0.6;
        background: rgba(255,255,255,0.06);
        color: var(--text);
        border: 1px solid rgba(184, 140, 255, 0.22);
      }

      .settings {
        display: grid;
        gap: 12px;
        margin-top: 16px;
      }

      .field {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(184, 140, 255, 0.12);
        border-radius: 12px;
        padding: 10px 12px;
      }

      .field label {
        display: flex;
        justify-content: space-between;
        color: var(--muted);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }

      input[type="range"] {
        width: 100%;
        margin-top: 10px;
      }

      .log-box {
        margin-top: 20px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(184, 140, 255, 0.12);
        border-radius: 14px;
        padding: 12px;
      }

      .log-box h3 {
        margin: 0 0 10px;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
      }

      ul {
        list-style: none;
        margin: 0;
        padding: 0;
        display: grid;
        gap: 8px;
      }

      li {
        color: var(--text);
        font-size: 13px;
        opacity: 0.9;
      }
    </style>
  </head>
  <body>
    <div class="vcore-shell">
      <div class="topbar">
        <div class="brand">
          <span class="brand-mark"></span>
          VCore
        </div>
        <div class="status-pill">system online</div>
      </div>

      <div class="content">
        <section class="board-panel">
          <div class="board" id="board">
            <div class="pocket" style="left: 6%; top: 6%;"></div>
            <div class="pocket" style="left: 50%; top: 6%;"></div>
            <div class="pocket" style="left: 94%; top: 6%;"></div>
            <div class="pocket" style="left: 6%; top: 94%;"></div>
            <div class="pocket" style="left: 50%; top: 94%;"></div>
            <div class="pocket" style="left: 94%; top: 94%;"></div>

            <div class="coin black" style="left: 50%; top: 45%;"></div>
            <div class="coin red" style="left: 57%; top: 52%;"></div>
            <div class="coin black" style="left: 54%; top: 40%;"></div>
            <div class="coin black" style="left: 63%; top: 45%;"></div>
            <div class="coin white striker" style="left: 18%; top: 52%;"></div>
          </div>

          <div class="chip-row">
            <div class="metric">
              <div class="metric-label">Detection</div>
              <div class="metric-value">98.4%</div>
            </div>
            <div class="metric">
              <div class="metric-label">Expected Score</div>
              <div class="metric-value">6.8</div>
            </div>
            <div class="metric">
              <div class="metric-label">Loop</div>
              <div class="metric-value">3.1s</div>
            </div>
          </div>
        </section>

        <aside class="controls-panel">
          <div class="panel-header">
            <h2>Controller</h2>
            <div class="toggle"><span></span></div>
          </div>

          <div class="button-cluster">
            <button class="start-btn">Start</button>
            <button class="stop-btn">Stop</button>
          </div>

          <div class="settings">
            <div class="field">
              <label><span>Detection bias</span><span>72%</span></label>
              <input type="range" min="0" max="100" value="72" />
            </div>
            <div class="field">
              <label><span>Shot precision</span><span>84%</span></label>
              <input type="range" min="0" max="100" value="84" />
            </div>
            <div class="field">
              <label><span>Force control</span><span>66%</span></label>
              <input type="range" min="0" max="100" value="66" />
            </div>
          </div>

          <div class="log-box">
            <h3>Execution log</h3>
            <ul>
              <li>Board state stabilized.</li>
              <li>Candidate shot generated: pocket B2.</li>
              <li>Trajectory validated by collision model.</li>
              <li>Action queued for release.</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  </body>
</html>
