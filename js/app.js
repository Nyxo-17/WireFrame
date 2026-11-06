/* ==========================================================================
   WireFrame HTML5 / ES6 — Moteur Temps Réel 144 FPS & Codex (par Nyxo_17)
   ========================================================================== */

const WF_DATA = window.WIREFRAME_DATA || {
  codex: { warframes: [], weapons: [], resources: [], mods: [], relics: [], bounties: [] },
  duviri: { warframes_weeks: [], incarnon_weeks: [] },
  translations: { fr: {}, en: {} },
  version: { version: "1.0.35" }
};

let currentLang = localStorage.getItem("wf_lang") || "fr";
let currentZoom = parseInt(localStorage.getItem("wf_zoom") || "100", 10);
let currentFps = parseInt(localStorage.getItem("wf_fps") || "144", 10);
let currentTheme = localStorage.getItem("wf_theme") || "dark";
let showRightPanel = localStorage.getItem("wf_right_panel") !== "false";
let currentTab = "welcome";

// État de la recherche et des filtres Codex
const codexState = {
  resources: { query: "", filter: "all" },
  mods: { query: "", filter: "all" },
  warframes: { query: "", filter: "all" },
  weapons: { query: "", filter: "all" },
  relics: { query: "", filter: "all" }
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
    },
    news: [
      {
        title_fr: "Le t-shirt \"Definitely the Lotus\" est maintenant disponible",
        title_en: "\"Definitely The Lotus\" T-Shirt Available Now",
        link: "https://store.warframe.com/collections/featured/products/definitely-the-lotus-t-shirt",
        image: "https://www-static.warframe.com/uploads/thumbnails/bda201fce9f7dbf314713007e046c889_1600x900.jpg",
        date: "2026-11-02T21:35:00.000Z"
      },
      {
        title_fr: "Community Stream & Twitch Drop Schedule",
        title_en: "Community Stream & Twitch Drop Schedule",
        link: "https://forums.warframe.com/topic/1531432-community-stream-schedule-november-2-8-2026/",
        image: "https://media.invisioncic.com/Mwarframe/monthly_2026_05/EM335_Drops.jpg.f9b99bce3373a1b10af4d2deafeb2daa.jpg",
        date: "2026-11-02T20:51:00.000Z"
      },
      {
        title_fr: "Lisez le Résumé du Devstream 198",
        title_en: "Read Now: Devstream 198 Overview",
        link: "https://www.warframe.com/news/devstream-198-overview",
        image: "https://www-static.warframe.com/uploads/8175be244877c6b48e13a1a49e3bbcf1.png",
        date: "2026-11-02T20:25:00.000Z"
      },
      {
        title_fr: "Movember 2026",
        title_en: "Movember 2026",
        link: "https://www.warframe.com/en/news/movember-2026",
        image: "https://www-static.warframe.com/uploads/14ec028261a5f8c6bb627876a890482f.png",
        date: "2026-11-02T08:56:00.000Z"
      },
      {
        title_fr: "Warframe : Tau arrive en décembre",
        title_en: "Warframe: Tau Coming in December",
        link: "https://www.warframe.com/tau",
        image: "https://www-static.warframe.com/uploads/2e36b9c6bfb025a324113c5840245ace.png",
        date: "2026-10-30T18:30:00.000Z"
      },
      {
        title_fr: "Précommandez dès maintenant : Collection de Produits Dérivés Portau",
        title_en: "Preorder Now: Portau Merch Collection",
        link: "https://www.warframe.com/en/news/portau-collection-coming-soon",
        image: "https://www-static.warframe.com/uploads/a18b62951254df7dd0563b899d380d29.jpg",
        date: "2026-10-30T11:07:00.000Z"
      },
      {
        title_fr: "Résurgence Prime : Nidus Prime et Saryn Prime !",
        title_en: "Prime Resurgence: Nidus Prime and Saryn Prime!",
        link: "https://www.warframe.com/prime-resurgence",
        image: "https://www-static.warframe.com/uploads/8f5e71995c1f45edf570da1f53d73711.png",
        date: "2026-10-29T14:13:00.000Z"
      },
      {
        title_fr: "Iceblade of Narin: The Icebind: Hotfix 44.1.4",
        title_en: "Iceblade of Narin: The Icebind: Hotfix 44.1.4",
        link: "https://www.warframe.com/en/patch-notes/pc/44-1-4",
        image: "https://cdn.warframestat.us/genesis/img/news-placeholder.png",
        date: "2026-10-27T15:06:00.000Z"
      },
      {
        title_fr: "Known Issues List — Warframe Forums",
        title_en: "Known Issues List — Warframe Forums",
        link: "https://forums.warframe.com/topic/1523875-known-issues-iceblade-of-narin/",
        image: "https://cdn.warframestat.us/genesis/img/news-placeholder.png",
        date: "2026-09-23T15:15:00.000Z"
      }
    ]
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
      },
      news: Array.isArray(raw.news) && raw.news.length > 0
        ? raw.news
            .slice()
            .sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0))
            .slice(0, 15)
            .map((n) => ({
              title_fr: (n.translations && n.translations.fr) || n.message || "Actualité Warframe",
              title_en: (n.translations && n.translations.en) || n.message || "Warframe News",
              link: n.link || "https://www.warframe.com/fr/news",
              image: n.imageLink || "data/app_logo.png",
              date: n.date || "",
              eta: n.eta || ""
            }))
        : fallback.news
    };
  } catch (err) {
    return fallback;
  }
}

/* ==========================================================================
   3. PANNEAU LATÉRAL DROIT EN DIRECT & COMPTE À REBOURS 1 SECONDE
   ========================================================================== */
function formatNewsDate(isoStr) {
  if (!isoStr) return "Officiel";
  const d = new Date(isoStr);
  if (isNaN(d.getTime())) return "Officiel";
  const diffDays = Math.max(0, Math.floor((Date.now() - d.getTime()) / 86400000));
  if (diffDays === 0) return currentLang === "fr" ? "Aujourd'hui" : "Today";
  if (diffDays === 1) return currentLang === "fr" ? "Hier" : "Yesterday";
  return currentLang === "fr" ? `Il y a ${diffDays}j` : `${diffDays}d ago`;
}

function buildLiveNewsList() {
  const listEl = document.getElementById("live-news-list");
  if (!listEl || !worldState) return;

  const titleEl = document.getElementById("live-news-title");
  if (titleEl) {
    titleEl.textContent = currentLang === "fr" ? "❖ Actualités Officielles" : "❖ Official Warframe News";
  }
  const allLinkEl = document.getElementById("live-news-all");
  if (allLinkEl) {
    allLinkEl.href = currentLang === "fr" ? "https://www.warframe.com/fr/news" : "https://www.warframe.com/news";
  }

  const newsItems = worldState.news || [];
  listEl.innerHTML = newsItems
    .map((n) => {
      const title = currentLang === "fr" ? n.title_fr : n.title_en;
      const dateLbl = formatNewsDate(n.date);
      const imgUrl = n.image || "data/app_logo.png";
      return `
        <a href="${n.link}" target="_blank" class="news-card" title="${title.replace(/"/g, "&quot;")}">
          <img src="${imgUrl}" alt="News" class="news-thumb" loading="lazy" onerror="this.onerror=null;this.src='data/app_logo.png';" />
          <div class="news-body">
            <div class="news-title">${title}</div>
            <div class="news-meta">◈ Warframe.com • ${dateLbl}</div>
          </div>
        </a>
      `;
    })
    .join("");
}

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
  if (statusEl) statusEl.textContent = "❖ " + worldState.source;

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
      ? `● ${tr("baro_present")} : ${baro.location}`
      : `◷ ${tr("baro_arrives")} : ${baro.location}`;
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
    tTitle.textContent = "◈ " + title;
    tMsg.textContent = message;
    banner.classList.remove("hidden");
    clearTimeout(window._toastTimeout);
    window._toastTimeout = setTimeout(() => banner.classList.add("hidden"), 5000);
  }

  // Notification système navigateur/Windows si autorisée
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification(title, { body: message, icon: "data/app_logo.png" });
  }

  if (currentTab === "settings" || currentTab === "notifications") {
    renderSettingsView();
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
    case "settings":
    case "notifications":
      renderSettingsView(container);
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
    case "weapons":
      renderCodexView(container, "weapons", tr("wpn_page_title"));
      break;
    case "relics":
      renderCodexView(container, "relics", tr("rel_page_title"));
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
    { title: tr("card_wpn_title"), desc: tr("card_wpn_desc"), tab: "weapons" },
    { title: tr("card_rel_title"), desc: tr("card_rel_desc"), tab: "relics" },
    {
      title: currentLang === "fr" ? "◎  6. Temps des Planètes" : "◎  6. Planet Timers",
      desc: tr("card_wld_desc"),
      tab: "worlds"
    },
    {
      title: currentLang === "fr" ? "⌖  7. Mises à Prix (Rotations A/B/C)" : "⌖  7. Bounties (Rotations A/B/C)",
      desc: tr("card_bnt_desc"),
      tab: "bounties"
    },
    {
      title: currentLang === "fr" ? "⟡  8. Le Circuit de Duviri & Incarnon" : "⟡  8. The Duviri Circuit & Incarnon",
      desc: tr("card_cir_desc"),
      tab: "duviri"
    },
    {
      title: currentLang === "fr" ? "❖  9. Marchand du Néant — Baro Ki'Teer" : "❖  9. Void Trader — Baro Ki'Teer",
      desc: tr("card_baro_desc"),
      tab: "baro"
    },
    {
      title:
        currentLang === "fr"
          ? "❖  10. Paramètres, 20 Thèmes, FPS & Notifications"
          : "❖  10. Settings, 20 Themes, FPS & Notifications",
      desc:
        currentLang === "fr"
          ? "Personnalisation complète avec 20 thèmes visuels (Sombre, Clair, OLED, Bleu, Cyan, Vert, Jaune, Rouge, Orange, Violet, Rose), fluidité 30 à 144 FPS et alertes sonores en direct."
          : "Full customization with 20 visual themes (Dark, Light, OLED, Blue, Cyan, Green, Yellow, Red, Orange, Purple, Pink), 30 to 144 FPS smoothness and live sound alerts.",
      tab: "settings"
    },
    {
      title:
        currentLang === "fr"
          ? "❖  11. Actualités Warframe & Discord Officiel"
          : "❖  11. Official Warframe News & Discord",
      desc: tr("card_news_desc"),
      extUrl: "https://discord.gg/DhGwHPf82n",
      extBtn: "❖ Discord ➔"
    }
  ];

  const stats = [
    { icon: "◈", val: "239", lbl: currentLang === "fr" ? "Ressources" : "Resources", tab: "resources" },
    { icon: "⬡", val: "1 442", lbl: "Mods", tab: "mods" },
    { icon: "✦", val: "120", lbl: "Warframes", tab: "warframes" },
    { icon: "⚔", val: "635", lbl: currentLang === "fr" ? "Armes" : "Weapons", tab: "weapons" },
    { icon: "⬡", val: "801", lbl: currentLang === "fr" ? "Reliques" : "Relics", tab: "relics" },
    { icon: "◎", val: "24/7", lbl: currentLang === "fr" ? "Cycles Direct" : "Live Cycles", tab: "worlds" },
    { icon: "❖", val: "20 Thèmes", lbl: currentLang === "fr" ? "Paramètres" : "Settings", tab: "settings" }
  ];

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
      <div class="view-header-title" style="margin-bottom:0;">${currentLang === "fr" ? "Accueil — WireFrame" : "Home — WireFrame"}</div>
      <div style="display:flex; align-items:center; gap:10px;">
        <button class="btn-open" onclick="selectTab('settings')" style="padding:6px 14px; font-size:12.5px; display:inline-flex; align-items:center; gap:6px;">
          ❖ ${currentLang === "fr" ? "Paramètres & Thèmes" : "Settings & Themes"}
        </button>
        <div style="display:flex; align-items:center; gap:8px; background:#141A29; border:1px solid #263554; padding:5px 12px; border-radius:8px;">
          <img src="data/app_logo.png" alt="Nyxo_17" style="width:24px; height:24px; object-fit:contain;" />
          <span style="font-size:12px; color:#8B949E;">${tr("created_by")} <strong style="color:#58A6FF;">Nyxo_17</strong></span>
        </div>
      </div>
    </div>

    <div class="welcome-banner">
      <h3>${tr("welcome_banner_title")}</h3>
      <p>${tr("welcome_banner_desc")}</p>
    </div>

    <div style="display:grid; grid-template-columns:repeat(7, 1fr); gap:10px; margin-bottom:14px;">
      ${stats
        .map(
          (s) => `
        <div onclick="selectTab('${s.tab}')" style="background:#141A29; border:1px solid #232F46; border-radius:10px; padding:10px; text-align:center; cursor:pointer; transition:all 0.18s ease;" onmouseover="this.style.borderColor='#58A6FF'" onmouseout="this.style.borderColor='#232F46'">
          <div style="font-size:18px; font-weight:800; color:#79C0FF;">${s.icon} ${s.val}</div>
          <div style="font-size:11.5px; color:#8B949E; font-weight:600; margin-top:2px;">${s.lbl}</div>
        </div>
      `
        )
        .join("")}
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
          ${
            c.extUrl
              ? `<a href="${c.extUrl}" target="_blank" class="btn-open" style="text-decoration:none;">${c.extBtn}</a>`
              : `<button class="btn-open" onclick="selectTab('${c.tab}')">${tr("open_btn")}</button>`
          }
        </div>
      `
        )
        .join("")}
    </div>
  `;
}

