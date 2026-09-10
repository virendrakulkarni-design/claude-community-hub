/**
 * Claude Community Hub - Client Application
 * Handles dynamic post rendering, search, Mermaid diagram compilation, theme toggles, and Markdown exports.
 */

let allPosts = [];

document.addEventListener('DOMContentLoaded', async () => {
  // 1. Initialize Mermaid configuration
  mermaid.initialize({
    startOnLoad: false,
    theme: document.body.classList.contains('light-theme') ? 'default' : 'dark',
    themeVariables: {
      fontFamily: 'Inter, -apple-system, sans-serif',
      fontSize: '13px',
      primaryColor: '#1e293b',
      primaryTextColor: '#f8fafc',
      primaryBorderColor: '#38bdf8',
      lineColor: '#64748b'
    },
    securityLevel: 'loose'
  });

  // 2. Setup Theme
  initTheme();

  // 3. Load Posts Data (Supports both HTTP fetch and direct file:// fallback)
  await loadPosts();

  // 4. Render UI
  renderTabs();
  renderPosts(allPosts);

  // 5. Setup Search
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      const filtered = allPosts.filter(p => 
        p.title.toLowerCase().includes(query) ||
        p.lead.toLowerCase().includes(query) ||
        p.level.toLowerCase().includes(query) ||
        (p.mentalModel && p.mentalModel.text.toLowerCase().includes(query))
      );
      renderPosts(filtered);
    });
  }
});

/**
 * Load Posts from window.POSTS_DATA or fetch('data/posts.json')
 */
async function loadPosts() {
  if (window.POSTS_DATA && Array.isArray(window.POSTS_DATA)) {
    allPosts = window.POSTS_DATA;
    return;
  }

  try {
    const res = await fetch('data/posts.json');
    if (res.ok) {
      allPosts = await res.json();
    }
  } catch (err) {
    console.warn("Could not fetch data/posts.json, relying on inline data if available", err);
  }
}

/**
 * Render Filter Tabs
 */
function renderTabs() {
  const tabsContainer = document.getElementById('levelTabs');
  if (!tabsContainer) return;

  let tabsHtml = `<button class="tab-btn active" data-target="all"><span class="tab-num">ALL</span><span class="tab-label">All Dispatches (${allPosts.length})</span></button>`;
  
  allPosts.forEach((post, index) => {
    const num = `L${index + 1}`;
    const shortLabel = post.level.split(':')[1]?.trim() || post.title.slice(0, 18) + '...';
    tabsHtml += `
      <button class="tab-btn" data-target="${post.id}">
        <span class="tab-num">${num}</span>
        <span class="tab-label">${escapeHtml(shortLabel)}</span>
      </button>
    `;
  });

  tabsContainer.innerHTML = tabsHtml;

  // Add click listener
  tabsContainer.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      tabsContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const targetId = btn.getAttribute('data-target');
      if (targetId === 'all') {
        renderPosts(allPosts);
      } else {
        const selected = allPosts.filter(p => p.id === targetId);
        renderPosts(selected);
        const targetEl = document.getElementById(targetId);
        if (targetEl) {
          window.scrollTo({
            top: targetEl.getBoundingClientRect().top + window.pageYOffset - 80,
            behavior: 'smooth'
          });
        }
      }
    });
  });
}

/**
 * Render Posts List
 */
