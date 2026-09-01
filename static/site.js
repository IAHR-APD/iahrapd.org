/* IAHR-APD — progressive enhancement only. Every page works without this file. */
(function () {
  'use strict';

  // ---------------------------------------------------------------- countdown
  var days = document.getElementById('days');
  if (days && days.dataset.opening) {
    var target = new Date(days.dataset.opening + 'T00:00:00Z');
    var left = Math.ceil((target - new Date()) / 86400000);
    days.textContent = left > 0 ? left.toLocaleString('en-US') : '0';
  }

  // ---------------------------------------------------------------- hero contours
  var cv = document.getElementById('contours');
  var ctx = cv && cv.getContext('2d');

  function drawContours() {
    if (!ctx) return;
    var dpr = window.devicePixelRatio || 1;
    var w = cv.clientWidth, h = cv.clientHeight;
    if (!w || !h) return;
    cv.width = w * dpr; cv.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    ctx.lineWidth = 1;
    for (var i = 0; i < 26; i++) {
      var t = i / 25;
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(255,255,255,' + (0.045 + 0.075 * (1 - t)) + ')';
      for (var x = 0; x <= w; x += 6) {
        var p = x / w;
        var y = h * (0.12 + t * 1.05)
              - Math.sin(p * 3.1 + i * 0.28) * (18 + i * 2.4)
              - Math.sin(p * 7.4 + i * 0.11) * (6 + i * 0.7);
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
  }
  drawContours();

  var raf;
  window.addEventListener('resize', function () {
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(drawContours);
  });

  // ---------------------------------------------------------------- hero slideshow
  // Cross-fades the rivers of the region behind the headline. Without JavaScript
  // the first photograph simply stays put.
  var stage = document.getElementById('hero-slides');
  if (stage) {
    var slides = Array.prototype.slice.call(stage.querySelectorAll('img'));
    var dots = Array.prototype.slice.call(document.querySelectorAll('#slide-dots button'));
    var place = document.getElementById('slide-place');
    var region = document.getElementById('slide-region');
    var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var at = 0, timer = null;

    function show(i) {
      at = (i + slides.length) % slides.length;
      slides.forEach(function (img, n) { img.classList.toggle('on', n === at); });
      dots.forEach(function (b, n) { b.setAttribute('aria-current', n === at ? 'true' : 'false'); });
      place.textContent = slides[at].dataset.place;
      region.textContent = slides[at].dataset.region;
    }

    function start() {
      if (still || slides.length < 2) return;
      clearInterval(timer);
      timer = setInterval(function () { show(at + 1); },
                          (parseInt(stage.dataset.interval, 10) || 7) * 1000);
    }

    dots.forEach(function (b) {
      b.addEventListener('click', function () {
        show(parseInt(b.dataset.slide, 10));
        start();
      });
    });

    // Do not burn cycles while the tab is in the background.
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) clearInterval(timer); else start();
    });

    start();
  }

  // ---------------------------------------------------------------- gallery year jumps
  var yearnav = document.getElementById('yearnav');
  if (yearnav) {
    yearnav.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('button[data-year]') : null;
      if (!b) return;
      var sec = document.getElementById(b.dataset.year);
      if (sec) sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  // ---------------------------------------------------------------- lightbox
  // Reads its set from whichever .gallery the clicked thumbnail sits in, so any
  // number of years and photographs works with no change here.
  var box = document.getElementById('lightbox');
  if (box) {
    var lbImg = document.getElementById('lb-img');
    var lbCap = document.getElementById('lb-cap');
    var prev = document.getElementById('lb-prev');
    var next = document.getElementById('lb-next');
    var shots = [], at = 0, opener = null;

    function render() {
      var btn = shots[at];
      var img = btn.querySelector('img');
      lbImg.src = btn.dataset.full || img.src;
      lbImg.alt = img.alt;
      var caption = btn.dataset.caption || img.alt;
      lbCap.textContent = caption + '  ·  ' + (at + 1) + ' / ' + shots.length;
      prev.hidden = next.hidden = shots.length < 2;
    }

    function open(btn) {
      shots = Array.prototype.slice.call(btn.closest('.gallery').querySelectorAll('.shot'));
      at = shots.indexOf(btn);
      opener = btn;
      box.hidden = false;
      document.body.style.overflow = 'hidden';
      render();
      document.getElementById('lb-close').focus();
    }

    function close() {
      box.hidden = true;
      lbImg.removeAttribute('src');
      document.body.style.overflow = '';
      if (opener) opener.focus();
    }

    function step(d) {
      at = (at + d + shots.length) % shots.length;
      render();
    }

    document.addEventListener('click', function (e) {
      var btn = e.target.closest ? e.target.closest('.gallery .shot') : null;
      if (btn) { open(btn); return; }
      if (box.hidden) return;
      var ctl = e.target.closest('#lb-close, #lb-prev, #lb-next');
      if (ctl) {
        if (ctl.id === 'lb-close') close();
        else step(ctl.id === 'lb-next' ? 1 : -1);
      } else if (e.target === box || e.target.tagName === 'FIGURE') {
        close();
      }
    });

    document.addEventListener('keydown', function (e) {
      if (box.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowRight') step(1);
      else if (e.key === 'ArrowLeft') step(-1);
    });
  }

  // ---------------------------------------------------------------- email links
  // Addresses are split in the markup so they are not sitting in the page
  // source as plain text for address scrapers to collect.
  var links = document.querySelectorAll("a.mailto[data-u][data-d]");
  for (var i = 0; i < links.length; i++) {
    links[i].href = "mailto:" + links[i].dataset.u + "@" + links[i].dataset.d;
  }
})();