/* --- VUE 2 : PARAMÈTRES (THÈME, FPS & CENTRE DE NOTIFICATIONS) --- */
function setTheme(themeKey) {
  const valid = [
    "dark",
    "light",
    "full-black",
    "full-white",
    "blue-dark",
    "blue-light",
    "cyan-dark",
    "cyan-light",
    "green-dark",
    "green-light",
    "yellow-dark",
    "yellow-light",
    "red-dark",
    "red-light",
    "orange-dark",
    "orange-light",
    "purple-dark",
    "purple-light",
    "pink-dark",
    "pink-light"
  ];
  currentTheme = valid.includes(themeKey) ? themeKey : "dark";
  localStorage.setItem("wf_theme", currentTheme);
  document.documentElement.setAttribute("data-theme", currentTheme);

  if (currentTab === "settings" || currentTab === "notifications") {
    renderSettingsView();
  }
}

function setFps(fpsVal) {
  const valid = [30, 60, 120, 144];
  currentFps = valid.includes(Number(fpsVal)) ? Number(fpsVal) : 144;
  localStorage.setItem("wf_fps", String(currentFps));

  const tagEl = document.getElementById("topbar-fps-tag");
  if (tagEl) {
    tagEl.textContent = `HTML5 • ${currentFps} FPS`;
  }

  // Adapte la réactivité des transitions CSS selon le mode FPS choisi
  const durMap = { 30: "0.36s", 60: "0.24s", 120: "0.16s", 144: "0.12s" };
  document.documentElement.style.setProperty("--fps-transition", durMap[currentFps] || "0.16s");

  if (currentTab === "settings" || currentTab === "notifications") {
    renderSettingsView();
  }
}

function toggleRightPanel(forceState) {
  if (typeof forceState === "boolean") {
    showRightPanel = forceState;
  } else {
    showRightPanel = !showRightPanel;
  }
  localStorage.setItem("wf_right_panel", String(showRightPanel));

  const panel = document.getElementById("right-live-panel");
  if (panel) {
    panel.classList.toggle("collapsed", !showRightPanel);
  }

  const btn = document.getElementById("btn-toggle-live");
  if (btn) {
    btn.classList.toggle("active", showRightPanel);
  }
  const lbl = document.getElementById("lbl-toggle-live");
  if (lbl) {
    if (currentLang === "fr") {
      lbl.textContent = showRightPanel ? "Cacher Direct" : "Afficher Direct";
    } else {
      lbl.textContent = showRightPanel ? "Hide Live" : "Show Live";
    }
  }

  if (currentTab === "settings" || currentTab === "notifications") {
    renderSettingsView();
  }
}

