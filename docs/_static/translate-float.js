function googleTranslateElementInit() {
  new google.translate.TranslateElement({
    pageLanguage: 'en',
    includedLanguages: 'zh-CN,ja,fr,es',
    layout: google.translate.TranslateElement.InlineLayout.SIMPLE
  }, 'google_translate_floating');
}

// Floating button UI
window.addEventListener('DOMContentLoaded', () => {
  const translateDiv = document.createElement('div');
  translateDiv.id = 'google_translate_floating';
  translateDiv.style.position = 'fixed';
  translateDiv.style.bottom = '20px';
  translateDiv.style.right = '20px';
  translateDiv.style.zIndex = '9999';
  translateDiv.style.backgroundColor = '#f0f0f0';
  translateDiv.style.border = '1px solid #ccc';
  translateDiv.style.padding = '6px 8px';
  translateDiv.style.borderRadius = '6px';
  translateDiv.style.boxShadow = '0 0 6px rgba(0,0,0,0.2)';
  translateDiv.style.fontSize = '0.9em';
  document.body.appendChild(translateDiv);
});
