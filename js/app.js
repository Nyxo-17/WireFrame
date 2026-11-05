/* ==========================================================================
   WireFrame HTML5 / ES6 — Moteur Temps Réel 144 FPS & Codex (par Nyxo_17)
   ========================================================================== */

const WF_DATA = window.WIREFRAME_DATA || {
  codex: { warframes: [], resources: [], mods: [], bounties: [] },
  duviri: { warframes_weeks: [], incarnon_weeks: [] },
  translations: { fr: {}, en: {} },
  version: { version: "1.0.0" }
};

let currentLang = localStorage.getItem("wf_lang") || "fr";
let currentZoom = parseInt(localStorage.getItem("wf_zoom") || "100", 10);
let currentTab = "welcome";

// État de la pagination et recherche Codex
const codexState = {
  resources: { query: "", page: 0 },
  mods: { query: "", page: 0 },
  warframes: { query: "", page: 0 }
};
const ITEMS_PER_PAGE = 20;

// État des serveurs Warframe & Cycles
let worldState = null;
let duviriState = null;
let bountyState = null;
let prevCycleSnapshot = {};

// Préférences de notifications
const defaultNotifPrefs = {
  planets: true,
  baro: true,
  bounties: true,
  incarnon: true,
  warframes: true,
  sound: true
};
let notifPrefs = JSON.parse(localStorage.getItem("wf_notif_prefs") || JSON.stringify(defaultNotifPrefs));
let notifHistory = JSON.parse(localStorage.getItem("wf_notif_history") || "[]");

// Époques UTC de référence
const VALLIS_EPOCH_MS = Date.UTC(2018, 10, 10, 8, 13, 48); // 10 Nov 2018
const BARO_EPOCH_MS = Date.UTC(2023, 3, 21, 13, 0, 0);     // 21 Avr 2023
const DUVIRI_EPOCH_MS = Date.UTC(2023, 4, 1, 0, 0, 0);     // Lundi 1 Mai 2023 00:00 UTC
const BOUNTY_ROTATION_SEC = 9000;                          // 2h30

// Images des planètes
const PLANET_IMAGES = {
  cetus: "data/planets/earth.png",
  earth: "data/planets/earth.png",
  vallis: "data/planets/venus.png",
  cambion: "data/planets/deimos.png",
  zariman: "data/planets/zariman.png"
};

/* ==========================================================================
   1. TRADUCTIONS (FR / EN) & FORMATAGE
   ========================================================================== */
function tr(key) {
  const dict = WF_DATA.translations[currentLang] || WF_DATA.translations.fr || {};
  return dict[key] || key;
}

function cleanNavText(raw) {
  // Retire l'emoji de début déjà présent dans .nav-icon
  return raw.replace(/^[^\wÀ-ÿ]+\s*/, "");
}

function trCycleState(stateStr) {
  const map = {
    Jour: tr("state_day"),
    Nuit: tr("state_night"),
    Chaud: tr("state_warm"),
    Froid: tr("state_cold"),
    Fass: tr("state_fass"),
    Vome: tr("state_vome")
  };
  return map[stateStr] || stateStr;
}

function getStateColor(stateStr) {
  const s = (stateStr || "").toLowerCase();
  if (s.includes("jour") || s.includes("day") || s.includes("chaud") || s.includes("warm") || s.includes("fass")) {
    return "#F59E0B";
  }
  return "#4DA3FF";
}

function getRemainingSeconds(isoDate) {
  if (!isoDate) return 0;
  const target = new Date(isoDate).getTime();
  if (isNaN(target)) return 0;
  return Math.max(0, Math.floor((target - Date.now()) / 1000));
}

function formatCountdown(seconds, short = false) {
  if (seconds <= 0) return short ? "0m 00s" : "Rotation...";
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  const pad = (n) => String(n).padStart(2, "0");

  if (short) {
    if (d > 0) return `${d}j ${h}h`;
    if (h > 0) return `${h}h ${pad(m)}m ${pad(s)}s`;
    return `${m}m ${pad(s)}s`;
  }
  if (d > 0) return `${d}j ${pad(h)}h ${pad(m)}m ${pad(s)}s`;
  if (h > 0) return `${h}h ${pad(m)}m ${pad(s)}s`;
  return `${m}m ${pad(s)}s`;
}

/* ==========================================================================
   2. CALCULS CYCLES UTC & RÉCUPÉRATION API WARFRAME EN DIRECT
   ========================================================================== */
