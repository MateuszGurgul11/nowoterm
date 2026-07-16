/* NOVOTERM BUDOWNICTWO — interakcje (minimalistyczne, GSAP + ScrollTrigger) */
(function () {
  "use strict";

  document.documentElement.classList.remove("no-js");

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasGsap = typeof gsap !== "undefined";

  /* ---------- header scroll state ---------- */
  var header = document.querySelector(".header");
  function onScroll() {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 24);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- mobile nav ---------- */
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", document.body.classList.contains("nav-open"));
    });
    document.querySelectorAll(".nav a").forEach(function (a) {
      a.addEventListener("click", function () { document.body.classList.remove("nav-open"); });
    });
    document.querySelectorAll(".nav-drop > button").forEach(function (b) {
      b.addEventListener("click", function () { b.parentElement.classList.toggle("is-open"); });
    });
  }

  /* ---------- filtr realizacji ---------- */
  var filters = document.querySelectorAll(".filter");
  var works = document.querySelectorAll(".work");
  filters.forEach(function (f) {
    f.addEventListener("click", function () {
      filters.forEach(function (x) { x.classList.remove("is-active"); });
      f.classList.add("is-active");
      var cat = f.dataset.filter;
      works.forEach(function (w) {
        var show = cat === "all" || w.dataset.cat === cat;
        w.classList.toggle("is-hidden", !show);
      });
      if (hasGsap && typeof ScrollTrigger !== "undefined") ScrollTrigger.refresh();
    });
  });

  /* ---------- formularz zapytania ofertowego ---------- */
  var form = document.querySelector(".form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var success = form.querySelector(".form-success");
      var data = new FormData(form);
      var subject = encodeURIComponent("Zapytanie ofertowe — " + (data.get("obiekt") || "obiekt") + ", " + (data.get("metraz") || "?") + " m2");
      var bodyLines = [];
      data.forEach(function (v, k) { if (v) bodyLines.push(k + ": " + v); });
      var mailto = "mailto:biuro@novoterm-budownictwo.pl?subject=" + subject + "&body=" + encodeURIComponent(bodyLines.join("\n"));
      if (success) success.classList.add("is-visible");
      window.location.href = mailto;
    });
  }

  /* ---------- hero video: do przodu natywnie, cofanie bez kolejki seeków ---------- */
  var heroVideo = document.querySelector(".hero-video");
  if (heroVideo && !reducedMotion) {
    var reversing = false;
    var reverseStep = 1 / 24; /* ~1 klatka przy 24 fps — płynne cofanie */

    function playForward() {
      reversing = false;
      heroVideo.playbackRate = 1;
      if (heroVideo.currentTime > 0.02) heroVideo.currentTime = 0;
      var p = heroVideo.play();
      if (p && typeof p.catch === "function") p.catch(function () {});
    }

    function onSeekedReverse() {
      heroVideo.removeEventListener("seeked", onSeekedReverse);
      if (!reversing) return;

      if (heroVideo.currentTime <= reverseStep) {
        playForward();
        return;
      }

      var next = Math.max(0, heroVideo.currentTime - reverseStep);
      heroVideo.addEventListener("seeked", onSeekedReverse);
      try {
        if (typeof heroVideo.fastSeek === "function") heroVideo.fastSeek(next);
        else heroVideo.currentTime = next;
      } catch (e) {
        heroVideo.currentTime = next;
      }
    }

    function startReverse() {
      if (reversing) return;
      reversing = true;
      heroVideo.pause();
      /* od razu pierwszy krok wstecz — bez czekania na ended / buforowanie pustki */
      var startAt = Math.max(0, (heroVideo.duration || heroVideo.currentTime) - reverseStep);
      heroVideo.addEventListener("seeked", onSeekedReverse);
      try {
        if (typeof heroVideo.fastSeek === "function") heroVideo.fastSeek(startAt);
        else heroVideo.currentTime = startAt;
      } catch (e) {
        heroVideo.currentTime = startAt;
      }
    }

    function onTimeUpdate() {
      if (reversing) return;
      var duration = heroVideo.duration;
      if (!duration || !isFinite(duration)) return;
      /* zawróć tuż przed końcem — unikamy pauzy na zdarzeniu ended */
      if (heroVideo.currentTime >= duration - 0.12) startReverse();
    }

    heroVideo.loop = false;
    heroVideo.muted = true;
    heroVideo.preload = "auto";
    heroVideo.addEventListener("timeupdate", onTimeUpdate);

    function startWhenReady() {
      /* dociągnij cały plik, żeby pierwsze cofanie nie czekało na sieć */
      if (heroVideo.buffered.length) {
        var end = heroVideo.buffered.end(heroVideo.buffered.length - 1);
        if (heroVideo.duration && end >= heroVideo.duration - 0.25) {
          playForward();
          return;
        }
      }
      if (heroVideo.readyState >= 3) playForward();
    }

    heroVideo.addEventListener("canplaythrough", function onReady() {
      heroVideo.removeEventListener("canplaythrough", onReady);
      playForward();
    });
    heroVideo.addEventListener("progress", startWhenReady);

    if (heroVideo.readyState >= 3) playForward();
    else heroVideo.load();
  }

  /* ---------- GSAP ---------- */
  if (!hasGsap || reducedMotion) {
    document.documentElement.classList.add("reduced-motion");
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  /* hero — spokojna sekwencja wejścia */
  var heroItems = gsap.utils.toArray("[data-hero]");
  if (heroItems.length) {
    gsap.set(heroItems, { opacity: 0, y: 26 });
    gsap.to(heroItems, {
      opacity: 1, y: 0,
      duration: 1.4,
      ease: "power2.out",
      stagger: 0.16,
      delay: 0.2
    });
  }

  /* reveal — delikatny fade-up (ScrollTrigger.batch) */
  var revealEls = gsap.utils.toArray("[data-reveal]");
  if (revealEls.length) {
    ScrollTrigger.batch(revealEls, {
      start: "top 88%",
      once: true,
      onEnter: function (batch) {
        gsap.to(batch, {
          opacity: 1, y: 0,
          duration: 1.1,
          ease: "power2.out",
          stagger: 0.12,
          overwrite: true
        });
      }
    });
    ScrollTrigger.refresh();
  }

  /* liczniki */
  gsap.utils.toArray("[data-count]").forEach(function (el) {
    var target = parseFloat(el.dataset.count);
    var obj = { v: 0 };
    ScrollTrigger.create({
      trigger: el,
      start: "top 92%",
      once: true,
      onEnter: function () {
        gsap.to(obj, {
          v: target,
          duration: 2,
          ease: "power2.out",
          onUpdate: function () {
            el.textContent = Math.round(obj.v).toLocaleString("pl-PL");
          }
        });
      }
    });
  });
})();
