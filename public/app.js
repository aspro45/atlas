import { makeReader, write, connectWallet, activeAccount, balanceOf, short, fmtErr }
  from "./shared/genlayer-lite.js";

const CONTRACT = "0x4F611050934677D94940c2998aF336EE9BEf9023";
const EXPLORER = "https://explorer-studio.genlayer.com/address/0x4F611050934677D94940c2998aF336EE9BEf9023";
const { read } = makeReader(CONTRACT);
const STLABEL = ["Awaiting proof", "Verified", "Rejected"];
const STKEY = ["pending", "verified", "rejected"];
const CATS = ["landmark", "monument", "nature", "city", "mystery", "other"];
const $ = (id) => document.getElementById(id);
const esc = (s) => (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const hostOf = (u) => { try { return new URL(u).hostname.replace(/^www\./, ""); } catch (_) { return u; } };

let account = null, places = [], markers = [], map = null, dropMode = false, ghost = null, pickCat = "landmark", picked = null;

function toast(msg, kind = "", title = "atlas") {
  const el = document.createElement("div"); el.className = "toast " + kind;
  el.innerHTML = `<span class="tt">${title}</span>`; el.appendChild(document.createTextNode(msg));
  $("log").appendChild(el); setTimeout(() => el.remove(), kind === "err" ? 15000 : 5000);
}

/* ---- map ---- */
function initMap() {
  map = L.map("map", { zoomControl: true, attributionControl: true, worldCopyJump: true }).setView([30, 5], 3);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; OpenStreetMap &copy; CARTO', subdomains: "abcd", maxZoom: 19,
  }).addTo(map);
  map.on("click", onMapClick);
}
function pinIcon(statusKey, ghostly) {
  return L.divIcon({ className: "", html: `<div class="pin ${ghostly ? "ghost" : statusKey}"></div>`, iconSize: [18, 18], iconAnchor: [9, 9] });
}
function drawMarkers() {
  markers.forEach((m) => map.removeLayer(m)); markers = [];
  places.forEach((p) => {
    const lat = parseFloat(p.lat), lng = parseFloat(p.lng);
    if (Number.isNaN(lat) || Number.isNaN(lng)) return;
    const m = L.marker([lat, lng], { icon: pinIcon(STKEY[p.status]) }).addTo(map);
    m.on("click", () => openPanel(p.id));
    markers.push(m);
  });
}

/* ---- detail panel ---- */
function openPanel(id) {
  const p = places.find((x) => x.id === id); if (!p) return;
  const sk = STKEY[p.status];
  let verdict = "";
  if (p.status === 1) verdict = `<div class="p-verdict pv-ok"><b>Confirmed by validators.</b> ${p.rationale ? esc(p.rationale) : ""}</div>`;
  if (p.status === 2) verdict = `<div class="p-verdict pv-no"><b>Rejected.</b> ${p.rationale ? esc(p.rationale) : "The source did not confirm a real place."}</div>`;
  const canVerify = p.status === 0;
  $("panelBody").innerHTML = `
    <div class="p-cat">${esc(p.category)}</div>
    <div class="p-name">${esc(p.name)}</div>
    <span class="p-status ps-${sk}"><i class="dot ${sk}"></i> ${STLABEL[p.status]}</span>
    <div class="p-desc">${esc(p.description)}</div>
    ${verdict}
    <div class="p-meta">
      <div class="p-kv"><span class="k">Coordinates</span><span class="v">${esc(p.lat)}, ${esc(p.lng)}</span></div>
      <div class="p-kv"><span class="k">Source</span><span class="v"><a href="${esc(p.proof_url)}" target="_blank" rel="noopener">${esc(hostOf(p.proof_url))} ↗</a></span></div>
      <div class="p-kv"><span class="k">Pinned by</span><span class="v">${short(p.submitter)}</span></div>
    </div>
    ${canVerify ? `<button class="gbtn accent wide" id="verifyBtn"><i class="ph-bold ph-shield-check"></i> Verify with validators</button><p class="add-note">Reads the source and runs a real LLM consensus. Match → verified, otherwise rejected.</p>` : ""}`;
  $("panel").setAttribute("aria-hidden", "false");
  if (canVerify) $("verifyBtn").onclick = () => doVerify(p.id);
  const lat = parseFloat(p.lat), lng = parseFloat(p.lng);
  if (!Number.isNaN(lat)) map.flyTo([lat, lng], Math.max(map.getZoom(), 5), { duration: .6 });
}
$("panelX").onclick = () => $("panel").setAttribute("aria-hidden", "true");

