const $ = (id) => document.getElementById(id);
let result,
  baseline,
  playing = false,
  cursor = 12,
  animation,
  runCount = 0;
const colors = { selected: "#b5522f", baseline: "#91a0a2", bess: "#416e91" };
const config = () => ({
  scenario: $("scenario").value,
  mitigation: $("mitigation").value,
  scr: +$("scr").value,
  load_mw: +$("load").value,
  bess_mw: +$("bess").value,
  q_gain: +$("gain").value,
});
async function request(c) {
  const r = await fetch("/api/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(c),
  });
  if (!r.ok) throw Error(JSON.stringify(await r.json()));
  return r.json();
}
function plot(id, series, min, max, label) {
  const el = $(id),
    dpr = devicePixelRatio || 1,
    w = el.clientWidth,
    h = el.clientHeight;
  el.width = w * dpr;
  el.height = h * dpr;
  const x = el.getContext("2d");
  x.scale(dpr, dpr);
  const l = 43,
    r = 10,
    top = 8,
    b = 22,
    pw = w - l - r,
    ph = h - top - b;
  const px = (v) => l + (v / 12) * pw,
    py = (v) => top + ((max - v) / (max - min)) * ph;
  x.font = "8px monospace";
  x.lineWidth = 1;
  for (let j = 0; j <= 3; j++) {
    const v = min + ((max - min) * j) / 3,
      yy = py(v);
    x.strokeStyle = "#e8ece7";
    x.beginPath();
    x.moveTo(l, yy);
    x.lineTo(w - r, yy);
    x.stroke();
    x.fillStyle = "#788780";
    x.textAlign = "right";
    x.fillText(v.toFixed(max - min < 2 ? 2 : 0), l - 7, yy + 3);
  }
  for (let j = 0; j <= 12; j += 2) {
    x.fillStyle = "#8b9690";
    x.textAlign = "center";
    x.fillText(j + "s", px(j), h - 5);
  }
  if (["fault", "recovery", "combined"].includes($("scenario").value)) {
    x.fillStyle = "#b5522f12";
    x.fillRect(px(2), top, Math.max(3, px(2.15) - px(2)), ph);
  }
  series.forEach((s) => {
    x.save();
    x.beginPath();
    x.rect(l, top, pw, ph);
    x.clip();
    x.strokeStyle = s.color;
    x.lineWidth = s.dash ? 1.2 : 1.8;
    x.setLineDash(s.dash ? [4, 3] : []);
    x.beginPath();
    const end = Math.min(s.data.length, Math.floor(cursor / 0.005) + 1);
    for (let j = 0; j < end; j += 2) {
      const xx = px(result.time_s[j]),
        yy = py(s.data[j]);
      j ? x.lineTo(xx, yy) : x.moveTo(xx, yy);
    }
    x.stroke();
    x.restore();
  });
  if (cursor < 12) {
    x.strokeStyle = "#172b3555";
    x.setLineDash([2, 3]);
    x.beginPath();
    x.moveTo(px(cursor), top);
    x.lineTo(px(cursor), h - b);
    x.stroke();
  }
}
function draw() {
  if (!result) return;
  const s = result.signals,
    b = baseline.signals;
  const pair = (name) => [
    { data: b[name], color: colors.baseline, dash: true },
    { data: s[name], color: colors.selected },
  ];
  plot(
    "voltage",
    pair("voltage_pu"),
    Math.min(0.5, ...s.voltage_pu, ...b.voltage_pu) - 0.03,
    1.12,
  );
  plot(
    "frequency",
    pair("frequency_hz"),
    Math.min(49.7, ...s.frequency_hz, ...b.frequency_hz) - 0.03,
    50.08,
  );
  plot(
    "power",
    [...pair("grid_mw"), { data: s.bess_mw, color: colors.bess }],
    -50,
    +$("load").value * 1.5,
  );
  plot("unserved", pair("unserved_mw"), 0, +$("load").value * 1.1);
  $("time").textContent = cursor.toFixed(2) + " s";
  $("timeline").value = cursor;
}
function spectrum() {
  if (!result || !$("harmonics").classList.contains("active")) return;
  const el = $("spectrum"),
    w = el.clientWidth,
    h = el.clientHeight,
    d = devicePixelRatio || 1;
  el.width = w * d;
  el.height = h * d;
  const x = el.getContext("2d");
  x.scale(d, d);
  const a = baseline.harmonics.voltage_percent,
    b = result.harmonics.voltage_percent,
    top = 35,
    bottom = h - 40,
    max = Math.max(3, ...a) * 1.25;
  x.font = "11px monospace";
  for (let j = 0; j < 4; j++) {
    let xx = 90 + (j * (w - 120)) / 4;
    [
      [a[j], "#91a0a2", 0],
      [b[j], colors.selected, 36],
    ].forEach(([v, c, off]) => {
      let hh = (v / max) * (bottom - top);
      x.fillStyle = c;
      x.fillRect(xx + off, bottom - hh, 27, hh);
      x.fillStyle = "#516460";
      x.fillText(v.toFixed(2) + "%", xx + off - 3, bottom - hh - 10);
    });
    x.fillStyle = "#65757b";
    x.fillText("h = " + result.harmonics.orders[j], xx, bottom + 23);
  }
  x.fillStyle = colors.selected;
  x.fillText("Selected", 40, 15);
  x.fillStyle = "#91a0a2";
  x.fillText("Baseline", 155, 15);
}
function show() {
  const m = result.metrics;
  const ns = result.national_screen;
  $("national").innerHTML =
    `<b>Finnish grid-demand recovery screen · ${ns.status}</b>${ns.grid_demand_at_deadline_pu !== undefined ? `Grid import at the recovery deadline: ${(ns.grid_demand_at_deadline_pu * 100).toFixed(1)}% of pre-fault demand. ` : ""}${ns.frt_conclusion || "This scenario does not exercise fault recovery."}<br><a href='${ns.source}' target='_blank' rel='noreferrer'>June 2026 requirement · §9.1.11 ↗</a> · Confirm facility applicability.`;
  $("metric-v").textContent = m.min_voltage_pu.toFixed(3);
  $("metric-f").textContent = m.frequency_nadir_hz.toFixed(3);
  $("metric-e").textContent = (m.unserved_mwh * 1000).toFixed(2);
  $("metric-h").textContent = m.thdv_percent.toFixed(2);
  $("checks").innerHTML = result.checks
    .map(
      (c) =>
        `<div class="check"><span class="${c.passed ? "pass" : "fail"}">${c.passed ? "✓" : "↗"}</span><b>${c.name}</b><span class="criterion">${c.criterion}</span><span class="result ${c.passed ? "pass" : "fail"}">${c.passed ? "MEETS TARGET" : "REVIEW"}</span></div>`,
    )
    .join("");
  $("link-scr").textContent = `SCR ${config().scr.toFixed(1)} · X/R 10`;
  $("poc").textContent = `${config().load_mw} MW / 0.98 PF`;
  $("architecture").textContent =
    $("mitigation").selectedOptions[0].text.toUpperCase();
  $("mode-results").innerHTML = result.modes
    .map(
      (p) =>
        `<div class="mode-card">λ = ${p.real.toFixed(2)} ${p.imag >= 0 ? "+" : "−"} j${Math.abs(p.imag).toFixed(2)}<br>Mode: ${p.frequency_hz.toFixed(2)} Hz<br>Damping ratio: ${p.damping_ratio.toFixed(3)}</div>`,
    )
    .join("");
  draw();
  spectrum();
}
async function run() {
  const token = ++runCount;
  $("run").disabled = true;
  $("status").textContent = "SOLVING";
  const start = performance.now();
  try {
    const c = config();
    const [a, b] = await Promise.all([
      request(c),
      request({ ...c, mitigation: "baseline" }),
    ]);
    if (token !== runCount) return;
    result = a;
    baseline = b;
    cursor = 12;
    playing = false;
    show();
    $("status").textContent = "STUDY COMPLETE";
    $("runtime").textContent =
      `SOLVED IN ${((performance.now() - start) / 1000).toFixed(2)} s · SYNTHETIC SCREENING`;
    $("comparison").innerHTML =
      '<p class="note">Configuration changed. Run comparison for current settings.</p>';
  } catch (e) {
    $("status").textContent = "INPUT ERROR";
    $("runtime").textContent = e.message;
  } finally {
    $("run").disabled = false;
  }
}
async function compare() {
  if (!result) return;
  $("compare").disabled = true;
  $("status").textContent = "COMPARING";
  const c = config();
  try {
    const catalog = await (await fetch("/api/catalog")).json();
    const rows = [];
    for (const [key, title] of Object.entries(catalog.mitigations)) {
      const r = await request({ ...c, mitigation: key });
      rows.push({ key, title, m: r.metrics });
    }
    $("comparison").innerHTML =
      "<table><thead><tr><th>ARCHITECTURE</th><th>V MIN / pu</th><th>NADIR / Hz</th><th>AI RAMP / MW/s</th><th>IT DEFICIT / kWh</th><th>THDv / %</th></tr></thead><tbody>" +
      rows
        .map(
          (r) =>
            `<tr class="${r.key === c.mitigation ? "highlight" : ""}"><td>${r.title}</td><td>${r.m.min_voltage_pu.toFixed(3)}</td><td>${r.m.frequency_nadir_hz.toFixed(3)}</td><td>${r.m.workload_ramp_mw_s.toFixed(1)}</td><td>${(r.m.unserved_mwh * 1000).toFixed(2)}</td><td>${r.m.thdv_percent.toFixed(2)}</td></tr>`,
        )
        .join("") +
      "</tbody></table>";
    selectTab("evidence");
    $("status").textContent = "COMPARISON COMPLETE";
  } catch (e) {
    $("status").textContent = "COMPARISON ERROR";
    $("comparison").textContent = e.message;
  } finally {
    $("compare").disabled = false;
  }
}
function selectTab(name) {
  document
    .querySelectorAll(".tabs button")
    .forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  document
    .querySelectorAll(".view")
    .forEach((v) => v.classList.toggle("active", v.id === name));
  draw();
  spectrum();
}
document
  .querySelectorAll(".tabs button")
  .forEach((b) => (b.onclick = () => selectTab(b.dataset.tab)));