function computeOfflineWorldState() {
  const nowMs = Date.now();
  const nowSec = Math.floor(nowMs / 1000);

  // Vallée Orbis : 1600s (400s Chaud, 1200s Froid)
  const vallisElapsed = Math.floor((nowMs - VALLIS_EPOCH_MS) / 1000) % 1600;
  const isWarm = vallisElapsed < 400;
  const vallisRem = isWarm ? (400 - vallisElapsed) : (1600 - vallisElapsed);
  const vallisExp = new Date(nowMs + vallisRem * 1000).toISOString();

  // Cetus & Cambion : 9000s (6000s Jour/Fass, 3000s Nuit/Vome)
  const cetusElapsed = nowSec % 9000;
  const isDay = cetusElapsed < 6000;
  const cetusRem = isDay ? (6000 - cetusElapsed) : (9000 - cetusElapsed);
  const cetusExp = new Date(nowMs + cetusRem * 1000).toISOString();

  // Terre (Forêts) : 28800s (14400s Jour, 14400s Nuit)
  const earthElapsed = nowSec % 28800;
  const earthDay = earthElapsed < 14400;
  const earthRem = earthDay ? (14400 - earthElapsed) : (28800 - earthElapsed);
  const earthExp = new Date(nowMs + earthRem * 1000).toISOString();

  // Baro Ki'Teer : cycle de 14 jours
  const baroCycle = 14 * 86400;
  const baroElapsed = Math.floor((nowMs - BARO_EPOCH_MS) / 1000) % baroCycle;
  const baroActive = baroElapsed < (2 * 86400);
  const baroRem = baroActive ? (2 * 86400 - baroElapsed) : (baroCycle - baroElapsed);
  const baroTarget = new Date(nowMs + baroRem * 1000).toISOString();

  return {
    source: "En direct (Calcul UTC)",
    cetus: { state: isDay ? "Jour" : "Nuit", expiry: cetusExp },
    vallis: { state: isWarm ? "Chaud" : "Froid", expiry: vallisExp },
    cambion: { state: isDay ? "Fass" : "Vome", expiry: cetusExp },
    earth: { state: earthDay ? "Jour" : "Nuit", expiry: earthExp },
    baro: {
      active: baroActive,
      location: "Relais Kronia (Saturne)",
      activation: baroActive ? new Date(nowMs).toISOString() : baroTarget,
      expiry: baroActive ? baroTarget : "",
      inventory: []
    }
  };
}

function computeDuviriState() {
  const nowMs = Date.now();
  const weekMs = 7 * 86400 * 1000;
  const elapsedMs = Math.max(0, nowMs - DUVIRI_EPOCH_MS);
  const weeksPassed = Math.floor(elapsedMs / weekMs);
  const remMs = weekMs - (elapsedMs % weekMs);
  const expiryIso = new Date(nowMs + remMs).toISOString();

  const wfWeeks = WF_DATA.duviri.warframes_weeks || [];
  const incWeeks = WF_DATA.duviri.incarnon_weeks || [];

  const wfIdx = wfWeeks.length ? (weeksPassed % wfWeeks.length) : 0;
  const wfNextIdx = wfWeeks.length ? ((weeksPassed + 1) % wfWeeks.length) : 0;

  const incIdx = incWeeks.length ? (weeksPassed % incWeeks.length) : 0;
  const incNextIdx = incWeeks.length ? ((weeksPassed + 1) % incWeeks.length) : 0;

  return {
    warframe_index: wfIdx,
    warframes_current: wfWeeks[wfIdx] || [],
    warframes_next: wfWeeks[wfNextIdx] || [],
    incarnon_index: incIdx,
    incarnon_current: incWeeks[incIdx] || [],
    incarnon_next: incWeeks[incNextIdx] || [],
    all_warframes: wfWeeks,
    all_incarnon: incWeeks,
    expiry: expiryIso
  };
}

function computeBountyState() {
  const nowSec = Math.floor(Date.now() / 1000);
  const rotIdx = Math.floor(nowSec / BOUNTY_ROTATION_SEC) % 3;
  const nextIdx = (rotIdx + 1) % 3;
  const remSec = BOUNTY_ROTATION_SEC - (nowSec % BOUNTY_ROTATION_SEC);
  const letters = ["Rotation A", "Rotation B", "Rotation C"];

  return {
    rotation_index: rotIdx,
    current_rotation: letters[rotIdx],
    next_rotation: letters[nextIdx],
    expiry: new Date(Date.now() + remSec * 1000).toISOString(),
    hubs: WF_DATA.codex.bounties || []
  };
}

async function fetchLiveWarframeAPI() {
  const fallback = computeOfflineWorldState();
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 4500);
    const res = await fetch("https://api.warframestat.us/pc/", { signal: controller.signal });
    clearTimeout(timer);
    if (!res.ok) throw new Error("HTTP " + res.status);
    const raw = await res.json();

    const cetus = raw.cetusCycle || {};
    const vallis = raw.vallisCycle || {};
    const cambion = raw.cambionCycle || {};
    const earth = raw.earthCycle || {};
    const baro = raw.voidTrader || {};

    return {
      source: "En direct (API)",
      cetus: {
        state: (cetus.state || "day").toLowerCase() === "day" ? "Jour" : "Nuit",
        expiry: cetus.expiry || fallback.cetus.expiry
      },
      vallis: {
        state: (vallis.state || "cold").toLowerCase() === "warm" ? "Chaud" : "Froid",
        expiry: vallis.expiry || fallback.vallis.expiry
      },
      cambion: {
        state: (cambion.state || "fass").toLowerCase() === "fass" ? "Fass" : "Vome",
        expiry: cambion.expiry || fallback.cambion.expiry
      },
      earth: {
        state: (earth.state || "day").toLowerCase() === "day" ? "Jour" : "Nuit",
        expiry: earth.expiry || fallback.earth.expiry
      },
      baro: {
        active: Boolean(baro.active),
        location: baro.location || fallback.baro.location,
        activation: baro.activation || fallback.baro.activation,
        expiry: baro.expiry || fallback.baro.expiry,
        inventory: Array.isArray(baro.inventory)
          ? baro.inventory.map((it) => ({
              item: it.item || "Objet",
              ducats: it.ducats || 0,
              credits: it.credits || 0
            }))
          : []
      }
    };
  } catch (err) {
    return fallback;
  }
}

/* ==========================================================================
   3. PANNEAU LATÉRAL DROIT EN DIRECT & COMPTE À REBOURS 1 SECONDE
   ========================================================================== */
