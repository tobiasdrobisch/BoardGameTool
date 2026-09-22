let translations = {};
let currentLang = "en";

async function loadLanguage(lang) {
    const response = await fetch(`/locales/${lang}.json`);
    translations = await response.json();

    currentLang = lang;
    localStorage.setItem("lang", lang);

    applyTranslations();
}

function t(key, vars = {}) {

  let text = translations[key] || key;

  for (const k in vars) {
    text = text.replace(`{${k}}`, vars[k]);
  }

  return text;
}

function applyTranslations() {

    // normal texts
    document.querySelectorAll("[data-i18n]").forEach(el => {

        const key = el.dataset.i18n;

        if (el.dataset.count) {
            el.innerText = t(key, { count: el.dataset.count });
        } else {
            el.innerText = t(key);
        }

    });

    // placeholder (inputs)
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {

        const key = el.dataset.i18nPlaceholder;
        el.placeholder = t(key);

    });

}

async function initLanguage() {
    const savedLang = localStorage.getItem("lang") || "en";
    await loadLanguage(savedLang);
}

document.addEventListener("DOMContentLoaded", () => {
    initLanguage();
});