$("run").onclick = run;
$("compare").onclick = compare;
$("compare2").onclick = compare;
$("scr").oninput = () => {
  $("scr-out").textContent = (+$("scr").value).toFixed(1);
};
$("gain").oninput = () => {
  $("gain-out").textContent = $("gain").value + " Mvar/pu";
};
$("gain").onchange = run;
$("timeline").oninput = () => {
  playing = false;
  $("play").textContent = "▶ Replay";
  cursor = +$("timeline").value;
  draw();
};
$("play").onclick = () => {
  playing = !playing;
  $("play").textContent = playing ? "Ⅱ Pause" : "▶ Replay";
  if (!playing) return;
  if (cursor >= 12) cursor = 0;
  let last = performance.now();
  function frame(now) {
    if (!playing) return;
    cursor = Math.min(12, cursor + (now - last) / 1000);
    last = now;
    draw();
    if (cursor < 12) animation = requestAnimationFrame(frame);
    else {
      playing = false;
      $("play").textContent = "▶ Replay";
    }
  }
  cancelAnimationFrame(animation);
  animation = requestAnimationFrame(frame);
};
$("csv").onclick = async () => {
  const r = await fetch("/api/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config()),
  });
  if (!r.ok) {
    $("status").textContent = "EXPORT ERROR";
    return;
  }
  const u = URL.createObjectURL(await r.blob()),
    a = document.createElement("a");
  a.href = u;
  a.download = "gridlens-trace.csv";
  a.click();
  URL.revokeObjectURL(u);
};
window.addEventListener("resize", () => {
  draw();
  spectrum();
});
(async () => {
  const catalog = await (await fetch("/api/catalog")).json();
  for (const [id, items] of [
    ["scenario", catalog.scenarios],
    ["mitigation", catalog.mitigations],
  ]) {
    $(id).innerHTML = Object.entries(items)
      .map(([v, t]) => `<option value="${v}">${t}</option>`)
      .join("");
  }
  $("scenario").value = "combined";
  $("mitigation").value = "coordinated";
  await run();
})();

(async () => {
  try {
    const r = await (await fetch("/api/workload")).json();
    document.getElementById("workload-evidence").innerHTML =
      `<p class='note'>${r.retained_jobs} retained HPC jobs · ${r.retained_samples.toLocaleString()} original power samples. Mean node-power P10 / median / P90: ${r.node_power_quantiles_w.map((x) => x.toFixed(0) + " W").join(" / ")}. Normalized hypothetical facility loading: 84.7 / 100.0 / 147.6 MW.</p><p class='note'>The supplied subset informs loading sensitivity. It does not establish subsecond AI behavior or calibrate grid dynamics. Six additional studies use these loading points.</p><a href='${r.doi}' target='_blank' rel='noreferrer'>PM100 dataset and attribution ↗</a>`;
  } catch (e) {
    document.getElementById("workload-evidence").textContent =
      "Workload provenance unavailable.";
  }
})();