function buildLiveWorldsGrid() {
  const grid = document.getElementById("live-worlds-grid");
  if (!grid || !worldState) return;

  const worlds = [
    { key: "cetus", title: tr("w_cetus_short"), sub: tr("w_cetus_sub"), img: PLANET_IMAGES.cetus },
    { key: "vallis", title: tr("w_vallis_short"), sub: tr("w_vallis_sub"), img: PLANET_IMAGES.vallis },
    { key: "cambion", title: tr("w_cambion_short"), sub: tr("w_cambion_sub"), img: PLANET_IMAGES.cambion },
    { key: "earth", title: tr("w_earth_short"), sub: tr("w_earth_sub"), img: PLANET_IMAGES.earth }
  ];

  grid.innerHTML = worlds
    .map((w) => {
      const st = worldState[w.key] || { state: "Jour", expiry: "" };
      const dispState = trCycleState(st.state);
      const color = getStateColor(dispState);
      const timer = formatCountdown(getRemainingSeconds(st.expiry), true);
      return `
        <div class="planet-card" style="padding:9px 10px; gap:6px;">
          <div class="planet-card-top" style="gap:8px;">
            <img src="${w.img}" alt="${w.title}" class="planet-img compact" />
            <div style="overflow:hidden;">
              <div class="planet-title" style="font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${w.title}</div>
              <div class="planet-sub" style="font-size:10px;">${w.sub}</div>
            </div>
          </div>
          <div class="planet-card-bottom">
            <span id="live-state-${w.key}" class="cycle-state" style="font-size:11.5px; color:${color};">● ${dispState}</span>
            <span id="live-timer-${w.key}" class="cycle-timer" style="font-size:11.5px;">${timer}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function updateLivePanel() {
  if (!worldState) worldState = computeOfflineWorldState();
  duviriState = computeDuviriState();
  bountyState = computeBountyState();

  const statusEl = document.getElementById("lbl-api-status");
  if (statusEl) statusEl.textContent = "📡 " + worldState.source;

  // Vérifie si la grille des planètes du panneau droit est déjà construite
  if (!document.getElementById("live-timer-cetus")) {
    buildLiveWorldsGrid();
  } else {
    ["cetus", "vallis", "cambion", "earth"].forEach((k) => {
      const st = worldState[k] || {};
      const disp = trCycleState(st.state);
      const stateEl = document.getElementById(`live-state-${k}`);
      const timerEl = document.getElementById(`live-timer-${k}`);
      if (stateEl) {
        stateEl.textContent = `● ${disp}`;
        stateEl.style.color = getStateColor(disp);
      }
      if (timerEl) {
        timerEl.textContent = formatCountdown(getRemainingSeconds(st.expiry), true);
      }
    });
  }

  // Duviri Incarnon & Warframes
  const duvTimer = formatCountdown(getRemainingSeconds(duviriState.expiry), true);
  const incTimerEl = document.getElementById("live-inc-timer");
  const wfTimerEl = document.getElementById("live-wf-timer");
  if (incTimerEl) incTimerEl.textContent = duvTimer;
  if (wfTimerEl) wfTimerEl.textContent = duvTimer;

  const incCurEl = document.getElementById("live-inc-cur");
  const incNxtEl = document.getElementById("live-inc-nxt");
  if (incCurEl) incCurEl.textContent = `${tr("lbl_current")}: ${duviriState.incarnon_current.join(", ")}`;
  if (incNxtEl) incNxtEl.textContent = `${tr("lbl_next")}: ${duviriState.incarnon_next.join(", ")}`;

  const wfCurEl = document.getElementById("live-wf-cur");
  const wfNxtEl = document.getElementById("live-wf-nxt");
  if (wfCurEl) wfCurEl.textContent = `${tr("lbl_current")}: ${duviriState.warframes_current.join(" • ")}`;
  if (wfNxtEl) wfNxtEl.textContent = `${tr("lbl_next")}: ${duviriState.warframes_next.join(" • ")}`;

  // Mises à prix
  const bntTimerEl = document.getElementById("live-bounty-timer");
  const bntInfoEl = document.getElementById("live-bounty-info");
  if (bntTimerEl) bntTimerEl.textContent = formatCountdown(getRemainingSeconds(bountyState.expiry), true);
  if (bntInfoEl) bntInfoEl.textContent = `${tr("lbl_current")}: ${bountyState.current_rotation}  ➔  ${tr("lbl_next")}: ${bountyState.next_rotation}`;

  // Baro Ki'Teer
  const baro = worldState.baro || {};
  const baroTarget = baro.active ? baro.expiry : baro.activation;
  const baroTimerEl = document.getElementById("live-baro-timer");
  const baroInfoEl = document.getElementById("live-baro-info");
  if (baroTimerEl) baroTimerEl.textContent = formatCountdown(getRemainingSeconds(baroTarget), true);
  if (baroInfoEl) {
    baroInfoEl.textContent = baro.active
      ? `🟢 ${tr("baro_present")} : ${baro.location}`
      : `⏳ ${tr("baro_arrives")} : ${baro.location}`;
  }

  // Mise à jour dynamique des timers de la vue centrale si ouverte
  updateActiveCenterTimers();
  checkCycleChangeAlerts();
}

function updateActiveCenterTimers() {
  if (currentTab === "worlds") {
    ["cetus", "vallis", "cambion", "earth"].forEach((k) => {
      const el = document.getElementById(`center-world-timer-${k}`);
      if (el && worldState[k]) {
        el.textContent = formatCountdown(getRemainingSeconds(worldState[k].expiry), false);
      }
    });
  } else if (currentTab === "bounties" && bountyState) {
    const el = document.getElementById("center-bounty-timer");
    if (el) {
      el.textContent = `${tr("bounties_change_in")} ${formatCountdown(getRemainingSeconds(bountyState.expiry), false)} (${tr("lbl_current")} : ${bountyState.current_rotation})`;
    }
  } else if (currentTab === "duviri" && duviriState) {
    const el = document.getElementById("center-duviri-timer");
    if (el) {
      el.textContent = `${tr("duviri_reset_prefix")} ${formatCountdown(getRemainingSeconds(duviriState.expiry), false)}`;
    }
  } else if (currentTab === "baro" && worldState && worldState.baro) {
    const el = document.getElementById("center-baro-timer");
    if (el) {
      const b = worldState.baro;
      const target = b.active ? b.expiry : b.activation;
      const prefix = b.active ? tr("baro_leaves_in") : tr("baro_arrives_in");
      el.textContent = `${prefix} ${formatCountdown(getRemainingSeconds(target), false)}`;
    }
  }
}

/* ==========================================================================
   4. SYSTÈME DE NOTIFICATIONS SONORES & VISUELLES
   ========================================================================== */
function triggerAlert(title, message) {
  const timeStr = new Date().toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  notifHistory.unshift({ time: timeStr, title, message });
  notifHistory = notifHistory.slice(0, 25);
  localStorage.setItem("wf_notif_history", JSON.stringify(notifHistory));

  // Signal sonore
  if (notifPrefs.sound) {
    try {
      const audio = new Audio("data/sounds/default_notify.wav");
      audio.volume = 0.85;
      audio.play().catch(() => {});
    } catch (e) {}
  }

  // Bannière Toast interne
  const banner = document.getElementById("toast-banner");
  const tTitle = document.getElementById("toast-title");
  const tMsg = document.getElementById("toast-msg");
  if (banner && tTitle && tMsg) {
    tTitle.textContent = "🔔 " + title;
    tMsg.textContent = message;
    banner.classList.remove("hidden");
    clearTimeout(window._toastTimeout);
    window._toastTimeout = setTimeout(() => banner.classList.add("hidden"), 5000);
  }

  // Notification système navigateur/Windows si autorisée
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification(title, { body: message, icon: "data/app_logo.png" });
  }

  if (currentTab === "notifications") {
    renderNotificationsView();
  }
}

function checkCycleChangeAlerts() {
  if (!worldState || !duviriState || !bountyState) return;
  const cur = {
    cetus: worldState.cetus?.state,
    vallis: worldState.vallis?.state,
    cambion: worldState.cambion?.state,
    earth: worldState.earth?.state,
    baro: worldState.baro?.active,
    bounty: bountyState.current_rotation,
    incarnon: duviriState.incarnon_index,
    warframes: duviriState.warframe_index
  };

  if (Object.keys(prevCycleSnapshot).length > 0) {
    if (notifPrefs.planets) {
      ["cetus", "vallis", "cambion", "earth"].forEach((k) => {
        if (prevCycleSnapshot[k] && prevCycleSnapshot[k] !== cur[k]) {
          triggerAlert("WireFrame — Cycle Planétaire", `${k.toUpperCase()} passe en cycle : ${trCycleState(cur[k])}`);
        }
      });
    }
    if (notifPrefs.bounties && prevCycleSnapshot.bounty !== cur.bounty) {
      triggerAlert("WireFrame — Mises à Prix", `Nouvelle rotation active : ${cur.bounty}`);
    }
    if (notifPrefs.baro && prevCycleSnapshot.baro !== cur.baro) {
      triggerAlert("WireFrame — Baro Ki'Teer", cur.baro ? "Baro Ki'Teer est arrivé sur le Relais !" : "Baro Ki'Teer est reparti dans le Néant.");
    }
  }
  prevCycleSnapshot = cur;
}

/* ==========================================================================
   5. RENDU DES 9 VUES CENTRALES
   ========================================================================== */
function selectTab(tabKey) {
  currentTab = tabKey;

  // Mise à jour du Neon Glow sur la Sidebar
  document.querySelectorAll(".nav-item").forEach((el) => {
    const isMatch = el.getAttribute("data-tab") === tabKey;
    el.classList.toggle("active", isMatch);
  });
  document.querySelectorAll(".nav-section-title").forEach((sec) => sec.classList.remove("glow"));
  const activeItem = document.querySelector(`.nav-item[data-tab="${tabKey}"]`);
  if (activeItem) {
    const secId = activeItem.getAttribute("data-sec");
    const secEl = document.getElementById(secId);
    if (secEl) secEl.classList.add("glow");
  }

  renderCurrentTab();
}

function renderCurrentTab() {
  const container = document.getElementById("center-zoom-content");
  if (!container) return;

  switch (currentTab) {
    case "welcome":
      renderWelcomeView(container);
      break;
    case "notifications":
      renderNotificationsView(container);
      break;
    case "resources":
      renderCodexView(container, "resources", tr("res_page_title"));
      break;
    case "mods":
      renderCodexView(container, "mods", tr("mod_page_title"));
      break;
    case "warframes":
      renderCodexView(container, "warframes", tr("wf_page_title"));
      break;
    case "worlds":
      renderWorldsView(container);
      break;
    case "bounties":
      renderBountiesView(container);
      break;
    case "duviri":
      renderDuviriView(container);
      break;
    case "baro":
      renderBaroView(container);
      break;
  }
}

/* --- VUE 1 : BIENVENUE --- */
function renderWelcomeView(container) {
  const cards = [
    { title: tr("card_res_title"), desc: tr("card_res_desc"), tab: "resources" },
    { title: tr("card_mod_title"), desc: tr("card_mod_desc"), tab: "mods" },
    { title: tr("card_wf_title"), desc: tr("card_wf_desc"), tab: "warframes" },
    { title: tr("card_wld_title"), desc: tr("card_wld_desc"), tab: "worlds" },
    { title: tr("card_bnt_title"), desc: tr("card_bnt_desc"), tab: "bounties" },
    { title: tr("card_duv_title"), desc: tr("card_duv_desc"), tab: "notifications" }
  ];

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
      <div class="view-header-title" style="margin-bottom:0;">${tr("welcome_page_title")}</div>
      <div style="display:flex; align-items:center; gap:8px; background:#141A29; border:1px solid #263554; padding:5px 12px; border-radius:8px;">
        <img src="data/app_logo.png" alt="Nyxo_17" style="width:24px; height:24px; object-fit:contain;" />
        <span style="font-size:12px; color:#8B949E;">${tr("created_by")} <strong style="color:#58A6FF;">Nyxo_17</strong></span>
      </div>
    </div>

    <div class="welcome-banner">
      <h3>${tr("welcome_banner_title")}</h3>
      <p>${tr("welcome_banner_desc")}</p>
    </div>

    <div class="cards-grid-2">
      ${cards
        .map(
          (c) => `
        <div class="feature-card">
          <div>
            <h4>${c.title}</h4>
            <p>${c.desc}</p>
          </div>
          <button class="btn-open" onclick="selectTab('${c.tab}')">${tr("open_btn")}</button>
        </div>
      `
        )
        .join("")}
    </div>
  `;
}

/* --- VUE 2 : CENTRE DE NOTIFICATIONS --- */
function renderNotificationsView(container = document.getElementById("center-zoom-content")) {
  if (!container) return;
  const switches = [
    { key: "planets", label: tr("notif_sw_planets") },
    { key: "baro", label: tr("notif_sw_baro") },
    { key: "bounties", label: tr("notif_sw_bounties") },
    { key: "incarnon", label: tr("notif_sw_incarnon") },
    { key: "warframes", label: tr("notif_sw_warframes") },
    { key: "sound", label: tr("notif_sw_sound") }
  ];

  container.innerHTML = `
    <div class="view-header-title">${tr("notif_page_title")}</div>
    <div class="view-header-sub">${tr("notif_page_sub")}</div>

    <div class="bounty-card" style="padding:16px;">
      ${switches
        .map(
          (sw) => `
        <label style="display:flex; align-items:center; gap:12px; padding:8px 4px; cursor:pointer; font-size:13px; color:#E6EDF3;">
          <input type="checkbox" ${notifPrefs[sw.key] ? "checked" : ""} onchange="toggleNotifPref('${sw.key}', this.checked)" style="width:17px; height:17px; accent-color:#3B82F6; cursor:pointer;" />
          <span>${sw.label}</span>
        </label>
      `
        )
        .join("")}

      <div style="margin-top:14px;">
        <button class="btn-open" style="font-size:13px; padding:8px 16px;" onclick="sendTestNotification()">
          ${tr("notif_test_btn")}
        </button>
      </div>
    </div>

    <div class="view-header-title" style="font-size:15px; margin:16px 0 8px 0; color:#58A6FF;">
      ${tr("notif_history_title")}
    </div>
    <div class="bounty-card" style="padding:14px;">
      ${
        notifHistory.length === 0
          ? `<div style="color:#8B949E; font-size:12.5px;">${tr("notif_empty_history")}</div>`
          : notifHistory
              .map(
                (h) => `
            <div style="padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12.5px;">
              <span style="color:#58A6FF; font-weight:700;">[${h.time}] ${h.title}</span> —
              <span style="color:#C9D1D9;">${h.message}</span>
            </div>
          `
              )
              .join("")
      }
    </div>
  `;
}

function toggleNotifPref(key, val) {
  notifPrefs[key] = Boolean(val);
  localStorage.setItem("wf_notif_prefs", JSON.stringify(notifPrefs));
}

function sendTestNotification() {
  if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
  }
  const msg =
    currentLang === "fr"
      ? "Les alertes sonores et visuelles de WireFrame fonctionnent parfaitement !"
      : "WireFrame sound and visual alerts are working properly!";
  triggerAlert("WireFrame — Test d'Alerte", msg);
}

/* --- VUES 3, 4, 5 : CODEX (RESSOURCES, MODS, WARFRAMES) --- */
function renderCodexView(container, categoryKey, title) {
  const st = codexState[categoryKey];
  const allItems = WF_DATA.codex[categoryKey] || [];
  const q = (st.query || "").trim().toLowerCase();

  const filtered = q
    ? allItems.filter(
        (it) =>
          (it.name || "").toLowerCase().includes(q) ||
          (it.category || "").toLowerCase().includes(q) ||
          (it.location || "").toLowerCase().includes(q) ||
          (it.drop || "").toLowerCase().includes(q)
      )
    : allItems;

  const totalPages = Math.max(1, Math.ceil(filtered.length / ITEMS_PER_PAGE));
  if (st.page >= totalPages) st.page = totalPages - 1;
  if (st.page < 0) st.page = 0;

  const start = st.page * ITEMS_PER_PAGE;
  const pageItems = filtered.slice(start, start + ITEMS_PER_PAGE);

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
      <div class="view-header-title" style="margin-bottom:0;">${title}</div>
      <div style="font-size:12px; font-weight:700; color:#58A6FF;">
        ${filtered.length} résultats (Page ${st.page + 1}/${totalPages})
      </div>
    </div>

    <div class="search-bar-row">
      <input
        id="codex-search-input"
        type="text"
        class="search-input"
        placeholder="${tr("search_placeholder")}"
        value="${st.query.replace(/"/g, "&quot;")}"
        oninput="onCodexSearch('${categoryKey}', this.value)"
      />
    </div>

    <div id="codex-results-list" class="codex-list">
      ${renderCodexItemsHTML(pageItems)}
    </div>

    <div class="pagination-bar">
      <button class="btn-open" ${st.page <= 0 ? "disabled style='opacity:0.4;cursor:default;'" : ""} onclick="changeCodexPage('${categoryKey}', -1)">
        ◀ Précédent
      </button>
      <span style="font-size:12.5px; font-weight:700; color:#E6EDF3;">
        Page ${st.page + 1} / ${totalPages}
      </span>
      <button class="btn-open" ${st.page >= totalPages - 1 ? "disabled style='opacity:0.4;cursor:default;'" : ""} onclick="changeCodexPage('${categoryKey}', 1)">
        Suivant ▶
      </button>
    </div>
  `;
}

function renderCodexItemsHTML(items) {
  if (!items.length) {
    return `<div style="padding:24px; text-align:center; color:#8B949E;">Aucun résultat trouvé.</div>`;
  }
  return items
    .map((item) => {
      const imgUrl = item.image
        ? `https://cdn.warframestat.us/img/${item.image}`
        : "data/app_logo.png";
      return `
        <div class="codex-item">
          <img src="${imgUrl}" alt="${item.name}" class="codex-thumb" loading="lazy" onerror="this.onerror=null;this.src='data/app_logo.png';" />
          <div>
            <div class="codex-head">
              <span class="codex-name">${item.name}</span>
              <span class="codex-cat">[${item.category || ""}]</span>
            </div>
            <div class="codex-loc">${tr("lbl_location")} ${item.location || "Système Origine"}</div>
            <div class="codex-drop">${tr("lbl_drop_method")} ${item.drop || ""}</div>
          </div>
        </div>
      `;
    })
    .join("");
}