async function renderPosts(posts) {
  const container = document.getElementById('posts-container');
  if (!container) return;

  if (!posts || posts.length === 0) {
    container.innerHTML = `<div class="empty-state">No architectural dispatches match your search query.</div>`;
    return;
  }

  container.innerHTML = posts.map(post => `
    <article id="${post.id}" class="post-card">
      <div class="post-header">
        <div class="post-meta">
          <span class="difficulty-badge ${post.levelClass || 'level-1'}">${escapeHtml(post.level)}</span>
          <span class="read-time">⏱️ ${escapeHtml(post.readTime)}</span>
          <span class="target-role">Audience: ${escapeHtml(post.audience)}</span>
        </div>
        <h2 class="post-title">${escapeHtml(post.title)}</h2>
        <p class="post-lead">${escapeHtml(post.lead)}</p>
        
        <div class="action-bar">
          <button class="btn-copy-slack" onclick="copyPostMarkdown('${post.id}')">
            📋 Copy Post for Slack / Teams / Confluence
          </button>
        </div>
      </div>

      <div class="post-body">
        <!-- Reality Check Stats Box -->
        <div class="stat-callout ${post.stats.type || 'info'}">
          <div class="stat-icon">${getStatIcon(post.stats.type)}</div>
          <div class="stat-text">
            <strong>${escapeHtml(post.stats.title)}</strong>
            <ul>
              ${post.stats.items.map(item => `<li>${item}</li>`).join('')}
            </ul>
          </div>
        </div>

        <!-- 60-Second Mental Model -->
        <h3>${escapeHtml(post.mentalModel.title)}</h3>
        <p>${post.mentalModel.text}</p>

        <!-- Architecture Diagram -->
        <div class="diagram-wrapper">
          <div class="mermaid">
${post.diagram}
          </div>
          <span class="diagram-caption">${escapeHtml(post.diagramCaption)}</span>
        </div>

        <!-- Code Block -->
        <div class="code-wrapper">
          <div class="code-header">
            <span>${escapeHtml(post.codeTitle)}</span>
            <button class="btn-copy-code" onclick="copySnippet(this)">Copy</button>
          </div>
          <pre><code>${escapeHtml(post.codeContent)}</code></pre>
        </div>

        <!-- Monday Morning Takeaway -->
        <div class="takeaway-box">
          <h4>${escapeHtml(post.takeaway.title)}</h4>
          <ol>
            ${post.takeaway.items.map(item => `<li>${item}</li>`).join('')}
          </ol>
          <p class="takeaway-badge">${escapeHtml(post.takeaway.badge)}</p>
        </div>
      </div>
    </article>
  `).join('');

  // Re-run Mermaid parser on the newly injected diagrams
  try {
    await mermaid.run({
      nodes: document.querySelectorAll('.mermaid')
    });
  } catch (err) {
    console.warn("Mermaid render error:", err);
  }
}

function getStatIcon(type) {
  switch (type) {
    case 'danger': return '⚠️';
    case 'success': return '💰';
    case 'warning': return '🔥';
    default: return '💡';
  }
}

/**
 * Toast Notification
 */
function showToast(message) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3200);
}

/**
 * Copy Code Snippet
 */
function copySnippet(button) {
  const pre = button.closest('.code-wrapper').querySelector('pre code');
  if (!pre) return;
  
  navigator.clipboard.writeText(pre.innerText).then(() => {
    const originalText = button.innerText;
    button.innerText = '✓ Copied';
    setTimeout(() => {
      button.innerText = originalText;
    }, 2000);
    showToast("Code snippet copied to clipboard!");
  }).catch(err => {
    console.error("Failed to copy snippet: ", err);
  });
}

/**
 * Generate formatted Markdown for Slack / Teams
 */
function copyPostMarkdown(postId) {
  const post = allPosts.find(p => p.id === postId);
  if (!post) return;

  const statsText = post.stats.items.map(i => `• ${stripHtml(i)}`).join('\n');
  const takeawayText = post.takeaway.items.map((it, idx) => `${idx + 1}. ${stripHtml(it)}`).join('\n');

  const markdown = `*Architect Dispatch | ${post.level}*
═══════════════════════════════════════════════════════════════
*${post.title}*

${post.lead}

🚨 *${post.stats.title}*
${statsText}

💡 *${post.mentalModel.title}*
${stripHtml(post.mentalModel.text)}

💻 *PRODUCTION CODE / SPEC:*
\`\`\`
${post.codeContent}
\`\`\`

🎁 *${post.takeaway.title}*
${takeawayText}

📌 *Key Takeaway:* ${post.takeaway.badge}
`;

  navigator.clipboard.writeText(markdown).then(() => {
    showToast(`✓ Copied "${post.title.slice(0, 25)}..." ready for Slack/Teams!`);
  }).catch(err => {
    console.error("Copy failed: ", err);
  });
}

function stripHtml(html) {
  const tmp = document.createElement("DIV");
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || "";
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Theme Manager
 */
function initTheme() {
  const themeToggle = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('claude-hub-theme');
  
  if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light-theme');
      const isLight = document.body.classList.contains('light-theme');
      localStorage.setItem('claude-hub-theme', isLight ? 'light' : 'dark');
      showToast(isLight ? "☀️ Switched to Light Theme" : "🌙 Switched to Dark Theme");
      renderPosts(allPosts);
    });
  }
}
