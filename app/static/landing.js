/* PayPal Protection Suite — landing page behavior.
   Carousel (auto-advance, arrows, dots, keyboard) + the live
   readiness pill, read from /api/status exactly like the shell. */
(function () {
  "use strict";

  /* ---------- readiness ---------- */
  var pill = document.getElementById("ready-pill");
  var note = document.getElementById("ready-note");
  fetch("/api/status")
    .then(function (r) { return r.json(); })
    .then(function (s) {
      if (s.ready) {
        pill.textContent = "READY";
        pill.className = "pill pill-ok";
        note.textContent = "Sandbox credentials are seated — live checks are on.";
      } else {
        pill.textContent = "DEMO ACCOUNT";
        pill.className = "pill pill-warn";
        note.textContent = "Running on the built-in demo account — " +
          "sample data, every motion real. " + s.message + ".";
      }
    })
    .catch(function () {
      pill.textContent = "STATUS UNKNOWN";
      note.textContent = "Could not reach /api/status.";
    });

  /* ---------- carousel ---------- */
  var slides = Array.prototype.slice.call(
    document.querySelectorAll(".slide"));
  var dotsBox = document.getElementById("car-dots");
  var idx = 0, timer = null;

  slides.forEach(function (_, i) {
    var b = document.createElement("button");
    b.setAttribute("role", "tab");
    b.setAttribute("aria-label", "Slide " + (i + 1));
    b.addEventListener("click", function () { show(i); restart(); });
    dotsBox.appendChild(b);
  });
  var dots = Array.prototype.slice.call(dotsBox.children);

  function show(i) {
    idx = (i + slides.length) % slides.length;
    slides.forEach(function (s, j) {
      s.classList.toggle("active", j === idx);
    });
    dots.forEach(function (d, j) {
      d.classList.toggle("active", j === idx);
    });
  }
  function next() { show(idx + 1); }
  function restart() {
    if (timer) { clearInterval(timer); }
    timer = setInterval(next, 6000);
  }
  document.getElementById("car-next").addEventListener("click",
    function () { next(); restart(); });
  document.getElementById("car-prev").addEventListener("click",
    function () { show(idx - 1); restart(); });
  var car = document.querySelector(".carousel");
  car.addEventListener("mouseenter", function () {
    if (timer) { clearInterval(timer); timer = null; }
  });
  car.addEventListener("mouseleave", restart);
  car.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") { next(); restart(); }
    if (e.key === "ArrowLeft") { show(idx - 1); restart(); }
  });
  show(0);
  restart();
})();

/* ---------- scroll reveal: sections rise in as they arrive ---------- */
if ("IntersectionObserver" in window) {
  document.documentElement.classList.add("reveal-on");
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("inview");
        io.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
}
