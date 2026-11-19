import os

script_dir = os.path.dirname(os.path.abspath(__file__))
desktop_path = os.path.abspath(os.path.join(script_dir, '..', 'apps', 'desktop-shell', 'desktop.html'))

with open(desktop_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add click event delegation for search result items and recent file items
extra_hooks = """
// Hook search result items click
document.addEventListener('click', (e) => {
  const sItem = e.target.closest('.search-result-item');
  if (sItem) {
    const nameEl = sItem.querySelector('.search-result-name');
    if (nameEl) {
      const name = nameEl.textContent.trim();
      openApp(name);
      const overlay = document.getElementById('search-overlay');
      if (overlay && overlay.classList.contains('visible')) toggleSearch();
    }
  }

  // Hook recent file items
  const rItem = e.target.closest('.recent-file-item') || e.target.closest('.recent-item');
  if (rItem) {
    openApp('Files');
  }

  // Hook welcome search input
  const wSearch = e.target.closest('.welcome-search') || e.target.closest('.welcome-input-wrap');
  if (wSearch) {
    toggleSearch();
  }
});
"""

script_end = content.find('</script>')
if extra_hooks not in content and script_end != -1:
    content = content[:script_end] + extra_hooks + content[script_end:]
    with open(desktop_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Search and recent file hooks added.')
else:
    print('Already present or script_end not found.')