function renderSettingsView(container = document.getElementById("center-zoom-content")) {
  if (!container) return;
  const switches = [
    { key: "planets", label: tr("notif_sw_planets") },
    { key: "baro", label: tr("notif_sw_baro") },
    { key: "bounties", label: tr("notif_sw_bounties") },
    { key: "incarnon", label: tr("notif_sw_incarnon") },
    { key: "warframes", label: tr("notif_sw_warframes") },
    { key: "sound", label: tr("notif_sw_sound") }
  ];

  const fpsOptions = [
    {
      fps: 30,
      label: "30 FPS",
      sub: currentLang === "fr" ? "◈ Économie d'énergie" : "◈ Power Saving"
    },
    {
      fps: 60,
      label: "60 FPS",
      sub: currentLang === "fr" ? "❖ Standard équilibré" : "❖ Balanced Standard"
    },
    {
      fps: 120,
      label: "120 FPS",
      sub: currentLang === "fr" ? "▲ Haute fluidité" : "▲ High Smoothness"
    },
    {
      fps: 144,
      label: "144 FPS",
      sub: currentLang === "fr" ? "✦ Ultra Réactif (Max)" : "✦ Ultra Responsive (Max)"
    }
  ];

  const themeOptions = [
    {
      id: "dark",
      label: currentLang === "fr" ? "◐ Sombre" : "◐ Dark",
      sub: currentLang === "fr" ? "Sci-Fi Bleu Nuit (Défaut)" : "Sci-Fi Midnight (Default)"
    },
    {
      id: "light",
      label: currentLang === "fr" ? "☼ Clair" : "☼ Light",
      sub: currentLang === "fr" ? "Clair & Doux" : "Soft Light"
    },
    {
      id: "full-black",
      label: "◆ Full Black",
      sub: currentLang === "fr" ? "Noir Pur OLED (#000)" : "Pure Black OLED (#000)"
    },
    {
      id: "full-white",
      label: "◇ Full White",
      sub: currentLang === "fr" ? "Blanc Pur (#FFF)" : "Pure White (#FFF)"
    },
    {
      id: "blue-dark",
      label: currentLang === "fr" ? "⬡ Bleu Sombre" : "⬡ Dark Blue",
      sub: currentLang === "fr" ? "Corpus & Prisma" : "Corpus & Prisma"
    },
    {
      id: "blue-light",
      label: currentLang === "fr" ? "✧ Bleu Clair" : "✧ Light Blue",
      sub: currentLang === "fr" ? "Glace de Fortuna & Azur" : "Fortuna Ice & Azure"
    },
    {
      id: "cyan-dark",
      label: currentLang === "fr" ? "⬡ Cyan Sombre" : "⬡ Dark Cyan",
      sub: currentLang === "fr" ? "Céphalon & Cryotique" : "Cephalon & Cryotic"
    },
    {
      id: "cyan-light",
      label: currentLang === "fr" ? "✧ Cyan Clair" : "✧ Light Cyan",
      sub: currentLang === "fr" ? "Lagon & Cristal Clair" : "Lagoon & Clear Crystal"
    },
    {
      id: "green-dark",
      label: currentLang === "fr" ? "❖ Vert Sombre" : "❖ Dark Green",
      sub: currentLang === "fr" ? "Émeraude & Forêts" : "Emerald & Earth Forests"
    },
    {
      id: "green-light",
      label: currentLang === "fr" ? "✦ Vert Clair" : "✦ Light Green",
      sub: currentLang === "fr" ? "Jade & Menthe Claire" : "Soft Jade & Mint"
    },
    {
      id: "yellow-dark",
      label: currentLang === "fr" ? "◆ Jaune Sombre" : "◆ Dark Yellow",
      sub: currentLang === "fr" ? "Or Orokin & Prime" : "Orokin Gold & Prime"
    },
    {
      id: "yellow-light",
      label: currentLang === "fr" ? "☼ Jaune Clair" : "☼ Light Yellow",
      sub: currentLang === "fr" ? "Solaire & Ivoire Doré" : "Solar & Golden Ivory"
    },
    {
      id: "red-dark",
      label: currentLang === "fr" ? "◈ Rouge Sombre" : "◈ Dark Red",
      sub: currentLang === "fr" ? "Kuva & Voile Rouge" : "Kuva & Red Veil"
    },
    {
      id: "red-light",
      label: currentLang === "fr" ? "✦ Rouge Clair" : "✦ Light Red",
      sub: currentLang === "fr" ? "Carmin Clair & Rose" : "Soft Crimson Light"
    },
    {
      id: "orange-dark",
      label: currentLang === "fr" ? "☼ Orange Sombre" : "☼ Dark Orange",
      sub: currentLang === "fr" ? "Ember & Fusion Solaire" : "Ember & Solar Fusion"
    },
    {
      id: "orange-light",
      label: currentLang === "fr" ? "◎ Orange Clair" : "◎ Light Orange",
      sub: currentLang === "fr" ? "Ambre Clair & Cuivre" : "Soft Amber & Copper"
    },
    {
      id: "purple-dark",
      label: currentLang === "fr" ? "⟡ Violet Sombre" : "⟡ Dark Purple",
      sub: currentLang === "fr" ? "Lotus & Énergie du Néant" : "Lotus & Void Energy"
    },
    {
      id: "purple-light",
      label: currentLang === "fr" ? "❖ Violet Clair" : "❖ Light Purple",
      sub: currentLang === "fr" ? "Améthyste & Lavande" : "Amethyst & Lavender"
    },
    {
      id: "pink-dark",
      label: currentLang === "fr" ? "❖ Rose Sombre" : "❖ Dark Pink",
      sub: currentLang === "fr" ? "Octavia & Néon Magenta" : "Octavia & Neon Magenta"
    },
    {
      id: "pink-light",
      label: currentLang === "fr" ? "✦ Rose Clair" : "✦ Light Pink",
      sub: currentLang === "fr" ? "Cerisier & Quartz Rose" : "Cherry Blossom & Rose Quartz"
    }
  ];

  container.innerHTML = `
    <div class="view-header-title">${tr("settings_page_title")}</div>
    <div class="view-header-sub">${tr("settings_page_sub")}</div>

    <!-- BLOC 0 : CHOIX DU THÈME VISUEL (20 THÈMES) -->
    <div class="bounty-card" style="padding:16px; margin-bottom:16px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <div style="font-size:15px; font-weight:700; color:var(--accent-blue);">
          ❖ ${currentLang === "fr" ? "Thème de l'Interface" : "Interface Theme"}
        </div>
        <span style="font-size:12px; font-weight:700; color:var(--accent-green); background:rgba(74,222,128,0.12); border:1px solid rgba(74,222,128,0.35); padding:2px 10px; border-radius:12px;">
          ● ${(themeOptions.find((t) => t.id === currentTheme) || themeOptions[0]).label}
        </span>
      </div>
      <div style="font-size:12.5px; color:var(--text-muted); margin-bottom:10px;">
        ${
          currentLang === "fr"
            ? "Choisis l'apparence visuelle de WireFrame parmi les 20 thèmes (Sombre, Clair, OLED, Bleu, Cyan, Vert, Jaune, Rouge, Orange, Violet, Rose) :"
            : "Select the visual theme for WireFrame among the 20 themes (Dark, Light, OLED, Blue, Cyan, Green, Yellow, Red, Orange, Purple, Pink):"
        }
      </div>

      <div class="fps-selector-grid" style="grid-template-columns: repeat(4, 1fr);">
        ${themeOptions
          .map(
            (th) => `
          <button class="fps-pill-btn ${currentTheme === th.id ? "active" : ""}" onclick="setTheme('${th.id}')">
            <span class="fps-pill-hz">${th.label}</span>
            <span class="fps-pill-desc">${th.sub}</span>
          </button>
        `
          )
          .join("")}
      </div>
    </div>

    <!-- BLOC 1 : CHOIX DES FPS (30 / 60 / 120 / 144) -->
    <div class="bounty-card" style="padding:16px; margin-bottom:16px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <div style="font-size:15px; font-weight:700; color:var(--accent-blue);">${tr("fps_sec_title")}</div>
        <span style="font-size:12px; font-weight:700; color:var(--accent-green); background:rgba(74,222,128,0.12); border:1px solid rgba(74,222,128,0.35); padding:2px 10px; border-radius:12px;">
          ● ${currentFps} FPS ${currentLang === "fr" ? "Actif" : "Active"}
        </span>
      </div>
      <div style="font-size:12.5px; color:var(--text-muted); margin-bottom:10px;">${tr("fps_sec_desc")}</div>

      <div class="fps-selector-grid">
        ${fpsOptions
          .map(
            (opt) => `
          <button class="fps-pill-btn ${currentFps === opt.fps ? "active" : ""}" onclick="setFps(${opt.fps})">
            <span class="fps-pill-hz">${opt.label}</span>
            <span class="fps-pill-desc">${opt.sub}</span>
          </button>
        `
          )
          .join("")}
      </div>

      <div style="margin-top:14px; padding-top:12px; border-top:1px solid var(--border-subtle);">
        <label style="display:flex; align-items:center; gap:12px; cursor:pointer; font-size:13px; color:var(--text-main);">
          <input type="checkbox" ${showRightPanel ? "checked" : ""} onchange="toggleRightPanel(this.checked)" style="width:17px; height:17px; accent-color:var(--accent-blue); cursor:pointer;" />
          <span>${
            currentLang === "fr"
              ? "❖  Afficher la colonne de droite (Actualités Officielles Warframe)"
              : "❖  Show right-hand column (Official Warframe News)"
          }</span>
        </label>
      </div>
    </div>

    <!-- BLOC 2 : CENTRE DE NOTIFICATIONS & ALERTES EN DIRECT -->
    <div class="view-header-title" style="font-size:16px; margin:8px 0 4px 0; color:var(--accent-blue);">
      ${tr("notif_page_title")}
    </div>
    <div class="view-header-sub" style="margin-bottom:10px;">${tr("notif_page_sub")}</div>

    <div class="bounty-card" style="padding:16px;">
      ${switches
        .map(
          (sw) => `
        <label style="display:flex; align-items:center; gap:12px; padding:8px 4px; cursor:pointer; font-size:13px; color:var(--text-main);">
          <input type="checkbox" ${notifPrefs[sw.key] ? "checked" : ""} onchange="toggleNotifPref('${sw.key}', this.checked)" style="width:17px; height:17px; accent-color:var(--accent-blue); cursor:pointer;" />
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

    <div class="view-header-title" style="font-size:15px; margin:16px 0 8px 0; color:var(--accent-blue);">
      ${tr("notif_history_title")}
    </div>
    <div class="bounty-card" style="padding:14px;">
      ${
        notifHistory.length === 0
          ? `<div style="color:var(--text-muted); font-size:12.5px;">${tr("notif_empty_history")}</div>`
          : notifHistory
              .map(
                (h) => `
            <div style="padding:6px 0; border-bottom:1px solid var(--border-subtle); font-size:12.5px;">
              <span style="color:var(--accent-blue); font-weight:700;">[${h.time}] ${h.title}</span> —
              <span style="color:var(--text-main);">${h.message}</span>
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

/* --- VUES 3, 4, 5 : CODEX EN GRILLE (RESSOURCES, MODS, WARFRAMES) + MODALE --- */
function cleanDropText(rawDrop) {
  if (!rawDrop) return "";
  return rawDrop
    // Supprime les balises internes Warframe (ex: <DT_PUNCTURE_COLOR>)
    .replace(/<[^>]+>/g, "")
    // Corrige les pourcentages multipliés par 100 dans les données brutes (ex: 3333.00% -> 33.33%)
    .replace(/(\d{3,5})\.(\d{2})%/g, (match) => {
      const num = parseFloat(match) / 100;
      return num.toFixed(num % 1 === 0 ? 0 : 2) + "%";
    });
}

function formatGridBadge(rawCat) {
  if (!rawCat) return "Codex";
  return rawCat
    .replace("Warframe Standard • ", "")
    .replace("Warframe Prime • ", "✦ Prime • ");
}

const CODEX_FILTERS = {
  relics: [
    { id: "all", fr: "Tout", en: "All", fn: () => true },
    { id: "active", fr: "● Actives (En jeu)", en: "● Active (In-game)", fn: (it) => (it.category || "").includes("Active") },
    { id: "vaulted", fr: "⬡ Vaultées (Soute)", en: "⬡ Vaulted", fn: (it) => (it.category || "").includes("Vaultée") },
    { id: "lith", fr: "Lith", en: "Lith", fn: (it) => (it.name || "").startsWith("Lith ") },
    { id: "meso", fr: "Meso", en: "Meso", fn: (it) => (it.name || "").startsWith("Meso ") },
    { id: "neo", fr: "Neo", en: "Neo", fn: (it) => (it.name || "").startsWith("Neo ") },
    { id: "axi", fr: "Axi", en: "Axi", fn: (it) => (it.name || "").startsWith("Axi ") },
    { id: "requiem", fr: "Requiem", en: "Requiem", fn: (it) => (it.name || "").startsWith("Requiem ") }
  ],
  warframes: [
    { id: "all", fr: "Tout", en: "All", fn: () => true },
    { id: "prime", fr: "✦ Warframes Prime", en: "✦ Prime Warframes", fn: (it) => (it.category || "").includes("Prime") },
    { id: "standard", fr: "❖ Warframes Standard", en: "❖ Standard Warframes", fn: (it) => (it.category || "").includes("Standard") },
    {
      id: "tank",
      fr: "♥ Tanks (PV > 400)",
      en: "♥ Tanks (HP > 400)",
      fn: (it) => {
        const m = (it.category || "").match(/♥\s*(\d+)/);
        return m ? parseInt(m[1], 10) > 400 : false;
      }
    }
  ],
  weapons: [
    { id: "all", fr: "Tout", en: "All", fn: () => true },
    { id: "primary", fr: "⌖ Principales", en: "⌖ Primary", fn: (it) => (it.category || "").includes("Principale") },
    { id: "secondary", fr: "⌖ Secondaires", en: "⌖ Secondary", fn: (it) => (it.category || "").includes("Secondaire") },
    { id: "melee", fr: "⚔ Mêlée", en: "⚔ Melee", fn: (it) => (it.category || "").includes("Mêlée") && !(it.category || "").includes("Arch-Mêlée") },
    { id: "arch", fr: "▲ Arch-Armes", en: "▲ Arch-Weapons", fn: (it) => (it.category || "").includes("Arch-") },
    { id: "prime", fr: "✦ Prime", en: "✦ Prime", fn: (it) => (it.category || "").includes("Prime") },
    { id: "kuva_tenet", fr: "◈ Kuva, Principe & Coda", en: "◈ Kuva, Tenet & Coda", fn: (it) => /Kuva|Principe|Coda/i.test(it.category || "") },
    { id: "incarnon", fr: "⟡ Incarnon", en: "⟡ Incarnon", fn: (it) => (it.category || "").includes("Incarnon") }
  ],
  mods: [
    { id: "all", fr: "Tout", en: "All", fn: () => true },
    { id: "wf", fr: "✦ Warframe & Aura", en: "✦ Warframe & Aura", fn: (it) => /warframe|aura|exilus/i.test(it.category || "") },
    { id: "primary", fr: "⌖ Fusil & Pompe", en: "⌖ Rifle & Shotgun", fn: (it) => /rifle|shotgun|primary|bow|sniper/i.test(it.category || "") },
    { id: "pistol", fr: "⌖ Pistolet", en: "⌖ Pistol", fn: (it) => /pistol|secondary/i.test(it.category || "") },
    { id: "melee", fr: "⚔ Mêlée & Postures", en: "⚔ Melee & Stances", fn: (it) => /melee|stance|claws|sword|dagger|hammer|polearm|staff|nikana|scythe|whip|fist|glaive|machete|rapier|sparring|tonfa|nunchaku|heavy blade|dual|blade|shield|warfan|two-handed/i.test(it.category || "") },
    { id: "companion", fr: "❖ Compagnon", en: "❖ Companion", fn: (it) => /companion|kubrow|kavat|sentinel|beast|robotic|hound|moa/i.test(it.category || "") },
    { id: "vehic", fr: "❖ Archwing / Necramech / Railjack", en: "❖ Archwing / Necramech / Railjack", fn: (it) => /arch|necramech|plexus|k-drive|parazon/i.test(it.category || "") },
    { id: "legendary", fr: "◈ Légendaire (Accru)", en: "◈ Legendary (Primed)", fn: (it) => (it.category || "").includes("Legendary") },
    { id: "rare", fr: "◆ Rare (Or)", en: "◆ Rare (Gold)", fn: (it) => (it.category || "").includes("• Rare") },
    { id: "uncommon", fr: "○ Inhabituel (Argent)", en: "○ Uncommon (Silver)", fn: (it) => (it.category || "").includes("Uncommon") },
    { id: "common", fr: "◇ Commun (Bronze)", en: "◇ Common (Bronze)", fn: (it) => /• Common|• Commun/i.test(it.category || "") }
  ],
  resources: [
    { id: "all", fr: "Tout", en: "All", fn: () => true },
    { id: "res", fr: "⬡ Ressources & Composants", en: "⬡ Resources & Parts", fn: (it) => it.category === "Resource" },
    { id: "gem", fr: "◈ Gemmes & Minerais", en: "◈ Gems & Ores", fn: (it) => it.category === "Gem" },
    { id: "plant", fr: "✦ Plantes", en: "✦ Plants", fn: (it) => it.category === "Plant" },
    { id: "cetus", fr: "◎ Cetus / Terre", en: "◎ Cetus / Earth", fn: (it) => /cetus|earth|eidolon|thumper|ostron/i.test((it.location || "") + " " + (it.drop || "")) },
    { id: "vallis", fr: "✦ Orb Vallis / Fortuna", en: "✦ Orb Vallis / Fortuna", fn: (it) => /vallis|venus|fortuna|solaris|profit-taker/i.test((it.location || "") + " " + (it.drop || "")) },
    { id: "deimos", fr: "⟡ Deimos / Cambion", en: "⟡ Deimos / Cambion", fn: (it) => /deimos|cambion|necralisk|entrati|albrecht/i.test((it.location || "") + " " + (it.drop || "")) },
    { id: "duviri", fr: "⟡ Duviri", en: "⟡ Duviri", fn: (it) => /duviri/i.test((it.location || "") + " " + (it.drop || "")) },
    { id: "1999", fr: "⟡ 1999 (Höllvania)", en: "⟡ 1999 (Höllvania)", fn: (it) => /1999|höllvania|hex/i.test((it.location || "") + " " + (it.drop || "")) }
  ]
};

function getFilteredCodexItems(categoryKey) {
  const st = codexState[categoryKey];
  const allItems = WF_DATA.codex[categoryKey] || [];
  const q = (st.query || "").trim().toLowerCase();
  const activeFilterId = st.filter || "all";
  const filterDef = (CODEX_FILTERS[categoryKey] || []).find((f) => f.id === activeFilterId);
  const filterFn = filterDef ? filterDef.fn : () => true;

  return allItems.filter((it) => {
    if (!filterFn(it)) return false;
    if (!q) return true;
    return (
      (it.name || "").toLowerCase().includes(q) ||
      (it.category || "").toLowerCase().includes(q) ||
      (it.location || "").toLowerCase().includes(q) ||
      (it.drop || "").toLowerCase().includes(q)
    );
  });
}

let codexRenderedCount = 0;
let codexObserver = null;
const CODEX_BATCH_SIZE = 48;

function setCodexFilter(categoryKey, filterId) {
  codexState[categoryKey].filter = filterId;
  const filtered = getFilteredCodexItems(categoryKey);
  window._currentCodexFiltered = filtered;

  document.querySelectorAll(".filter-pill").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-fid") === filterId);
  });

  resetAndRenderCodexGrid(filtered);
}

function renderCodexView(container, categoryKey, title) {
  const st = codexState[categoryKey];
  const filtered = getFilteredCodexItems(categoryKey);
  window._currentCodexFiltered = filtered;
  const filters = CODEX_FILTERS[categoryKey] || [];
  const curFilter = st.filter || "all";

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
      <div class="view-header-title" style="margin-bottom:0;">${title}</div>
      <div id="codex-count-label" style="font-size:12px; font-weight:700; color:#58A6FF;">
        ${filtered.length} ${currentLang === "fr" ? "éléments trouvés" : "items found"}
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

    <div class="codex-filters-bar">
      ${filters
        .map(
          (f) => `
        <button class="filter-pill ${curFilter === f.id ? "active" : ""}" data-fid="${f.id}" onclick="setCodexFilter('${categoryKey}', '${f.id}')">
          ${currentLang === "fr" ? f.fr : f.en}
        </button>
      `
        )
        .join("")}
    </div>

    <div id="codex-results-list" class="codex-grid"></div>
    <div id="codex-scroll-sentinel" style="height:28px; width:100%;"></div>
  `;

  resetAndRenderCodexGrid(filtered);
}

function resetAndRenderCodexGrid(filtered) {
  codexRenderedCount = 0;
  const listEl = document.getElementById("codex-results-list");
  if (!listEl) return;

  const countEl = document.getElementById("codex-count-label");
  if (countEl) {
    countEl.textContent = `${filtered.length} ${currentLang === "fr" ? "éléments trouvés" : "items found"}`;
  }

  if (!filtered.length) {
    listEl.innerHTML = `<div style="grid-column: 1 / -1; padding:24px; text-align:center; color:#8B949E;">Aucun résultat trouvé.</div>`;
    return;
  }

  listEl.innerHTML = "";
  appendNextCodexBatch();
  setupCodexScrollObserver();
}

function appendNextCodexBatch() {
  const filtered = window._currentCodexFiltered || [];
  const listEl = document.getElementById("codex-results-list");
  if (!listEl || codexRenderedCount >= filtered.length) return;

  const nextSlice = filtered.slice(codexRenderedCount, codexRenderedCount + CODEX_BATCH_SIZE);
  const html = renderCodexGridHTML(nextSlice, codexRenderedCount);
  listEl.insertAdjacentHTML("beforeend", html);
  codexRenderedCount += nextSlice.length;
}

function setupCodexScrollObserver() {
  if (codexObserver) {
    codexObserver.disconnect();
    codexObserver = null;
  }
  const sentinel = document.getElementById("codex-scroll-sentinel");
  const scrollRoot = document.querySelector(".center-container");
  if (!sentinel) return;

  codexObserver = new IntersectionObserver(
    (entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        appendNextCodexBatch();
      }
    },
    {
      root: scrollRoot || null,
      rootMargin: "550px"
    }
  );
  codexObserver.observe(sentinel);

  if (scrollRoot && !scrollRoot._hasCodexScrollListener) {
    scrollRoot._hasCodexScrollListener = true;
    scrollRoot.addEventListener(
      "scroll",
      () => {
        if (!["resources", "mods", "warframes", "weapons", "relics"].includes(currentTab)) return;
        const remaining = scrollRoot.scrollHeight - scrollRoot.scrollTop - scrollRoot.clientHeight;
        if (remaining < 600) {
          appendNextCodexBatch();
        }
      },
      { passive: true }
    );
  }
}

function renderCodexGridHTML(items, startOffset = 0) {
  if (!items.length) return "";
  return items
    .map((item, idx) => {
      const imgUrl = item.image
        ? `https://cdn.warframestat.us/img/${item.image}`
        : "data/app_logo.png";
      const globalIdx = startOffset + idx;
      const badgeTxt = formatGridBadge(item.category);
      return `
        <div class="codex-grid-card" onclick="openCodexModal(${globalIdx})" title="Cliquer pour voir les détails de ${item.name.replace(/"/g, "&quot;")}">
          <span class="codex-grid-badge">${badgeTxt}</span>
          <img src="${imgUrl}" alt="${item.name}" class="codex-grid-img" loading="lazy" decoding="async" onerror="this.onerror=null;this.src='data/app_logo.png';" />
          <div class="codex-grid-name">${item.name}</div>
        </div>
      `;
    })
    .join("");
}

const PLANET_VISUAL_RULES = [
  { match: /lua|circulus|yuvarium|copernicus|tycho|plato/i, name: "Lua", img: "https://cdn.warframestat.us/img/EmoteLua.png" },
  { match: /deimos|cambion|necralisk|albrecht|entrati lab|sanctum|cambire|munio|persto|armatus|effervo|magnacidium/i, name: "Deimos", img: "data/planets/deimos.png" },
  { match: /venus|vénus|orb vallis|vallée orbis|fortuna|vesper|kiliken|tessera/i, name: "Vénus (Orb Vallis)", img: "data/planets/venus.png" },
  { match: /earth|terre|cetus|eidolon|cervantes|everest|mariana|bendar|iota|korm/i, name: "Terre (Cetus)", img: "data/planets/earth.png" },
  { match: /zariman|halako|everview|greenway/i, name: "Zariman Ten Zero", img: "data/planets/zariman.png" },
  { match: /duviri|circuit|kullervo|isleweaver|orowyrm/i, name: "Duviri", img: "https://cdn.warframestat.us/img/EmoteDuviri.png" },
  { match: /höllvania|1999|wf1999|scaldra|techrot|hex/i, name: "Höllvania (1999)", img: "https://cdn.warframestat.us/img/EmoteLasria.png" },
  { match: /perita|dark refractory/i, name: "Dark Refractory (Perita)", img: "https://cdn.warframestat.us/img/EmotePerita.png" },
  { match: /saturn|saturne|helene|hélène|piscinas|tethys|titan/i, name: "Saturne", img: "https://cdn.warframestat.us/img/EmoteSaturn.png" },
  { match: /uranus|ophelia|assur|titania|brutus/i, name: "Uranus", img: "https://cdn.warframestat.us/img/EmoteUranus.png" },
  { match: /neptune|salacia|psamathe/i, name: "Neptune", img: "https://cdn.warframestat.us/img/EmoteNeptune.png" },
  { match: /pluto|pluton|hieracon/i, name: "Pluton", img: "https://cdn.warframestat.us/img/EmotePluto.png" },
  { match: /eris|candiru|lepis|naeglar|akkad/i, name: "Éris", img: "https://cdn.warframestat.us/img/EmoteEris.png" },
  { match: /mars|wahiba|war\b/i, name: "Mars", img: "https://cdn.warframestat.us/img/EmoteMars.png" },
  { match: /jupiter|io\b|cameria|themisto|sinai/i, name: "Jupiter", img: "https://cdn.warframestat.us/img/EmoteJupiter.png" },
  { match: /ceres|cérès|gabii|seimeni|exta|draco/i, name: "Cérès", img: "https://cdn.warframestat.us/img/EmoteCeres.png" },
  { match: /sedna|hydron/i, name: "Sedna", img: "https://cdn.warframestat.us/img/EmoteSedna.png" },
  { match: /phobos|zeugma|stickney/i, name: "Phobos", img: "https://cdn.warframestat.us/img/EmotePhobos.png" },
  { match: /europa|europe|valefor|naamah/i, name: "Europe", img: "https://cdn.warframestat.us/img/EmoteEuropa.png" },
  { match: /mercury|mercure|apollodorus|tolstoj/i, name: "Mercure", img: "https://cdn.warframestat.us/img/EmoteMercury.png" },
  { match: /kuva fortress|forteresse kuva|taveuni|siphon.*kuva|déluge.*kuva|kuva flood/i, name: "Forteresse Kuva", img: "https://cdn.warframestat.us/img/EmoteKuvaFortress.png" },
  { match: /void|néant|granum|ani\b|mot\b|hepit|ukko|teshub/i, name: "Le Néant (Void)", img: "https://cdn.warframestat.us/img/EmoteVoid.png" },
  { match: /railjack|proxima|skirmish/i, name: "Railjack Proxima", img: "https://cdn.warframestat.us/img/EmoteDeepSpace.png" }
];

const MOB_VISUAL_RULES = [
  // Reliques du Néant & Résurgence Prime
  { match: /\blith\s+[a-z0-9]+/i, name: "Relique Lith", kind: "⬡ Relique Lith", img: "https://cdn.warframestat.us/img/RelicLithD.png", planetImg: "https://cdn.warframestat.us/img/EmoteVoid.png" },
  { match: /\bmeso\s+[a-z0-9]+/i, name: "Relique Meso", kind: "⬡ Relique Meso", img: "https://cdn.warframestat.us/img/RelicMesoD.png", planetImg: "https://cdn.warframestat.us/img/EmoteVoid.png" },
  { match: /\bneo\s+[a-z0-9]+/i, name: "Relique Neo", kind: "⬡ Relique Neo", img: "https://cdn.warframestat.us/img/RelicNeoD.png", planetImg: "https://cdn.warframestat.us/img/EmoteVoid.png" },
  { match: /\baxi\s+[a-z0-9]+/i, name: "Relique Axi", kind: "⬡ Relique Axi", img: "https://cdn.warframestat.us/img/RelicAxiD.png", planetImg: "https://cdn.warframestat.us/img/EmoteVoid.png" },
  { match: /\brequiem\b/i, name: "Relique Requiem", kind: "⬡ Relique Requiem", img: "https://cdn.warframestat.us/img/RelicImmortalA.png", planetImg: "https://cdn.warframestat.us/img/EmoteKuvaFortress.png" },
  { match: /varzia|résurgence prime|soute prime|vaultée|\baya\b/i, name: "Varzia (Résurgence Prime)", kind: "❖ Résurgence Prime", img: "https://cdn.warframestat.us/img/Aya.png", planetImg: "https://cdn.warframestat.us/img/EmoteMars.png" },
  { match: /reliques du néant/i, name: "Reliques du Néant", kind: "⬡ Reliques Prime", img: "https://cdn.warframestat.us/img/RelicAxiD.png", planetImg: "https://cdn.warframestat.us/img/EmoteVoid.png" },

  // Syndicats, Marchands & Modes Spéciaux
  { match: /new loka|nouveau loka/i, name: "Nouveau Loka", kind: "❖ Syndicat", img: "https://cdn.warframestat.us/img/NewLokaAvatar.png", planetImg: "data/planets/earth.png" },
  { match: /perrin sequence|séquence perrin|ergo glast/i, name: "Séquence Perrin (Ergo Glast)", kind: "❖ Syndicat", img: "https://cdn.warframestat.us/img/PerrinSequenceAvatar.png", planetImg: "https://cdn.warframestat.us/img/EmoteNeptune.png" },
  { match: /steel meridian|méridien d'acier/i, name: "Méridien d'Acier", kind: "❖ Syndicat", img: "https://cdn.warframestat.us/img/SteelMeridianAvatar.png", planetImg: "data/planets/earth.png" },
  { match: /arbiters of hexis|arbitres de hexis|arbitration/i, name: "Arbitres de Hexis / Arbitrage", kind: "❖ Syndicat & Arbitrage", img: "https://cdn.warframestat.us/img/ArbitersHexisAvatar.png" },
  { match: /cephalon suda|céphalon suda/i, name: "Céphalon Suda", kind: "❖ Syndicat", img: "https://cdn.warframestat.us/img/CephalonSudaAvatar.png" },
  { match: /red veil|voile rouge/i, name: "Voile Rouge", kind: "❖ Syndicat", img: "https://cdn.warframestat.us/img/RedVeilAvatar.png" },
  { match: /simaris|sanctuary onslaught|assaut du sanctuaire/i, name: "Céphalon Simaris", kind: "❖ Sanctuaire Simaris", img: "https://cdn.warframestat.us/img/CephalonSimarisAvatar.png" },
  { match: /baro ki'teer|marchand du néant/i, name: "Baro Ki'Teer", kind: "◈ Marchand du Néant", img: "https://cdn.warframestat.us/img/BobbleheadBaroKiTeer.png", planetImg: "https://cdn.warframestat.us/img/EmoteVoid.png" },
  { match: /nora night|ondes nocturnes|nightwave/i, name: "Nora Night (Ondes Nocturnes)", kind: "❖ Ondes Nocturnes", img: "https://cdn.warframestat.us/img/BobbleheadNoraNight.png" },
  { match: /teshin|conclave|route de l'acier/i, name: "Teshin (Conclave / Acier)", kind: "⚔ Teshin", img: "https://cdn.warframestat.us/img/BobbleheadTeshin.png" },
  { match: /cavalero|irréductibles|holdfasts/i, name: "Cavalero (Zariman)", kind: "❖ Syndicat Zariman", img: "data/planets/zariman.png" },
  { match: /kahl|chipper/i, name: "Garnison de Kahl", kind: "❖ Camp du Voyageur", img: "https://cdn.warframestat.us/img/GrineerAtricula.png", planetImg: "data/planets/earth.png" },
  { match: /nightmare mode|mode cauchemar/i, name: "Mission Mode Cauchemar", kind: "⚔ Mode Cauchemar", img: "https://cdn.warframestat.us/img/SkullBadgeBronze.png" },
  { match: /salles orokin|clés de dragon|dragon key|corrupted vault|derelict vault/i, name: "Salles Orokin (Clés de Dragon)", kind: "⬡ Coffre Orokin Corrompu", img: "https://cdn.warframestat.us/img/FactionOrokin.png", planetImg: "data/planets/deimos.png" },
  { match: /liche kuva|kuva lich|larvling/i, name: "Liche Kuva", kind: "⚔ Némésis Kuva", img: "https://cdn.warframestat.us/img/FactionKuva.png", planetImg: "https://cdn.warframestat.us/img/EmoteKuvaFortress.png" },
  { match: /sœur de parvos|sister of parvos|hound/i, name: "Sœur de Parvos", kind: "⚔ Némésis Corpus", img: "https://cdn.warframestat.us/img/CorpusArticula.png", planetImg: "https://cdn.warframestat.us/img/EmoteNeptune.png" },
  { match: /technocyte coda|eleanor|lettie|arthur|amir|aoi|quincy/i, name: "L'Hexagone / Technocyte Coda", kind: "⚔ Syndicat & Boss 1999", img: "https://cdn.warframestat.us/img/FactionTechrot.png", planetImg: "https://cdn.warframestat.us/img/EmoteLasria.png" },
  { match: /dojo de clan|laboratoire|marché en jeu|recherche de clan/i, name: "Dojo de Clan / Marché", kind: "❖ Dojo & Marché", img: "https://cdn.warframestat.us/img/ClanEmblemHolo.png" },

  // Bosses, Mobs & Faune
  { match: /narmer thumper/i, name: "Narmer Thumper", kind: "⚔ Boss / Mob", img: "https://cdn.warframestat.us/img/PlushyThumperMediumDirty.png", planetImg: "data/planets/earth.png" },
  { match: /tusk thumper doma/i, name: "Tusk Thumper Doma", kind: "⚔ Boss / Mob", img: "https://cdn.warframestat.us/img/PlushyThumperLarge.png", planetImg: "data/planets/earth.png" },
  { match: /tusk thumper/i, name: "Tusk Thumper Bull", kind: "⚔ Boss / Mob", img: "https://cdn.warframestat.us/img/PlushyThumperMedium.png", planetImg: "data/planets/earth.png" },
  { match: /profit-taker|preneur de profit/i, name: "Profit-Taker Orb", kind: "⚔ Boss Orbe", img: "https://cdn.warframestat.us/img/ArachnoidCamperAF.png", planetImg: "data/planets/venus.png" },
  { match: /exploiter orb|orbe exploiteur/i, name: "Exploiter Orb", kind: "⚔ Boss Orbe", img: "https://cdn.warframestat.us/img/ArachnoidCamperTerraAF.png", planetImg: "data/planets/venus.png" },
  { match: /raknoid/i, name: "Raknoid (Scyto / Kyta / Mite)", kind: "⚔ Mob Corpus", img: "https://cdn.warframestat.us/img/CrpArachnoidPowerCoreHunger.png", planetImg: "data/planets/venus.png" },
  { match: /hydrolyst/i, name: "Eidolon Hydrolyst", kind: "⚔ Boss Eidolon", img: "https://cdn.warframestat.us/img/TeralystRainAF.png", planetImg: "data/planets/earth.png" },
  { match: /gantulyst/i, name: "Eidolon Gantulyst", kind: "⚔ Boss Eidolon", img: "https://cdn.warframestat.us/img/TeralystBigAF.png", planetImg: "data/planets/earth.png" },
  { match: /vomvalyst|teralyst|eidolon/i, name: "Eidolon (Teralyst / Vomvalyst)", kind: "⚔ Mob / Boss Eidolon", img: "https://cdn.warframestat.us/img/TeralystAF.png", planetImg: "data/planets/earth.png" },
  { match: /orowyrm/i, name: "Orowyrm", kind: "⚔ Boss Duviri", img: "https://cdn.warframestat.us/img/DuviriDragonDisplayIcon.png", planetImg: "https://cdn.warframestat.us/img/EmoteDuviri.png" },
  { match: /thrax|circulus|yuvarium/i, name: "Thrax (Centurion / Legatus)", kind: "⚔ Mob Thrax", img: "https://cdn.warframestat.us/img/Xmas23Thrax.png", planetImg: "https://cdn.warframestat.us/img/EmoteLua.png" },
  { match: /void angel|ange du néant/i, name: "Ange du Néant (Void Angel)", kind: "⚔ Boss Zariman", img: "https://cdn.warframestat.us/img/VoidAngelGlyph.png", planetImg: "data/planets/zariman.png" },
  { match: /\bdax\b/i, name: "Dax (Equitem / Gladius / Arcus)", kind: "⚔ Mob Dax", img: "https://cdn.warframestat.us/img/UmbraDaxPoster.png", planetImg: "https://cdn.warframestat.us/img/EmoteDuviri.png" },
  { match: /battalyst|hunhullus|dactolyst|vanguard|sentient|mimic|brachiolyst|symbilyst|aerolyst/i, name: "Sentient / Battalyst", kind: "⚔ Mob Sentient", img: "https://cdn.warframestat.us/img/BobbleheadSentientWarrior.png" },
  { match: /conculyst/i, name: "Conculyst Sentient", kind: "⚔ Mob Sentient", img: "https://cdn.warframestat.us/img/BobbleheadSentientMeleeWarrior.png" },
  { match: /juggernaut|membroid|proto-infested|lephantis|jordas|boiler|charger|runner|leaper|brood mother|ancient|mutalist|crawler|infested|carnis|jugulus|saxum|deimos/i, name: "Mob / Boss Infesté", kind: "⚔ Mob Infesté", img: "https://cdn.warframestat.us/img/InfTacAlertPussAncient.png", planetImg: "data/planets/deimos.png" },
  { match: /ambulas/i, name: "Ambulas", kind: "⚔ Boss Corpus", img: "https://cdn.warframestat.us/img/BobbleheadAmbulas.png", planetImg: "https://cdn.warframestat.us/img/EmotePluto.png" },
  { match: /jackal/i, name: "Jackal", kind: "⚔ Boss Corpus", img: "https://cdn.warframestat.us/img/BobbleheadJackal.png", planetImg: "data/planets/venus.png" },
  { match: /\bvor\b/i, name: "Corrupted Vor / Captain Vor", kind: "⚔ Boss", img: "https://cdn.warframestat.us/img/BobbleheadVor.png", planetImg: "https://cdn.warframestat.us/img/EmoteVoid.png" },
  { match: /sargas ruk/i, name: "Général Sargas Ruk", kind: "⚔ Boss Grineer", img: "https://cdn.warframestat.us/img/BobbleheadSargusRuk.png", planetImg: "https://cdn.warframestat.us/img/EmoteSaturn.png" },
  { match: /tyl regor/i, name: "Tyl Regor", kind: "⚔ Boss Grineer", img: "https://cdn.warframestat.us/img/BobbleheadTylRegor.png", planetImg: "https://cdn.warframestat.us/img/EmoteUranus.png" },
  { match: /alad v/i, name: "Alad V", kind: "⚔ Boss Corpus", img: "https://cdn.warframestat.us/img/BobbleheadAladV.png", planetImg: "https://cdn.warframestat.us/img/EmoteJupiter.png" },
  { match: /ropalolyst/i, name: "Ropalolyst", kind: "⚔ Boss Sentient", img: "https://cdn.warframestat.us/img/RopalolystAF.png", planetImg: "https://cdn.warframestat.us/img/EmoteJupiter.png" },
  { match: /angst|acolyte|violence|malice|misery|torment|stalker/i, name: "Stalker / Acolyte", kind: "⚔ Boss Acolyte", img: "https://cdn.warframestat.us/img/BobbleheadAcolyteStriker.png" },
  { match: /emperor condroc/i, name: "Emperor Condroc", kind: "⚔ Faune Cetus", img: "https://cdn.warframestat.us/img/PlushyCondrocRare.png", planetImg: "data/planets/earth.png" },
  { match: /condroc/i, name: "Condroc (Plaines d'Eidolon)", kind: "⚔ Faune Cetus", img: "https://cdn.warframestat.us/img/PlushyCondrocCommon.png", planetImg: "data/planets/earth.png" },
  { match: /ghost kuaka/i, name: "Ghost Kuaka", kind: "⚔ Faune Cetus", img: "https://cdn.warframestat.us/img/PlushyKuakaRare.png", planetImg: "data/planets/earth.png" },
  { match: /kuaka/i, name: "Kuaka (Plaines d'Eidolon)", kind: "⚔ Faune Cetus", img: "https://cdn.warframestat.us/img/PlushyKuakaUncommon.png", planetImg: "data/planets/earth.png" },
  { match: /mergoo/i, name: "Mergoo (Plaines d'Eidolon)", kind: "⚔ Faune Cetus", img: "https://cdn.warframestat.us/img/PlushyMergooCommon.png", planetImg: "data/planets/earth.png" },
  { match: /kullervo/i, name: "Kullervo (Duviri)", kind: "⚔ Boss Duviri", img: "https://cdn.warframestat.us/img/BobbleKullervo.png", planetImg: "https://cdn.warframestat.us/img/EmoteDuviri.png" },
  { match: /bonewidow/i, name: "Bonewidow Necramech", kind: "⚔ Necramech", img: "https://cdn.warframestat.us/img/ThanoMech.png", planetImg: "data/planets/deimos.png" },
  { match: /voidrig|necramech|isolation vault/i, name: "Voidrig Necramech", kind: "⚔ Necramech", img: "https://cdn.warframestat.us/img/NechroMech.png", planetImg: "data/planets/deimos.png" },
  { match: /scaldra/i, name: "Scaldra (1999)", kind: "⚔ Faction 1999", img: "https://cdn.warframestat.us/img/FactionScaldra.png", planetImg: "https://cdn.warframestat.us/img/EmoteLasria.png" },
  { match: /techrot|h-09 apex|antivirus/i, name: "Techrot (1999)", kind: "⚔ Mob 1999", img: "https://cdn.warframestat.us/img/FactionTechrot.png", planetImg: "https://cdn.warframestat.us/img/EmoteLasria.png" },
  { match: /murmur|netracell|entratilab|albrecht|culverin|arcocanid|anatomizer|gruzzling|fragmented/i, name: "La Murmure (Laboratoires Entrati)", kind: "⚔ Mob Murmure", img: "https://cdn.warframestat.us/img/FactionMurmur.png", planetImg: "data/planets/deimos.png" },
  { match: /\bmother\b/i, name: "Mother (Entrati)", kind: "❖ Syndicat Deimos", img: "https://cdn.warframestat.us/img/Xmas20Mother.png", planetImg: "data/planets/deimos.png" },
  { match: /\bfather\b/i, name: "Father (Entrati)", kind: "❖ Syndicat Deimos", img: "https://cdn.warframestat.us/img/Xmas20Father.png", planetImg: "data/planets/deimos.png" },
  { match: /\bdaughter\b/i, name: "Daughter (Entrati)", kind: "❖ Syndicat Deimos", img: "https://cdn.warframestat.us/img/Xmas20Daughter.png", planetImg: "data/planets/deimos.png" },
  { match: /grandmother/i, name: "Grandmother (Entrati)", kind: "❖ Syndicat Deimos", img: "https://cdn.warframestat.us/img/Xmas20GMother.png", planetImg: "data/planets/deimos.png" },
  { match: /otak|necraloid|\bloid\b|entrati \(son\)|\bson\b/i, name: "Otak / Loid / Son (Necralisk)", kind: "❖ Syndicat Deimos", img: "https://cdn.warframestat.us/img/TwitchNecraloidGlyph.png", planetImg: "data/planets/deimos.png" },
  { match: /kosma|gyre|gyrix|lech kril|grineer|grokdrul|iradite|butcher|seeker|lancer|trooper|bombard|gunner|nox|manic|bailiff|ghoul|drekar|tusk|kuva|executioner|hellion|ballista|eviscerator|napalm|commander|scorch|dargyn|drahk|hyekka|kela|vay hek/i, name: "Unité / Boss Grineer", kind: "⚔ Mob Grineer", img: "https://cdn.warframestat.us/img/GrineerAtricula.png" },
  { match: /oxium|ramsled|spaceport|temple of profit|vox solaris|solaris|smokefinger|raptor|hyena|corpus|crewman|moa|osprey|nullifier|bursa|comba|scrambus|terra|vapos|juno|aurax|orm|machinist|amalgam|sniper|prod|detron|ranger|zanuka|demolisher|treasurer/i, name: "Unité / Boss Corpus", kind: "⚔ Mob Corpus", img: "https://cdn.warframestat.us/img/CorpusArticula.png" },
  { match: /orokin|caches|suumbaat|ostron|quills|operational supply|corrupted|spy|espionnage/i, name: "Orokin / Caches / Ostron", kind: "⬡ Orokin / Syndicat", img: "https://cdn.warframestat.us/img/FactionOrokin.png" }
];

function resolvePrimeRewardIcon(rawText) {
  if (!rawText) return null;
  if (/\bforma\b/i.test(rawText)) {
    return { src: "https://cdn.warframestat.us/img/GenericComponent.png", title: "Forma Blueprint" };
  }
  const allItems = [...(WF_DATA.codex?.warframes || []), ...(WF_DATA.codex?.weapons || [])];
  const low = rawText.toLowerCase();
  for (const it of allItems) {
    const n = (it.name || "").toLowerCase();
    if (n && n.includes("prime") && low.includes(n) && it.image) {
      return { src: `https://cdn.warframestat.us/img/${it.image}`, title: it.name };
    }
  }
  return null;
}

function resolveSourceVisuals(rawText, itemName = "") {
  const combined = `${rawText || ""} ${itemName || ""}`;
  let planet = null;
  let mob = null;

  // Si c'est une récompense Prime de Relique (ex: "Alternox Prime Blueprint — 2% ➔ 10%"), trouve l'image de l'arme/Warframe Prime !
  const primeRewardIcon = currentTab === "relics" ? resolvePrimeRewardIcon(rawText) : null;

  for (const p of PLANET_VISUAL_RULES) {
    if (p.match.test(rawText) || (!planet && p.match.test(combined))) {
      planet = p;
      if (p.match.test(rawText)) break;
    }
  }
  for (const m of MOB_VISUAL_RULES) {
    if (m.match.test(rawText) || (!mob && m.match.test(itemName))) {
      mob = m;
      if (m.match.test(rawText)) break;
    }
  }

  const icons = [];
  if (primeRewardIcon) {
    icons.push(primeRewardIcon);
  }
  if (mob && !icons.some((ic) => ic.src === mob.img)) {
    icons.push({ src: mob.img, title: mob.name });
  }
  if (planet) {
    if (!icons.some((ic) => ic.src === planet.img) && icons.length < 2) {
      icons.push({ src: planet.img, title: planet.name });
    }
  } else if (mob && mob.planetImg && !icons.some((ic) => ic.src === mob.planetImg) && icons.length < 2) {
    icons.push({ src: mob.planetImg, title: "Planète" });
  }

  if (!icons.length) {
    icons.push({ src: "https://cdn.warframestat.us/img/EmoteVoid.png", title: "Système Origine" });
  }

  let badge = "◎ Planète & Mission";
  if (primeRewardIcon) {
    badge = `✦ Récompense Prime (${primeRewardIcon.title})`;
  } else if (mob && planet) {
    badge = `${mob.kind} • ◎ ${planet.name}`;
  } else if (mob) {
    badge = `${mob.kind} (${mob.name})`;
  } else if (planet) {
    badge = `◎ Planète : ${planet.name}`;
  }

  if (/mining|filon|lésion|vein|lesion/i.test(rawText)) {
    badge = `⬡ Minage • ${planet ? planet.name : "Monde Ouvert"}`;
  } else if (/bounty|mise à prix|rotation/i.test(rawText) && planet) {
    badge = `⌖ Mission / Rotation • ◎ ${planet.name}`;
  }

  return { icons, badge, planet, mob };
}

function parseDropEntry(rawLine, itemName = "") {
  const line = (rawLine || "").trim();

  // Cas 1 : Récompense de Relique du type "... — 2% (Intacte) ➔ 10% (Éclatante)"
  const relicMatch = line.match(/—\s*(\d+(?:\.\d+)?)%\s*\(Intacte\)\s*➔\s*(\d+(?:\.\d+)?)%\s*\(Éclatante\)/i);
  if (relicMatch) {
    const pIntact = parseFloat(relicMatch[1]);
    const pRad = parseFloat(relicMatch[2]);
    const cleanTitle = line
      .replace(relicMatch[0], "")
      .replace(/^[✦◈●]\s*(\[[^\]]+\]\s*)+/g, "")
      .trim();

    let color = "#4ADE80";
    let bg = "rgba(74, 222, 128, 0.16)";
    let border = "rgba(74, 222, 128, 0.55)";
    let rarityLabel = "● Commun (Bronze)";

    if (line.includes("Rare") || pIntact <= 5) {
      color = "#FBBF24";
      bg = "rgba(245, 158, 11, 0.2)";
      border = "rgba(251, 191, 36, 0.7)";
      rarityLabel = "✦ Rare (Or)";
    } else if (line.includes("Inhabituel") || pIntact <= 15) {
      color = "#38BDF8";
      bg = "rgba(56, 189, 248, 0.18)";
      border = "rgba(56, 189, 248, 0.6)";
      rarityLabel = "◈ Inhabituel (Argent)";
    }

    const vis = resolveSourceVisuals(cleanTitle, itemName);
    return {
      title: cleanTitle,
      pct: pRad,
      pctText: `${pIntact}% ➔ ${pRad}%`,
      barWidth: Math.max(12, Math.min(100, pRad * 3.5)),
      color,
      bg,
      border,
      rarityLabel,
      icons: vis.icons,
      badge: vis.badge
    };
  }

  // Cas 2 : Pourcentage standard du type (33.36% Rare) ou (100% Common) ou (14.29%)
  const pctMatch =
    line.match(/\(\s*(\d+(?:\.\d+)?)%\s*([A-Za-zÀ-ÿ\s]*)\)/) ||
    line.match(/(\d+(?:\.\d+)?)%\s*(Common|Uncommon|Rare|Legendary|Commun|Inhabituel|Légendaire)?/i);

  let pct = null;
  let rarityRaw = "";
  let cleanTitle = line;

  if (pctMatch) {
    pct = parseFloat(pctMatch[1]);
    if (pct > 100) pct = +(pct / 100).toFixed(2);
    rarityRaw = (pctMatch[2] || "").trim();
    cleanTitle = line.replace(pctMatch[0], "").replace(/\(\s*\)/g, "").trim();
  }

  let color = "#4ADE80";
  let bg = "rgba(74, 222, 128, 0.16)";
  let border = "rgba(74, 222, 128, 0.55)";
  let rarityLabel = currentLang === "fr" ? "● Commun" : "● Common";

  const rLow = rarityRaw.toLowerCase();
  if (rLow.includes("rare") || rLow.includes("legend") || (pct !== null && pct < 10)) {
    color = "#FBBF24";
    bg = "rgba(245, 158, 11, 0.18)";
    border = "rgba(251, 191, 36, 0.65)";
    rarityLabel = currentLang === "fr" ? "✦ Rare" : "✦ Rare";
  } else if (rLow.includes("uncommon") || rLow.includes("inhabituel") || (pct !== null && pct < 35)) {
    color = "#38BDF8";
    bg = "rgba(56, 189, 248, 0.16)";
    border = "rgba(56, 189, 248, 0.55)";
    rarityLabel = currentLang === "fr" ? "◆ Inhabituel" : "◆ Uncommon";
  } else {
    rarityLabel = currentLang === "fr" ? "● Commun / Garanti" : "● Common / Guaranteed";
  }

  const vis = resolveSourceVisuals(cleanTitle || line, itemName);

  return {
    title: cleanTitle || line,
    pct,
    pctText: pct !== null ? `${pct % 1 === 0 ? pct.toFixed(0) : pct.toFixed(2)}%` : (currentLang === "fr" ? "100%" : "100%"),
    barWidth: pct !== null ? Math.max(8, Math.min(100, pct)) : 100,
    color,
    bg,
    border,
    rarityLabel,
    icons: vis.icons,
    badge: vis.badge
  };
}

function openCodexModal(indexInFiltered) {
  const list = window._currentCodexFiltered || [];
  const item = list[indexInFiltered];
  if (!item) return;

  const modal = document.getElementById("codex-modal");
  const body = document.getElementById("codex-modal-body");
  if (!modal || !body) return;

  const imgUrl = item.image
    ? `https://cdn.warframestat.us/img/${item.image}`
    : "data/app_logo.png";

  let rawLoc = item.location || "Système Origine";
  const rawDropCleaned = cleanDropText(item.drop || "");
  if (rawLoc.includes("Système Origine") && /Location:\s*([^.|]+)/i.test(rawDropCleaned)) {
    const m = rawDropCleaned.match(/Location:\s*([^.|]+)/i);
    if (m && m[1]) rawLoc = m[1].trim();
  }

  const locParts = rawLoc.split("•").map((s) => s.trim()).filter(Boolean);
  const dropParts = rawDropCleaned.split("|").map((s) => s.trim()).filter(Boolean);

  // Collecte toutes les icônes uniques de Planètes, Reliques & Mobs pour l'en-tête
  const headerVisuals = [];
  [...locParts, ...dropParts].forEach((part) => {
    const v = resolveSourceVisuals(part, item.name);
    v.icons.forEach((ic) => {
      if (!headerVisuals.some((h) => h.src === ic.src) && headerVisuals.length < 6) {
        headerVisuals.push(ic);
      }
    });
  });

  // Cartes visuelles "Où trouver" (affiche aussi un badge % si présent dans la localisation, ex: Reliques)
  const locCardsHtml = locParts
    .map((locStr) => {
      const vis = resolveSourceVisuals(locStr, item.name);
      const pctInLoc = locStr.match(/\(\s*(\d+(?:\.\d+)?)%\s*\)/);
      const cleanLocTitle = pctInLoc ? locStr.replace(pctInLoc[0], "").trim() : locStr;
      return `
        <div class="modal-loc-card" style="justify-content:space-between;">
          <div style="display:flex; align-items:center; gap:11px; min-width:0; flex:1;">
            <div class="modal-source-icons">
              ${vis.icons
                .map(
                  (ic) => `
                <img src="${ic.src}" alt="${ic.title}" title="${ic.title}" class="modal-source-thumb" onerror="this.onerror=null;this.src='data/app_logo.png';" />
              `
                )
                .join("")}
            </div>
            <div style="min-width:0; flex:1;">
              <div style="font-size:11px; font-weight:800; color:var(--accent-cyan); margin-bottom:2px;">${vis.badge}</div>
              <div style="font-size:13px; font-weight:700; color:var(--text-main); line-height:1.3;">${cleanLocTitle}</div>
            </div>
          </div>
          ${
            pctInLoc
              ? `<span style="font-size:13.5px; font-weight:900; color:#38BDF8; background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.5); padding:3px 9px; border-radius:8px; flex-shrink:0;">${pctInLoc[1]}%</span>`
              : ""
          }
        </div>
      `;
    })
    .join("");

  // Lignes visuelles "Comment l'avoir / Récompenses & % de Drop"
  const dropRowsHtml = dropParts
    .map((dropStr) => {
      const parsed = parseDropEntry(dropStr, item.name);
      return `
        <div class="modal-drop-row">
          <div class="modal-drop-left">
            <div class="modal-source-icons">
              ${parsed.icons
                .map(
                  (ic) => `
                <img src="${ic.src}" alt="${ic.title}" title="${ic.title}" class="modal-source-thumb" onerror="this.onerror=null;this.src='data/app_logo.png';" />
              `
                )
                .join("")}
            </div>
            <div class="modal-drop-info">
              <div style="font-size:11px; font-weight:800; color:var(--accent-cyan); margin-bottom:2px;">${parsed.badge}</div>
              <div class="modal-drop-title">${parsed.title}</div>
              <div class="modal-drop-bar-bg">
                <div class="modal-drop-bar-fill" style="width:${parsed.barWidth}%; background:${parsed.color}; box-shadow: 0 0 8px ${parsed.color};"></div>
              </div>
            </div>
          </div>
          <div class="modal-drop-right">
            <span class="drop-pct-badge" style="color:${parsed.color}; background:${parsed.bg}; border:1.5px solid ${parsed.border};">
              ${parsed.pctText}
            </span>
            <span class="drop-rarity-tag" style="color:${parsed.color}; background:${parsed.bg};">
              ${parsed.rarityLabel}
            </span>
          </div>
        </div>
      `;
    })
    .join("");

  // Bloc optionnel de statistiques (Effet Max des Mods ou Statistiques de Combat des Armes)
  let statsBannerHtml = "";
  if (item.stats) {
    if (currentTab === "weapons") {
      const statChips = item.stats
        .split("|")
        .map((s) => s.trim())
        .filter((s) => s.startsWith("⚔") || s.startsWith("⌖") || s.startsWith("⟡") || s.startsWith("✦"));
      statsBannerHtml = `
        <div class="modal-sec-box" style="background:rgba(56,189,248,0.08); border-color:rgba(56,189,248,0.35);">
          <div class="modal-sec-label">⚔ Statistiques de Combat de l'Arme</div>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(170px, 1fr)); gap:8px;">
            ${statChips
              .map(
                (sc) => `
              <div style="background:rgba(10,15,26,0.55); border:1px solid var(--border-subtle); border-radius:8px; padding:8px 10px; font-size:13px; font-weight:800; color:var(--text-main);">
                ${sc}
              </div>
            `
              )
              .join("")}
          </div>
        </div>
      `;
    } else {
      statsBannerHtml = `
        <div class="modal-sec-box" style="background:rgba(251,191,36,0.08); border-color:rgba(251,191,36,0.4);">
          <div class="modal-sec-label" style="color:#FBBF24;">✦ Effet & Bonus du Mod (Rang Max)</div>
          <div style="font-size:14.5px; font-weight:800; color:var(--text-main); line-height:1.45;">
            ${item.stats}
          </div>
        </div>
      `;
    }
  }

  body.innerHTML = `
    <div class="modal-top">
      <img src="${imgUrl}" alt="${item.name}" class="modal-img" onerror="this.onerror=null;this.src='data/app_logo.png';" />
      <div style="flex:1; min-width:0;">
        <div style="display:flex; flex-wrap:wrap; align-items:center; gap:8px;">
          <span class="codex-grid-badge" style="font-size:12px; padding:3px 12px;">${item.category || "Codex"}</span>
          <span style="font-size:11.5px; font-weight:700; color:var(--accent-cyan); background:rgba(88,166,255,0.12); border:1px solid rgba(88,166,255,0.3); padding:2px 10px; border-radius:10px;">
            ⌖ ${locParts.length} ${currentLang === "fr" ? "Source(s) / Zone(s)" : "Source(s) / Zone(s)"}
          </span>
        </div>
        <div style="font-size:26px; font-weight:900; color:var(--text-main, #F0F6FC); margin-top:6px; letter-spacing:0.2px;">${item.name}</div>
        ${
          item.desc
            ? `<div style="font-size:12.5px; color:var(--text-muted); margin-top:4px; line-height:1.45;">${item.desc}</div>`
            : ""
        }
        <div style="display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-top:10px;">
          ${headerVisuals
            .map(
              (hv) => `
            <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(15,23,42,0.55); border:1px solid var(--border-subtle, #263554); padding:3px 10px 3px 5px; border-radius:20px;">
              <img src="${hv.src}" alt="${hv.title}" style="width:24px; height:24px; object-fit:contain;" onerror="this.onerror=null;this.src='data/app_logo.png';" />
              <span style="font-size:11.5px; font-weight:700; color:var(--text-main);">${hv.title}</span>
            </div>
          `
            )
            .join("")}
        </div>
      </div>
    </div>

    ${statsBannerHtml}

    <div class="modal-sec-box">
      <div class="modal-sec-label">${tr("lbl_location")} (Planètes, Boss, Reliques & Mobs Officiels)</div>
      <div class="modal-loc-grid">
        ${locCardsHtml}
      </div>
    </div>

    <div class="modal-sec-box" style="margin-bottom:18px;">
      <div class="modal-sec-label">${currentTab === "relics" ? tr("lbl_relic_rewards") : tr("lbl_drop_method")} (% de Drop & Rareté)</div>
      <div class="modal-drop-list">
        ${dropRowsHtml}
      </div>
    </div>

    <div style="display:flex; justify-content:flex-end;">
      <button class="btn-open" style="font-size:13.5px; padding:8px 24px; font-weight:800;" onclick="closeCodexModal()">
        ${currentLang === "fr" ? "Fermer" : "Close"}
      </button>
    </div>
  `;

  modal.classList.remove("hidden");
}

function closeCodexModal(event) {
  if (event && event.target && event.target.id !== "codex-modal") return;
  const modal = document.getElementById("codex-modal");
  if (modal) modal.classList.add("hidden");
}

window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeCodexModal();
});

function onCodexSearch(categoryKey, val) {
  codexState[categoryKey].query = val;
  const filtered = getFilteredCodexItems(categoryKey);
  window._currentCodexFiltered = filtered;
  resetAndRenderCodexGrid(filtered);
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
            <div class="planet-card hero-planet-card">
              <div class="planet-card-top">
                <img src="${c.img}" alt="${c.title}" class="planet-img hero-planet-img" />
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
            <div style="font-size:15px; font-weight:700; color:#58A6FF;">⌖ ${hub.hub}</div>
            <div style="font-size:12px; color:#8B949E;">⌖ ${hub.Syndicate || ""} — ${hub.highlights || ""}</div>
          </div>
        </div>
        ${rotKeys
          .map((rk, idx) => {
            const isActive = idx === bountyState.rotation_index;
            return `
              <div class="bounty-rot-row ${isActive ? "active" : ""}">
                <span style="color:${isActive ? "#4ADE80" : "#8B949E"};">
                  ${isActive ? "● " : "○ "}${rotLabels[idx]}${isActive ? " (ACTIVE)" : ""}
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
const INCARNON_WEAPON_IMAGES = {
  "Ack & Brunt": "AckAndBrunt.png",
  "Angstrum": "Angstrum.png",
  "Anku": "Anku.png",
  "Atomos": "Atomos.png",
  "Bo": "Bo.png",
  "Boar": "Boar.png",
  "Boltor": "Boltor.png",
  "Braton": "Braton.png",
  "Bronco": "Bronco.png",
  "Burston": "Burston.png",
  "Ceramic Dagger": "CeramicDagger.png",
  "Cestra": "Cestra.png",
  "Dera": "Dera.png",
  "Despair": "Despair.png",
  "Dread": "Dread.png",
  "Dual Ichor": "DualIchor.png",
  "Dual Toxocyst": "DualToxocyst.png",
  "Furax": "Furax.png",
  "Furis": "Furis.png",
  "Gammacor": "Gammacor.png",
  "Gorgon": "Gorgon.png",
  "Hate": "Hate.png",
  "Kunai": "Kunai.png",
  "Lato": "Lato.png",
  "Latron": "Latron.png",
  "Lex": "Lex.png",
  "Magistar": "Magistar.png",
  "Miter": "Miter.png",
  "Nami Solo": "NamiSolo.png",
  "Okina": "Okina.png",
  "Paris": "Paris.png",
  "Sibear": "Sibear.png",
  "Sicarus": "Sicarus.png",
  "Skana": "Skana.png",
  "Soma": "Soma.png",
  "Strun": "Strun.png",
  "Sybaris": "Sybaris.png",
  "Torid": "Torid.png",
  "Vasto": "Vasto.png",
  "Zylok": "ConclaveLeverPistol.png"
};

function getIncarnonWeaponImg(wName) {
  const map = (WF_DATA.duviri && WF_DATA.duviri.incarnon_images) || INCARNON_WEAPON_IMAGES;
  const file = map[wName] || INCARNON_WEAPON_IMAGES[wName] || `${wName.replace(/[^a-zA-Z0-9]/g, "")}.png`;
  return `https://cdn.warframestat.us/img/${file}`;
}

function getCircuitWarframeImg(wfName) {
  const found = (WF_DATA.codex?.warframes || []).find((w) => w.name.toLowerCase() === wfName.toLowerCase());
  const file = (found && found.image) || `${wfName.replace(/\s+/g, "")}.png`;
  return `https://cdn.warframestat.us/img/${file}`;
}

function renderDuviriView(container) {
  if (!duviriState) duviriState = computeDuviriState();

  const curIncWeek = duviriState.incarnon_index + 1;
  const curWfWeek = duviriState.warframe_index + 1;

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
      <div class="view-header-title" style="margin-bottom:0;">${tr("duviri_page_title")}</div>
      <div id="center-duviri-timer" style="font-size:13px; font-weight:700; color:#4ADE80;">
        ${tr("duviri_reset_prefix")} ${formatCountdown(getRemainingSeconds(duviriState.expiry), false)}
      </div>
    </div>

    <!-- VITRINE EN DIRECT DE LA SEMAINE ACTIVE (AVEC GRANDES IMAGES OFFICIELLES) -->
    <div class="cards-grid-2" style="margin-bottom:14px;">
      <div class="bounty-card" style="margin-bottom:0; border-color:#3B82F6; box-shadow:0 0 18px rgba(59,130,246,0.18);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:13.5px; font-weight:800; color:#79C0FF;">
            ✦ ${currentLang === "fr" ? "Armes Incarnon Actives" : "Active Incarnon Weapons"} (${tr("week_label")} ${curIncWeek})
          </span>
          <span style="font-size:11px; font-weight:700; color:#4ADE80;">● ${currentLang === "fr" ? "EN COURS" : "ACTIVE"}</span>
        </div>
        <div class="duviri-showcase-grid">
          ${duviriState.incarnon_current
            .map(
              (w) => `
            <div class="duviri-showcase-card">
              <img src="${getIncarnonWeaponImg(w)}" alt="${w}" class="duviri-showcase-img" loading="lazy" onerror="this.onerror=null;this.src='data/app_logo.png';" />
              <div class="duviri-showcase-name">${w}</div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>

      <div class="bounty-card" style="margin-bottom:0; border-color:#3B82F6; box-shadow:0 0 18px rgba(59,130,246,0.18);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:13.5px; font-weight:800; color:#79C0FF;">
            ❖ ${currentLang === "fr" ? "Warframes du Circuit Actives" : "Active Circuit Warframes"} (${tr("week_label")} ${curWfWeek})
          </span>
          <span style="font-size:11px; font-weight:700; color:#4ADE80;">● ${currentLang === "fr" ? "EN COURS" : "ACTIVE"}</span>
        </div>
        <div class="duviri-showcase-grid wf-grid">
          ${duviriState.warframes_current
            .map(
              (wf) => `
            <div class="duviri-showcase-card">
              <img src="${getCircuitWarframeImg(wf)}" alt="${wf}" class="duviri-showcase-img" loading="lazy" onerror="this.onerror=null;this.src='data/app_logo.png';" />
              <div class="duviri-showcase-name">${wf}</div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>
    </div>

    <!-- CALENDRIER COMPLET DES ROTATIONS AVEC IMAGES OFFICIELLES -->
    <div class="cards-grid-2">
      <div class="bounty-card">
        <div style="font-size:14px; font-weight:700; color:#58A6FF; margin-bottom:10px;">${tr("duviri_inc_col")}</div>
        ${duviriState.all_incarnon
          .map((weapons, idx) => {
            const isAct = idx === duviriState.incarnon_index;
            return `
              <div class="bounty-rot-row ${isAct ? "active" : ""}" style="grid-template-columns:130px 1fr; align-items:center; padding:8px 10px; margin:4px 0;">
                <span style="color:${isAct ? "#4ADE80" : "#8B949E"}; font-weight:${isAct ? "800" : "600"};">
                  ${tr("week_label")} ${idx + 1}${isAct ? tr("active_tag") : ""}
                </span>
                <div class="duviri-chips-wrap">
                  ${weapons
                    .map(
                      (w) => `
                    <span class="duviri-item-chip">
                      <img src="${getIncarnonWeaponImg(w)}" alt="${w}" class="duviri-chip-img" loading="lazy" onerror="this.onerror=null;this.src='data/app_logo.png';" />
                      <span>${w}</span>
                    </span>
                  `
                    )
                    .join("")}
                </div>
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
              <div class="bounty-rot-row ${isAct ? "active" : ""}" style="grid-template-columns:130px 1fr; align-items:center; padding:8px 10px; margin:4px 0;">
                <span style="color:${isAct ? "#4ADE80" : "#8B949E"}; font-weight:${isAct ? "800" : "600"};">
                  ${tr("week_label")} ${idx + 1}${isAct ? tr("active_tag") : ""}
                </span>
                <div class="duviri-chips-wrap">
                  ${wfs
                    .map(
                      (wf) => `
                    <span class="duviri-item-chip">
                      <img src="${getCircuitWarframeImg(wf)}" alt="${wf}" class="duviri-chip-img" loading="lazy" onerror="this.onerror=null;this.src='data/app_logo.png';" />
                      <span>${wf}</span>
                    </span>
                  `
                    )
                    .join("")}
                </div>
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
              <span style="font-weight:700; color:#F0F6FC;">▸ ${it.item}</span>
              <span style="color:#F59E0B; font-weight:700;">◆ ${it.ducats} Ducats   |   ○ ${(it.credits || 0).toLocaleString()} Crédits</span>
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
    "nav-welcome": currentLang === "fr" ? "Accueil" : "Home",
    "nav-settings": cleanNavText(tr("nav_settings")),
    "sec-inv": tr("sec_inventory"),
    "nav-resources": cleanNavText(tr("nav_resources")),
    "nav-mods": cleanNavText(tr("nav_mods")),
    "nav-warframes": cleanNavText(tr("nav_warframes")),
    "nav-weapons": cleanNavText(tr("nav_weapons")),
    "nav-relics": cleanNavText(tr("nav_relics")),
    "sec-cycles": tr("sec_cycles"),
    "nav-worlds": cleanNavText(tr("nav_worlds")),
    "nav-bounties": cleanNavText(tr("nav_bounties")),
    "nav-duviri": cleanNavText(tr("nav_duviri")),
    "nav-baro": cleanNavText(tr("nav_baro")),
    "btn-refresh": tr("btn_refresh"),
    "btn-check-update": pendingRemoteUpdate
      ? `⇣ ${tr("upd_install_btn")} (v${pendingRemoteUpdate.version})`
      : `${tr("btn_check_update")} (v${getEffectiveLocalVersion()})`,
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

  const lblLive = document.getElementById("lbl-toggle-live");
  if (lblLive) {
    lblLive.textContent =
      currentLang === "fr"
        ? showRightPanel
          ? "Cacher Direct"
          : "Afficher Direct"
        : showRightPanel
          ? "Hide Live"
          : "Show Live";
  }

  buildLiveWorldsGrid();
  buildLiveNewsList();
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
  buildLiveNewsList();
  updateLivePanel();
  renderCurrentTab();
  if (showLoader && loader) {
    setTimeout(() => loader.classList.add("hidden"), 350);
  }
}

function isNewerVersion(remoteVer, localVer) {
  const r = String(remoteVer || "1.0.35").replace(/^v/i, "").split(".").map((n) => parseInt(n, 10) || 0);
  const l = String(localVer || "1.0.35").replace(/^v/i, "").split(".").map((n) => parseInt(n, 10) || 0);
  for (let i = 0; i < Math.max(r.length, l.length); i++) {
    const rv = r[i] || 0;
    const lv = l[i] || 0;
    if (rv > lv) return true;
    if (rv < lv) return false;
  }
  return false;
}

function getEffectiveLocalVersion() {
  const bundledVer = WF_DATA.version?.version || "1.0.35";
  const cachedVer = localStorage.getItem("wf_live_version");
  if (cachedVer && isNewerVersion(cachedVer, bundledVer)) {
    WF_DATA.version = { ...(WF_DATA.version || {}), version: cachedVer };
    return cachedVer;
  }
  return bundledVer;
}

function applyLiveJsCode(jsText) {
  if (!jsText) return;
  try {
    // Extrait toutes les fonctions et constantes (de la Section 1 jusqu'avant DOMContentLoaded)
    const startMarker = "func" + "tion tr(";
    const endMarker = 'window.addEventListener("DOMContent' + 'Loaded"';
    const startIdx = jsText.indexOf(startMarker);
    const endIdx = jsText.indexOf(endMarker);
    if (startIdx === -1 || endIdx === -1) return;
    const bodyCode = jsText
      .slice(startIdx, endIdx)
      .replace(/^(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=/gm, "window.$1 =")
      .replace(/^async\s+function\s+([a-zA-Z0-9_$]+)\s*\(/gm, "window.$1 = async function $1(")
      .replace(/^function\s+([a-zA-Z0-9_$]+)\s*\(/gm, "window.$1 = function $1(");
    const runner = new Function(bodyCode);
    runner();
  } catch (e) {
    console.warn("Live JS hot-reload warning:", e);
  }
}

function restoreCachedLiveUpdate() {
  const bundledVer = WF_DATA.version?.version || "1.0.35";
  const cachedVer = localStorage.getItem("wf_live_version");
  const effectiveVer = getEffectiveLocalVersion();
  const cachedCss = localStorage.getItem("wf_live_css");
  const cachedJs = localStorage.getItem("wf_live_js");
  if (cachedVer && isNewerVersion(cachedVer, bundledVer)) {
    if (cachedCss) {
      let styleTag = document.getElementById("wf-live-css");
      if (!styleTag) {
        styleTag = document.createElement("style");
        styleTag.id = "wf-live-css";
        document.head.appendChild(styleTag);
      }
      styleTag.textContent = cachedCss;
    }
    if (cachedJs) {
      applyLiveJsCode(cachedJs);
    }
  } else {
    localStorage.removeItem("wf_live_css");
    localStorage.removeItem("wf_live_js");
  }
  const btnUpd = document.getElementById("btn-check-update");
  if (btnUpd) {
    btnUpd.textContent = `⇣ ${tr("btn_check_update")} (v${effectiveVer})`;
  }
}

async function applyLiveUpdateZeroDownload(remote) {
  const baseUrl = "https://raw.githubusercontent.com/Nyxo-17/WireFrame/main/";
  const ts = "?t=" + Date.now();
  try {
    const [cssRes, jsRes, trRes, duvRes, codexRes] = await Promise.allSettled([
      fetch(baseUrl + "css/style.css" + ts, { cache: "no-store" }),
      fetch(baseUrl + "js/app.js" + ts, { cache: "no-store" }),
      fetch(baseUrl + "data/translations.json" + ts, { cache: "no-store" }),
      fetch(baseUrl + "data/duviri_rotations.json" + ts, { cache: "no-store" }),
      fetch(baseUrl + "data/codex_data.json" + ts, { cache: "no-store" })
    ]);

    if (cssRes.status === "fulfilled" && cssRes.value.ok) {
      const cssText = await cssRes.value.text();
      let styleTag = document.getElementById("wf-live-css");
      if (!styleTag) {
        styleTag = document.createElement("style");
        styleTag.id = "wf-live-css";
        document.head.appendChild(styleTag);
      }
      styleTag.textContent = cssText;
      try {
        localStorage.setItem("wf_live_css", cssText);
      } catch (e) {}
    }

    if (jsRes.status === "fulfilled" && jsRes.value.ok) {
      const jsText = await jsRes.value.text();
      applyLiveJsCode(jsText);
      try {
        localStorage.setItem("wf_live_js", jsText);
      } catch (e) {}
    }

    if (trRes.status === "fulfilled" && trRes.value.ok) {
      WF_DATA.translations = await trRes.value.json();
    }
    if (duvRes.status === "fulfilled" && duvRes.value.ok) {
      WF_DATA.duviri = await duvRes.value.json();
    }
    if (codexRes.status === "fulfilled" && codexRes.value.ok) {
      WF_DATA.codex = await codexRes.value.json();
    }

    WF_DATA.version = remote;
    localStorage.setItem("wf_live_version", remote.version);

    const btnUpd = document.getElementById("btn-check-update");
    if (btnUpd) {
      btnUpd.textContent = `⇣ ${tr("btn_check_update")} (v${remote.version})`;
      btnUpd.style.borderColor = "";
      btnUpd.style.color = "";
      btnUpd.onclick = () => checkForUpdatesManual(false);
    }

    setTheme(currentTheme);
    setLanguage(currentLang);
    renderCurrentTab();

    triggerAlert(
      `✦ Mise à jour v${remote.version} installée en direct`,
      remote.changelog_fr || "Mise à jour appliquée instantanément sans aucun fichier à télécharger !"
    );
  } catch (err) {
    console.warn("Live update sync error:", err);
  }
}

let pendingRemoteUpdate = null;
let lastPromptedVersion = null;

async function installPendingUpdate() {
  if (!pendingRemoteUpdate) return;
  const target = pendingRemoteUpdate;
  pendingRemoteUpdate = null;
  await applyLiveUpdateZeroDownload(target);
}

function dismissUpdatePrompt() {
  const banner = document.getElementById("toast-banner");
  if (banner) banner.classList.add("hidden");
}

function promptUpdateProposal(remote) {
  pendingRemoteUpdate = remote;
  lastPromptedVersion = remote.version;

  const btnUpd = document.getElementById("btn-check-update");
  if (btnUpd) {
    btnUpd.textContent = `⇣ ${tr("upd_install_btn")} (v${remote.version})`;
    btnUpd.style.borderColor = "#4ADE80";
    btnUpd.style.color = "#4ADE80";
    btnUpd.onclick = () => installPendingUpdate();
  }

  triggerAlert(
    `${tr("upd_available_title")} : v${remote.version}`,
    remote.changelog_fr || "Une nouvelle version est disponible !"
  );

  const banner = document.getElementById("toast-banner");
  const tMsg = document.getElementById("toast-msg");
  if (tMsg) {
    const laterTxt = currentLang === "fr" ? "Plus tard" : "Later";
    tMsg.innerHTML = `
      <div style="margin-bottom:8px;">${remote.changelog_fr || "Une nouvelle version est prête à être installée !"}</div>
      <div style="display:flex; gap:8px; align-items:center;">
        <button onclick="installPendingUpdate()" class="btn-open" style="cursor:pointer; background:#15803D; border-color:#4ADE80; color:#FFFFFF; padding:6px 14px;">
          ⇣ ${tr("upd_install_btn")} (v${remote.version})
        </button>
        <button onclick="dismissUpdatePrompt()" class="btn-open" style="cursor:pointer; padding:6px 12px;">
          ✕ ${laterTxt}
        </button>
      </div>
    `;
  }
  if (banner) {
    clearTimeout(window._toastTimeout);
    window._toastTimeout = setTimeout(() => banner.classList.add("hidden"), 20000);
  }
}

async function checkForUpdatesManual(isSilentAuto = false) {
  const localVer = getEffectiveLocalVersion();
  try {
    const res = await fetch("https://raw.githubusercontent.com/Nyxo-17/WireFrame/main/version.json?t=" + Date.now(), {
      cache: "no-store"
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const remote = await res.json();
    if (remote.version && isNewerVersion(remote.version, localVer)) {
      if (!isSilentAuto || lastPromptedVersion !== remote.version) {
        promptUpdateProposal(remote);
      }
    } else if (!isSilentAuto) {
      triggerAlert("WireFrame — Mise à jour", `${tr("upd_up_to_date")} (v${localVer}).`);
    }
  } catch (e) {
    if (!isSilentAuto) {
      triggerAlert("WireFrame — Mise à jour", `${tr("upd_up_to_date")} (v${localVer}).`);
    }
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
  setTheme(currentTheme);
  setFps(currentFps);
  toggleRightPanel(showRightPanel);
  worldState = computeOfflineWorldState();
  restoreCachedLiveUpdate();
  setLanguage(currentLang);

  if (bar) bar.style.width = "45%";
  if (status) status.textContent = "Chargement du Codex (1 442 Mods, 239 Ressources, 120 Warframes)...";

  setTimeout(async () => {
    if (bar) bar.style.width = "85%";
    if (status) status.textContent = "Synchronisation avec les serveurs Warframe...";
    worldState = await fetchLiveWarframeAPI();
    buildLiveWorldsGrid();
    buildLiveNewsList();
    updateLivePanel();
    renderCurrentTab();

    if (bar) bar.style.width = "100%";
    if (status) status.textContent = "Prêt ! Bienvenue Tenno.";

    setTimeout(() => {
      if (splash) splash.classList.add("hidden");
      checkForUpdatesManual(true);
    }, 320);
  }, 450);

  // Boucle temps réel 1 seconde + rafraîchissement API toutes les 60 secondes + détection de MAJ (avec proposition) toutes les 5 min
  setInterval(updateLivePanel, 1000);
  setInterval(() => refreshAllData(false), 60000);
  setInterval(() => checkForUpdatesManual(true), 300000);
});

