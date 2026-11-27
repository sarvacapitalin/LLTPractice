// js/ad-manager.js - Visibility-aware, Zero-CLS Google AdSense & Preview Manager
import { ADSENSE_CONFIG } from "./ad-config.js";

const PREVIEW_STORAGE_KEY = "TS_LLR_AD_PREVIEW";
const SCRIPT_ID = "google-adsense-script";

class AdManager {
  constructor() {
    this.scriptInjected = false;
    this.observer = null;
    this.previewEnabled = this._detectPreviewMode();
  }

  _detectPreviewMode() {
    if (typeof window === "undefined") return false;
    try {
      const params = new URLSearchParams(window.location.search);
      const param = params.get("adpreview");
      if (param === "1" || param === "true") {
        sessionStorage.setItem(PREVIEW_STORAGE_KEY, "1");
        return true;
      }
      if (param === "0" || param === "false") {
        sessionStorage.removeItem(PREVIEW_STORAGE_KEY);
        return false;
      }
      return sessionStorage.getItem(PREVIEW_STORAGE_KEY) === "1";
    } catch (e) {
      return false;
    }
  }

  _hasValidClient() {
    return (
      ADSENSE_CONFIG.enabled === true &&
      typeof ADSENSE_CONFIG.clientId === "string" &&
      ADSENSE_CONFIG.clientId.startsWith("ca-pub-") &&
      !ADSENSE_CONFIG.clientId.includes("XXXX")
    );
  }

  _ensureScript() {
    if (this.scriptInjected || !this._hasValidClient()) return;
    if (
      document.getElementById(SCRIPT_ID) ||
      document.querySelector('script[src*="pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"]')
    ) {
      this.scriptInjected = true;
      return;
    }
    const script = document.createElement("script");
    script.id = SCRIPT_ID;
    script.async = true;
    script.crossOrigin = "anonymous";
    script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${encodeURIComponent(
      ADSENSE_CONFIG.clientId
    )}`;
    document.head.appendChild(script);
    this.scriptInjected = true;
  }

  _ensureObserver() {
    if (this.observer || typeof IntersectionObserver === "undefined") return;
    this.observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this._mountLiveAd(entry.target);
            this.observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "240px 0px" }
    );
  }

  _isContainerVisible(wrapper) {
    if (!wrapper || !wrapper.isConnected) return false;
    if (wrapper.closest(".tab-pane:not(.active)")) return false;
    if (document.body.classList.contains("exam-focus-mode") && wrapper.dataset.adExamHide === "true") {
      return false;
    }
    // Check live layout width to avoid AdSense TagError: availableWidth=0
    return wrapper.offsetWidth > 0;
  }

  _renderPreview(wrapper, slotMeta) {
    wrapper.classList.remove("is-hidden");
    wrapper.classList.add("is-preview");
    if (wrapper.dataset.previewRendered === "true") return;

    const inner = wrapper.querySelector(".ad-slot-inner");
    if (!inner) return;
    inner.innerHTML = `
      <div class="ad-preview-box">
        <span class="ad-preview-badge">AdSense Slot Preview</span>
        <strong class="ad-preview-title">${slotMeta.title}</strong>
        <span class="ad-preview-dims">${slotMeta.dimensions}</span>
        <span class="ad-preview-note">${slotMeta.rationale}</span>
      </div>
    `;
    wrapper.dataset.previewRendered = "true";
  }

  _mountLiveAd(wrapper) {
    if (!wrapper || wrapper.dataset.adLoaded === "true") return;
    if (!this._isContainerVisible(wrapper)) return;

    const slotKey = wrapper.dataset.adSlot;
    const slotMeta = ADSENSE_CONFIG.slots[slotKey];
    if (!slotMeta) return;

    const inner = wrapper.querySelector(".ad-slot-inner");
    if (!inner) return;

    this._ensureScript();

    const ins = document.createElement("ins");
    ins.className = "adsbygoogle";
    ins.style.display = "block";
    ins.setAttribute("data-ad-client", ADSENSE_CONFIG.clientId);
    ins.setAttribute("data-ad-slot", slotMeta.slotId);
    ins.setAttribute("data-ad-format", slotMeta.format || "auto");
    if (slotMeta.format !== "autorelaxed") {
      ins.setAttribute("data-full-width-responsive", "true");
    }

    inner.innerHTML = "";
    inner.appendChild(ins);
    wrapper.dataset.adLoaded = "true";

    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (e) {
      // Ignore AdSense push failures before script finishes loading
    }
  }

  _renderPreviewBanner() {
    if (!this.previewEnabled || document.getElementById("ad-preview-pill")) return;
    const pill = document.createElement("div");
    pill.id = "ad-preview-pill";
    pill.className = "ad-preview-pill no-print";
    pill.innerHTML = `
      <span>Ad Slots Preview ON</span>
      <button type="button" id="btn-exit-ad-preview">Exit Preview</button>
    `;
    document.body.appendChild(pill);
    pill.querySelector("#btn-exit-ad-preview")?.addEventListener("click", () => {
      try {
        sessionStorage.removeItem(PREVIEW_STORAGE_KEY);
        const url = new URL(window.location.href);
        url.searchParams.delete("adpreview");
        window.location.href = url.toString();
      } catch (e) {
        this.previewEnabled = false;
        pill.remove();
        this.refreshVisibleSlots();
      }
    });
  }

  init() {
    if (this.previewEnabled) {
      this._renderPreviewBanner();
    }
    this.refreshVisibleSlots();
  }

  refreshVisibleSlots() {
    const wrappers = document.querySelectorAll(".ad-slot-wrapper[data-ad-slot]");
    const liveReady = this._hasValidClient();

    wrappers.forEach(wrapper => {
      const slotKey = wrapper.dataset.adSlot;
      const slotMeta = ADSENSE_CONFIG.slots[slotKey];
      if (!slotMeta) {
        wrapper.classList.add("is-hidden");
        return;
      }

      if (this.previewEnabled && !liveReady) {
        this._renderPreview(wrapper, slotMeta);
        return;
      }

      if (!liveReady) {
        wrapper.classList.add("is-hidden");
        wrapper.classList.remove("is-preview");
        return;
      }

      wrapper.classList.remove("is-hidden", "is-preview");
      if (wrapper.dataset.adLoaded === "true") return;
      if (!this._isContainerVisible(wrapper)) return;

      this._ensureObserver();
      if (this.observer) {
        this.observer.observe(wrapper);
      } else {
        this._mountLiveAd(wrapper);
      }
    });
  }
}

export const adManager = new AdManager();

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => adManager.init());
  } else {
    adManager.init();
  }
}
