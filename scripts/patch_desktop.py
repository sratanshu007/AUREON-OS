import os

script_dir = os.path.dirname(os.path.abspath(__file__))
desktop_path = os.path.abspath(os.path.join(script_dir, '..', 'apps', 'desktop-shell', 'desktop.html'))
with open(desktop_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inject CSS before </style>
css_to_add = """
/* ===== AUREON WINDOW MANAGER ===== */
#windows-container {
  position: absolute; inset: 0; pointer-events: none; z-index: 45; overflow: hidden;
}
.aureon-window {
  position: absolute; pointer-events: auto;
  border-radius: 16px; background: rgba(255,255,255,0.88); backdrop-filter: blur(32px); -webkit-backdrop-filter: blur(32px);
  border: 1px solid rgba(220,229,245,0.85); box-shadow: 0 24px 64px rgba(22,119,248,0.22), 0 2px 8px rgba(0,0,0,0.06);
  display: flex; flex-direction: column; overflow: hidden; min-width: 400px; min-height: 280px;
  transition: transform 0.22s cubic-bezier(0.16,1,0.3,1), opacity 0.2s ease;
}
[data-theme="dark"] .aureon-window {
  background: rgba(24,35,60,0.92); border-color: rgba(38,53,84,0.9);
  box-shadow: 0 24px 64px rgba(0,0,0,0.6);
}
.aureon-window.minimized {
  transform: scale(0.4) translateY(300px); opacity: 0; pointer-events: none;
}
.aureon-window.maximized {
  inset: 38px 0 74px 0 !important; width: auto !important; height: auto !important;
  border-radius: 0; border: none;
}
.win-titlebar {
  height: 42px; background: rgba(255,255,255,0.6); backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(220,229,245,0.7); display: flex; align-items: center; justify-content: space-between;
  padding: 0 16px; cursor: move; user-select: none; flex-shrink: 0;
}
[data-theme="dark"] .win-titlebar {
  background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.08);
}
.win-traffic-lights {
  display: flex; align-items: center; gap: 8px; width: 60px;
}
.win-btn {
  width: 12px; height: 12px; border-radius: 50%; border: none; cursor: pointer; transition: 0.15s; outline: none;
}
.win-btn-close { background: #FF5F56; }
.win-btn-min { background: #FFBD2E; }
.win-btn-max { background: #27C93F; }
.win-btn:hover { filter: brightness(0.85); transform: scale(1.1); }
.win-title {
  font-size: 13px; font-weight: 600; color: var(--text-primary); display: flex; align-items: center; gap: 8px;
}
.win-body {
  flex: 1; border: none; width: 100%; height: 100%; background: transparent; overflow: hidden;
}
"""

style_end = content.find('</style>')
if style_end != -1 and 'aureon-window' not in content:
    content = content[:style_end] + css_to_add + content[style_end:]

# 2. Inject windows-container before dock
dock_pos = content.find('<div id="dock"')
if dock_pos != -1 and 'id="windows-container"' not in content:
    content = content[:dock_pos] + '<div id="windows-container"></div>\n' + content[dock_pos:]

# 3. Inject JS before </script>
js_to_add = """
// ===== AUREON WINDOW MANAGER ENGINE =====
const APP_REGISTRY = {
  'Files': { title: 'AUREON Files', url: '../files/files.html', icon: '📁', width: 920, height: 600 },
  'Browser': { title: 'AUREON Browser', url: '../browser/browser.html', icon: '🌐', width: 960, height: 620 },
  'Terminal': { title: 'AUREON Terminal', url: '../terminal/terminal.html', icon: '⌨️', width: 780, height: 500 },
  'Settings': { title: 'AUREON Settings', url: '../settings/settings.html', icon: '⚙️', width: 900, height: 600 },
  'Store': { title: 'AUREON Store', url: '../store/store.html', icon: '🛍️', width: 920, height: 600 },
  'AUREON Store': { title: 'AUREON Store', url: '../store/store.html', icon: '🛍️', width: 920, height: 600 },
  'Notes': { title: 'AUREON Notes', url: '../notes/notes.html', icon: '📝', width: 840, height: 540 },
  'Calendar': { title: 'AUREON Calendar', url: '../calendar/calendar.html', icon: '📅', width: 860, height: 560 },
  'Music': { title: 'AUREON Music', url: '../music/music.html', icon: '🎵', width: 840, height: 540 },
  'Photos': { title: 'AUREON Photos', url: '../photos/photos.html', icon: '🖼️', width: 900, height: 580 },
  'Videos': { title: 'AUREON Videos', url: '../videos/videos.html', icon: '🎬', width: 920, height: 580 },
  'Calculator': { title: 'Calculator', url: '../calculator/calculator.html', icon: '🔢', width: 380, height: 540 },
  'AUREON AI': { title: 'AUREON AI Assistant', url: '../ai-assistant/ai_assistant.html', icon: '✨', width: 800, height: 580 },
  'System Monitor': { title: 'System Monitor', url: '../system-monitor/monitor.html', icon: '📊', width: 920, height: 600 },
  'This PC': { title: 'This PC — AUREON Files', url: '../files/files.html', icon: '💻', width: 920, height: 600 },
  'Recycle Bin': { title: 'Recycle Bin', url: '../files/files.html', icon: '🗑️', width: 860, height: 540 },
  'Projects': { title: 'Projects — AUREON Files', url: '../files/files.html', icon: '💼', width: 920, height: 600 },
  'Media': { title: 'Media — AUREON Photos', url: '../photos/photos.html', icon: '🎬', width: 900, height: 580 }
};

let topZ = 100;
const openWindows = {};

function openApp(appName) {
  const meta = APP_REGISTRY[appName] || APP_REGISTRY['Files'];
  if (openWindows[appName]) {
    const win = openWindows[appName];
    if (win.classList.contains('minimized')) {
      win.classList.remove('minimized');
      bringToFront(win);
    } else if (win.style.zIndex == topZ) {
      minimizeWindow(win);
    } else {
      bringToFront(win);
    }
    return;
  }

  const container = document.getElementById('windows-container');
  const win = document.createElement('div');
  win.className = 'aureon-window';
  win.id = 'win-' + appName.replace(/\\s+/g, '-');
  win.dataset.app = appName;

  // Stagger position
  const offset = Object.keys(openWindows).length * 28 + 60;
  const w = Math.min(meta.width, window.innerWidth - 60);
  const h = Math.min(meta.height, window.innerHeight - 140);
  const left = Math.max(30, (window.innerWidth - w) / 2 + (offset % 120) - 60);
  const top = Math.max(50, (window.innerHeight - h) / 2 + (offset % 80) - 40);

  win.style.width = w + 'px';
  win.style.height = h + 'px';
  win.style.left = left + 'px';
  win.style.top = top + 'px';
  win.style.zIndex = ++topZ;

  win.innerHTML = `
    <div class="win-titlebar">
      <div class="win-traffic-lights">
        <button class="win-btn win-btn-close" title="Close" onclick="closeWindow(this.closest('.aureon-window'))"></button>
        <button class="win-btn win-btn-min" title="Minimize" onclick="minimizeWindow(this.closest('.aureon-window'))"></button>
        <button class="win-btn win-btn-max" title="Maximize" onclick="maximizeWindow(this.closest('.aureon-window'))"></button>
      </div>
      <div class="win-title"><span>${meta.icon}</span> <span>${meta.title}</span></div>
      <div style="width:60px;"></div>
    </div>
    <iframe class="win-body" src="${meta.url}"></iframe>
  `;

  // Dragging logic
  const tb = win.querySelector('.win-titlebar');
  let isDragging = false, startX, startY, initialL, initialT;

  tb.onmousedown = (e) => {
    if (e.target.classList.contains('win-btn')) return;
    bringToFront(win);
    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
    initialL = win.offsetLeft;
    initialT = win.offsetTop;
    document.onmousemove = (me) => {
      if (!isDragging) return;
      win.style.left = (initialL + me.clientX - startX) + 'px';
      win.style.top = Math.max(36, (initialT + me.clientY - startY)) + 'px';
    };
    document.onmouseup = () => { isDragging = false; document.onmousemove = null; };
  };

  tb.ondblclick = (e) => {
    if (e.target.classList.contains('win-btn')) return;
    maximizeWindow(win);
  };

  win.onmousedown = () => bringToFront(win);

  container.appendChild(win);
  openWindows[appName] = win;
  updateDockDot(appName, true);
}

function bringToFront(win) {
  win.style.zIndex = ++topZ;
}

function minimizeWindow(win) {
  win.classList.add('minimized');
}

function maximizeWindow(win) {
  win.classList.toggle('maximized');
}

function closeWindow(win) {
  const app = win.dataset.app;
  delete openWindows[app];
  win.remove();
  updateDockDot(app, false);
}

function updateDockDot(appName, isOpen) {
  document.querySelectorAll('.dock-icon').forEach(icon => {
    if (icon.dataset.label === appName ||
       (appName === 'AUREON Store' && icon.dataset.label === 'Store')) {
      icon.classList.toggle('running', isOpen);
    }
  });
}

// Hook dock clicks
document.querySelectorAll('.dock-icon').forEach(icon => {
  icon.addEventListener('click', () => {
    const label = icon.dataset.label;
    if (label === 'Launcher') {
      togglePanel('app-launcher');
    } else if (label) {
      openApp(label);
    }
  });
});

// Hook desktop icons double-click
document.querySelectorAll('.desktop-icon').forEach(icon => {
  icon.addEventListener('dblclick', () => {
    const label = icon.querySelector('.desktop-icon-label').textContent.trim();
    openApp(label);
  });
});

// Hook App Launcher items
document.addEventListener('click', (e) => {
  const lItem = e.target.closest('.launcher-app-item');
  if (lItem) {
    const name = lItem.querySelector('.launcher-app-name').textContent.trim();
    openApp(name);
    hidePanel('app-launcher');
  }
});
"""

script_end = content.find('</script>')
if script_end != -1 and 'APP_REGISTRY' not in content:
    content = content[:script_end] + js_to_add + content[script_end:]

with open(desktop_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Window Manager successfully injected into desktop.html')
