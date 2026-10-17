/* J.T. Barnes & Associates, PLLC | site behavior
   Plain JavaScript, no dependencies. Everything degrades gracefully without JS. */
(function () {
  "use strict";

  /* ------------------------------------------------------------------
     CONFIGURATION: edit these values, commit, and the site updates.
     Leave an endpoint blank ("") to fall back to a pre-filled email.
     ------------------------------------------------------------------ */
  var CONFIG = {
    firmEmail: "jtbarnes@jtbarnespllc.com",
    // Optional: a form service URL (Formspree, Jotform, Basin, etc.) that accepts POST.
    contactEndpoint: "",
    // Optional: newsletter provider signup URL that accepts POST (Buttondown, Mailchimp, etc.).
    newsletterEndpoint: ""
  };

  var root = document.documentElement;
  root.classList.remove("no-js");
  root.classList.add("js");

  /* Mobile navigation */
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  if (header && toggle) {
    toggle.addEventListener("click", function () {
      var open = header.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.textContent = open ? "Close" : "Menu";
    });
  }

  /* Current year in footer */
  var yr = document.querySelectorAll("[data-year]");
  for (var i = 0; i < yr.length; i++) { yr[i].textContent = String(new Date().getFullYear()); }

  function val(form, name) {
    var el = form.elements[name];
    return el ? String(el.value || "").trim() : "";
  }

  function postForm(url, form, statusEl, okMsg) {
    var data = new FormData(form);
    return fetch(url, { method: "POST", body: data, headers: { "Accept": "application/json" } })
      .then(function (r) {
        if (!r.ok) { throw new Error("status " + r.status); }
        statusEl.textContent = okMsg;
        form.reset();
      })
      .catch(function () {
        statusEl.textContent = "Something went wrong. Please email " + CONFIG.firmEmail + " directly.";
      });
  }

  /* Contact / intake form */
  var contact = document.getElementById("contact-form");
  if (contact) {
    contact.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = document.getElementById("contact-status");
      if (!contact.checkValidity()) { contact.reportValidity(); return; }
      if (CONFIG.contactEndpoint) {
        status.textContent = "Sending...";
        postForm(CONFIG.contactEndpoint, contact, status, "Thank you. Your inquiry was received. We will be in touch soon.");
        return;
      }
      var subject = "Inquiry: " + (val(contact, "matter") || "General") + " | " + val(contact, "name");
      var body = [
        "Name: " + val(contact, "name"),
        "Email: " + val(contact, "email"),
        "Phone: " + val(contact, "phone"),
        "Organization: " + val(contact, "organization"),
        "Matter type: " + val(contact, "matter"),
        "",
        val(contact, "message"),
        "",
        "(Submitted via jtbarnespllc.com. Sender acknowledged that no attorney-client relationship is formed by this inquiry.)"
      ].join("\n");
      window.location.href = "mailto:" + CONFIG.firmEmail + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
      status.textContent = "Your email app should open with your message ready to send. If it does not, please email " + CONFIG.firmEmail + ".";
    });
  }

  /* Newsletter signup */
  var news = document.querySelectorAll(".newsletter-form");
  for (var n = 0; n < news.length; n++) {
    (function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var status = form.querySelector(".form-status");
        if (!form.checkValidity()) { form.reportValidity(); return; }
        if (CONFIG.newsletterEndpoint) {
          status.textContent = "Subscribing...";
          postForm(CONFIG.newsletterEndpoint, form, status, "Subscribed. Watch your inbox for a confirmation email.");
          return;
        }
        var subject = "Subscribe: Securities Compliance Weekly";
        var body = "Please add me to Securities Compliance Weekly.\n\nName: " + val(form, "name") + "\nEmail: " + val(form, "email");
        window.location.href = "mailto:" + CONFIG.firmEmail + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
        status.textContent = "Your email app should open with a subscription request ready to send.";
      });
    })(news[n]);
  }
})();