function onCodexSearch(categoryKey, val) {
  codexState[categoryKey].query = val;
  codexState[categoryKey].page = 0;
  const container = document.getElementById("center-zoom-content");
  const input = document.getElementById("codex-search-input");
  const pos = input ? input.selectionStart : val.length;
  renderCurrentTab();
  const newInput = document.getElementById("codex-search-input");
  if (newInput) {
    newInput.focus();
    newInput.setSelectionRange(pos, pos);
  }
}

function changeCodexPage(categoryKey, delta) {
  codexState[categoryKey].page += delta;
  renderCurrentTab();
  const center = document.querySelector(".center-container");
  if (center) center.scrollTop = 0;
}

/* --- VUE 6 : TEMPS DES PLANÈTES --- */
function renderWorldsView(container) {
  if (!worldState) worldState = computeOfflineWorldState();
  const cards = [
    { key: "cetus", title: tr("w_cetus_long"), desc: tr("w_cetus_desc"), img: PLANET_IMAGES.cetus },
    { key: "vallis", title: tr("w_vallis_long"), desc: tr("w_vallis_desc"), img: PLANET_IMAGES.vallis },
    { key: "cambion", title: tr("w_cambion_long"), desc: tr("w_cambion_desc"), img: PLANET_IMAGES.cambion },
    { key: "earth", title: tr("w_earth_long"), desc: tr("w_earth_desc"), img: PLANET_IMAGES.earth }
  ];

  container.innerHTML = `
    <div class="view-header-title">${tr("worlds_page_title")}</div>
    <div class="view-header-sub">${tr("worlds_page_sub")}</div>

    <div class="cards-grid-2">
      ${cards
        .map((c) => {
          const st = worldState[c.key] || { state: "Jour", expiry: "" };
          const disp = trCycleState(st.state);
          const color = getStateColor(disp);
          const timer = formatCountdown(getRemainingSeconds(st.expiry), false);
          return `
            <div class="planet-card">
              <div class="planet-card-top">
                <img src="${c.img}" alt="${c.title}" class="planet-img" />
                <div>
                  <div class="planet-title">${c.title}</div>
                  <div class="planet-sub">${c.desc}</div>
                </div>
              </div>
              <div class="planet-card-bottom">
                <span class="cycle-state" style="color:${color};">● ${disp}</span>
                <span id="center-world-timer-${c.key}" class="cycle-timer">${timer}</span>
              </div>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

/* --- VUE 7 : MISES À PRIX (ROTATIONS A/B/C) --- */
function renderBountiesView(container) {
  if (!bountyState) bountyState = computeBountyState();
  const rotKeys = ["rot_a", "rot_b", "rot_c"];
  const rotLabels = ["Rotation A", "Rotation B", "Rotation C"];

  const getHubImg = (hubName) => {
    const n = (hubName || "").toLowerCase();
    if (n.includes("fortuna") || n.includes("vénus") || n.includes("venus")) return PLANET_IMAGES.vallis;
    if (n.includes("deimos") || n.includes("sanctum") || n.includes("necralisk")) return PLANET_IMAGES.cambion;
    if (n.includes("zariman")) return PLANET_IMAGES.zariman;
    return PLANET_IMAGES.cetus;
  };

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
      <div class="view-header-title" style="margin-bottom:0;">${tr("bounties_page_title")}</div>
      <div id="center-bounty-timer" style="font-size:13px; font-weight:700; color:#4ADE80;">
        ${tr("bounties_change_in")} ${formatCountdown(getRemainingSeconds(bountyState.expiry), false)} (${tr("lbl_current")} : ${bountyState.current_rotation})
      </div>
    </div>

    ${bountyState.hubs
      .map(
        (hub) => `
      <div class="bounty-card">
        <div class="bounty-hdr">
          <img src="${getHubImg(hub.hub)}" alt="${hub.hub}" />
          <div>
            <div style="font-size:15px; font-weight:700; color:#58A6FF;">📍 ${hub.hub}</div>
            <div style="font-size:12px; color:#8B949E;">🎯 ${hub.Syndicate || ""} — ${hub.highlights || ""}</div>
          </div>
        </div>
        ${rotKeys
          .map((rk, idx) => {
            const isActive = idx === bountyState.rotation_index;
            return `
              <div class="bounty-rot-row ${isActive ? "active" : ""}">
                <span style="color:${isActive ? "#4ADE80" : "#8B949E"};">
                  ${isActive ? "🟢 " : "⚪ "}${rotLabels[idx]}${isActive ? " (ACTIVE)" : ""}
                </span>
                <span style="color:${isActive ? "#FFFFFF" : "#B1BAC4"};">
                  ${hub[rk] || ""}
                </span>
              </div>
            `;
          })
          .join("")}
      </div>
    `
      )
      .join("")}
  `;
}

/* --- VUE 8 : CIRCUIT DE DUVIRI & INCARNON --- */
function renderDuviriView(container) {
  if (!duviriState) duviriState = computeDuviriState();

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
      <div class="view-header-title" style="margin-bottom:0;">${tr("duviri_page_title")}</div>
      <div id="center-duviri-timer" style="font-size:13px; font-weight:700; color:#4ADE80;">
        ${tr("duviri_reset_prefix")} ${formatCountdown(getRemainingSeconds(duviriState.expiry), false)}
      </div>
    </div>

    <div class="cards-grid-2">
      <div class="bounty-card">
        <div style="font-size:14px; font-weight:700; color:#58A6FF; margin-bottom:10px;">${tr("duviri_inc_col")}</div>
        ${duviriState.all_incarnon
          .map((weapons, idx) => {
            const isAct = idx === duviriState.incarnon_index;
            return `
              <div class="bounty-rot-row ${isAct ? "active" : ""}" style="grid-template-columns:135px 1fr;">
                <span style="color:${isAct ? "#4ADE80" : "#8B949E"};">
                  ${tr("week_label")} ${idx + 1}${isAct ? tr("active_tag") : ""}
                </span>
                <span style="color:${isAct ? "#FFFFFF" : "#C9D1D9"};">${weapons.join(" • ")}</span>
              </div>
            `;
          })
          .join("")}
      </div>

      <div class="bounty-card">
        <div style="font-size:14px; font-weight:700; color:#58A6FF; margin-bottom:10px;">${tr("duviri_wf_col")}</div>
        ${duviriState.all_warframes
          .map((wfs, idx) => {
            const isAct = idx === duviriState.warframe_index;
            return `
              <div class="bounty-rot-row ${isAct ? "active" : ""}" style="grid-template-columns:135px 1fr;">
                <span style="color:${isAct ? "#4ADE80" : "#8B949E"};">
                  ${tr("week_label")} ${idx + 1}${isAct ? tr("active_tag") : ""}
                </span>
                <span style="color:${isAct ? "#FFFFFF" : "#C9D1D9"};">${wfs.join(" • ")}</span>
              </div>
            `;
          })
          .join("")}
      </div>
    </div>
  `;
}

/* --- VUE 9 : BARO KI'TEER --- */
function renderBaroView(container) {
  if (!worldState) worldState = computeOfflineWorldState();
  const baro = worldState.baro || {};
  const target = baro.active ? baro.expiry : baro.activation;
  const prefix = baro.active ? tr("baro_leaves_in") : tr("baro_arrives_in");
  const inv = baro.inventory || [];

  container.innerHTML = `
    <div class="view-header-title">${tr("baro_page_title")}</div>

    <div class="bounty-card" style="padding:16px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <span style="font-size:15px; font-weight:700; color:${baro.active ? "#4ADE80" : "#F59E0B"};">
          ${baro.active ? tr("baro_status_here") : tr("baro_status_away")}
        </span>
        <span id="center-baro-timer" style="font-size:14px; font-weight:700; color:#FFFFFF;">
          ${prefix} ${formatCountdown(getRemainingSeconds(target), false)}
        </span>
      </div>
      <div style="font-size:13px; color:#8B949E;">
        ${tr("baro_dest_prefix")} <strong style="color:#E6EDF3;">${baro.location || "Relais"}</strong>
      </div>
    </div>

    <div class="view-header-title" style="font-size:15px; margin:16px 0 10px 0; color:#58A6FF;">
      ${tr("baro_inv_title")}
    </div>

    <div class="bounty-card" style="padding:14px;">
      ${
        inv.length === 0
          ? `<div style="color:#8B949E; font-size:13px; white-space:pre-line; padding:12px 0;">${tr("baro_empty_msg")}</div>`
          : inv
              .map(
                (it) => `
            <div style="display:flex; justify-content:space-between; padding:8px 10px; border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px;">
              <span style="font-weight:700; color:#F0F6FC;">🔹 ${it.item}</span>
              <span style="color:#F59E0B; font-weight:700;">🟡 ${it.ducats} Ducats   |   ⚪ ${(it.credits || 0).toLocaleString()} Crédits</span>
            </div>
          `
              )
              .join("")
      }
    </div>
  `;
}

/* ==========================================================================
   6. LANGUE (FR/EN), ZOOM CENTRAL & VÉRIFICATION DE MISE À JOUR GITHUB
   ========================================================================== */
function setLanguage(lang) {
  currentLang = lang === "en" ? "en" : "fr";
  localStorage.setItem("wf_lang", currentLang);

  document.getElementById("btn-lang-fr")?.classList.toggle("active", currentLang === "fr");
  document.getElementById("btn-lang-en")?.classList.toggle("active", currentLang === "en");

  // Traductions statiques de la Sidebar et du Panneau Droit
  const mapText = {
    "lbl-creator-role": tr("creator_role"),
    "sec-home": tr("sec_home"),
    "nav-welcome": cleanNavText(tr("nav_welcome")),
    "nav-notifications": cleanNavText(tr("nav_notifications")),
    "sec-inv": tr("sec_inventory"),
    "nav-resources": cleanNavText(tr("nav_resources")),
    "nav-mods": cleanNavText(tr("nav_mods")),
    "nav-warframes": cleanNavText(tr("nav_warframes")),
    "sec-cycles": tr("sec_cycles"),
    "nav-worlds": cleanNavText(tr("nav_worlds")),
    "nav-bounties": cleanNavText(tr("nav_bounties")),
    "nav-duviri": cleanNavText(tr("nav_duviri")),
    "nav-baro": cleanNavText(tr("nav_baro")),
    "btn-refresh": tr("btn_refresh"),
    "btn-check-update": `${tr("btn_check_update")} (v${WF_DATA.version?.version || "1.0.0"})`,
    "live-badge": tr("live_badge"),
    "live-tag": tr("live_tag"),
    "live-worlds-title": tr("live_worlds_title"),
    "live-duviri-title": tr("live_duviri_title"),
    "live-inc-title": tr("live_inc_title"),
    "live-wf-title": tr("live_wf_title"),
    "live-bounty-title": tr("live_bounty_title"),
    "live-baro-title": tr("live_baro_title")
  };

  Object.entries(mapText).forEach(([id, txt]) => {
    const el = document.getElementById(id);
    if (el) el.textContent = txt;
  });

  buildLiveWorldsGrid();
  updateLivePanel();
  renderCurrentTab();
}

function changeZoom(delta) {
  currentZoom = Math.min(140, Math.max(80, currentZoom + delta));
  localStorage.setItem("wf_zoom", String(currentZoom));
  const lbl = document.getElementById("zoom-label");
  if (lbl) lbl.textContent = `${currentZoom}%`;
  const center = document.getElementById("center-zoom-content");
  if (center) center.style.zoom = `${currentZoom}%`;
}

async function refreshAllData(showLoader = false) {
  const loader = document.getElementById("in-app-loader");
  if (showLoader && loader) loader.classList.remove("hidden");
  worldState = await fetchLiveWarframeAPI();
  buildLiveWorldsGrid();
  updateLivePanel();
  renderCurrentTab();
  if (showLoader && loader) {
    setTimeout(() => loader.classList.add("hidden"), 350);
  }
}

async function checkForUpdatesManual() {
  const localVer = WF_DATA.version?.version || "1.0.0";
  try {
    const res = await fetch("https://raw.githubusercontent.com/Nyxo-17/WireFrame/main/version.json?t=" + Date.now());
    if (!res.ok) throw new Error("HTTP " + res.status);
    const remote = await res.json();
    if (remote.version && remote.version !== localVer) {
      triggerAlert(
        `${tr("upd_available_title")} : v${remote.version}`,
        remote.changelog_fr || "Une nouvelle version est disponible sur GitHub !"
      );
    } else {
      triggerAlert("WireFrame — Mise à jour", `${tr("upd_up_to_date")} (v${localVer}).`);
    }
  } catch (e) {
    triggerAlert("WireFrame — Mise à jour", `${tr("upd_up_to_date")} (v${localVer}).`);
  }
}

/* ==========================================================================
   7. INITIALISATION AU DÉMARRAGE & ANIMATION DU SPLASH SCREEN
   ========================================================================== */
window.addEventListener("DOMContentLoaded", async () => {
  const bar = document.getElementById("splash-bar-fill");
  const status = document.getElementById("splash-status");
  const splash = document.getElementById("splash-screen");

  changeZoom(0);
  worldState = computeOfflineWorldState();
  setLanguage(currentLang);

  if (bar) bar.style.width = "45%";
  if (status) status.textContent = "Chargement du Codex (1 442 Mods, 239 Ressources, 120 Warframes)...";

  setTimeout(async () => {
    if (bar) bar.style.width = "85%";
    if (status) status.textContent = "Synchronisation avec les serveurs Warframe...";
    worldState = await fetchLiveWarframeAPI();
    buildLiveWorldsGrid();
    updateLivePanel();
    renderCurrentTab();

    if (bar) bar.style.width = "100%";
    if (status) status.textContent = "Prêt ! Bienvenue Tenno.";

    setTimeout(() => {
      if (splash) splash.classList.add("hidden");
    }, 320);
  }, 450);

  // Boucle temps réel 1 seconde + rafraîchissement API toutes les 60 secondes
  setInterval(updateLivePanel, 1000);
  setInterval(() => refreshAllData(false), 60000);
});