/* ---- drop-pin flow ---- */
function setDrop(on) {
  dropMode = on;
  $("dropHint").classList.toggle("on", on);
  $("map").style.cursor = on ? "crosshair" : "";
  if (!on && ghost) { map.removeLayer(ghost); ghost = null; }
}
$("dropBtn").onclick = () => { $("panel").setAttribute("aria-hidden", "true"); setDrop(true); };
$("cancelDrop").onclick = () => { setDrop(false); $("addPanel").setAttribute("aria-hidden", "true"); };
function onMapClick(e) {
  if (!dropMode) return;
  picked = e.latlng;
  if (ghost) map.removeLayer(ghost);
  ghost = L.marker(e.latlng, { icon: pinIcon("pending", true) }).addTo(map);
  $("coordReadout").classList.remove("empty");
  $("coordReadout").innerHTML = `<i class="ph-bold ph-crosshair"></i> <span>${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}</span>`;
  $("addPanel").setAttribute("aria-hidden", "false");
  $("dropHint").classList.remove("on");
}
function buildCats() {
  $("aCats").innerHTML = CATS.map((c) => `<span class="chip ${c === pickCat ? "on" : ""}" data-c="${c}">${c}</span>`).join("");
  document.querySelectorAll("#aCats .chip").forEach((c) => c.onclick = () => { pickCat = c.dataset.c; buildCats(); });
}
$("addX").onclick = () => { $("addPanel").setAttribute("aria-hidden", "true"); setDrop(false); };

/* ---- actions ---- */
async function doVerify(id) {
  if (!confirm("Verify this pin? Validators read the source and decide. Calls a real LLM.")) return;
  const btn = $("verifyBtn"); if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> validators reading…'; }
  try { await ensureWallet(); toast("Validators inspecting the source…", "", "verify"); await write(CONTRACT, "verify", [id]); toast("Settled on-chain.", "ok"); await load(); openPanel(id); }
  catch (e) { toast(fmtErr(e), "err"); if (btn) { btn.disabled = false; btn.textContent = "Verify with validators"; } }
}
async function submitPin() {
  if (!picked) return toast("Click the map to place your pin first.", "err");
  const name = $("aName").value.trim(), desc = $("aDesc").value.trim(), url = $("aUrl").value.trim();
  if (!name) return toast("Give the place a name.", "err");
  if (!desc) return toast("Add a short description.", "err");
  if (!url) return toast("Add a source URL.", "err");
  const btn = $("submitPin"); btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> adding';
  try {
    await ensureWallet();
    await write(CONTRACT, "add_place", [name, desc, pickCat, picked.lat.toFixed(6), picked.lng.toFixed(6), url]);
    toast("Pin added — awaiting proof.", "ok");
    $("aName").value = $("aDesc").value = $("aUrl").value = "";
    $("addPanel").setAttribute("aria-hidden", "true"); setDrop(false); picked = null;
    await load();
  } catch (e) { toast(fmtErr(e), "err"); btn.disabled = false; btn.innerHTML = "Add pin"; }
}
$("submitPin").onclick = submitPin;

/* ---- wallet ---- */
async function refreshWallet() {
  account = await activeAccount();
  const slot = $("walletslot");
  if (account) { let b = 0n; try { b = await balanceOf(account); } catch (_) {} slot.innerHTML = `<span class="gbtn" style="cursor:default"><i class="ph-fill ph-circle" style="color:var(--teal);font-size:9px"></i> ${short(account)}</span>`; }
  else { slot.innerHTML = `<button class="gbtn" id="connectBtn"><i class="ph-bold ph-wallet"></i> Connect</button>`; $("connectBtn").onclick = doConnect; }
}
async function doConnect() { try { account = await connectWallet(); toast("Connected on studionet.", "ok"); await refreshWallet(); } catch (e) { toast(fmtErr(e), "err"); } }
async function ensureWallet() { if (!account) account = await connectWallet(); await refreshWallet(); }

/* ---- load ---- */
async function load() {
  const count = Number(await read("get_place_count"));
  const out = [];
  for (let i = 0; i < count; i++) out.push({ id: i, ...(await read("get_place", [i])) });
  places = out;
  const v = places.filter((p) => p.status === 1).length;
  $("countLine").textContent = `— ${places.length} pins · ${v} verified`;
  drawMarkers();
}

const _cb = $("connectBtn"); if (_cb) _cb.onclick = doConnect;
const _contractLink = $("contractLink"); if (_contractLink) _contractLink.href = "https://explorer-studio.genlayer.com/address/0x4F611050934677D94940c2998aF336EE9BEf9023";
if (window.ethereum) window.ethereum.on?.("accountsChanged", refreshWallet);

(async () => {
  initMap(); buildCats(); await refreshWallet();
  try { await load(); } catch (e) { toast("Could not reach the chain. " + fmtErr(e), "err"); }
})();
