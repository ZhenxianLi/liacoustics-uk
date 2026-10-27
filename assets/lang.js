// Bilingual pages: blocks are marked lang="en" / lang="zh" and site.css hides
// whichever language is not selected. Load this in <head> so the choice is
// applied before first paint. Priority: ?lang= in the URL, then the saved
// choice, then the browser language.
(function () {
  var KEY = 'liacoustics-lang';
  var root = document.documentElement;

  function saved() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function initial() {
    var q = new URLSearchParams(location.search).get('lang');
    if (q === 'en' || q === 'zh') return q;
    var s = saved();
    if (s === 'en' || s === 'zh') return s;
    return /^zh\b/i.test(navigator.language || '') ? 'zh' : 'en';
  }

  function apply(lang) {
    root.setAttribute('data-lang', lang);
    root.setAttribute('lang', lang === 'zh' ? 'zh-CN' : 'en');
    var title = root.getAttribute('data-title-' + lang);
    if (title) document.title = title;
    var buttons = document.querySelectorAll('.lang-switch button');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute('aria-pressed', String(buttons[i].dataset.setLang === lang));
    }
  }

  apply(initial());

  document.addEventListener('DOMContentLoaded', function () {
    apply(root.getAttribute('data-lang'));
    document.addEventListener('click', function (e) {
      var btn = e.target.closest('.lang-switch button');
      if (!btn) return;
      var lang = btn.dataset.setLang;
      try { localStorage.setItem(KEY, lang); } catch (err) {}
      var url = new URL(location.href);
      if (url.searchParams.has('lang')) {
        url.searchParams.set('lang', lang);
        history.replaceState(null, '', url);
      }
      apply(lang);
    });
  });
})();
