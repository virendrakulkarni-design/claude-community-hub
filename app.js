/**
 * Claude Community Hub - Client Application
 * Implements Single-Post Reader Architecture:
 * - One post on screen at a time
 * - Sticky navigation toolbar & dropdown selector
 * - Bottom Next/Prev dispatch cards
 * - Left/Right Arrow keyboard shortcuts
 * - Instant search & jump dropdown
 * - Mermaid vector diagram compilation
 */

let allPosts = [];
let currentIndex = 0;

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

  // 3. Load Posts Data
  await loadPosts();

  if (!allPosts || allPosts.length === 0) {
    document.getElementById('single-post-container').innerHTML = `<div class="empty-state">No dispatches available.</div>`;
    return;
  }

  // 4. Determine initial post from URL hash (e.g. #post-3)
  const hash = window.location.hash.replace('#', '');
  const hashIndex = allPosts.findIndex(p => p.id === hash);
  if (hashIndex !== -1) {
    currentIndex = hashIndex;
  }

  // 5. Initialize Navigation & Render
  renderNavPills();
  initDropdown();
  initToolbarButtons();
  initBottomCards();
  initKeyboardNav();
  initSearch();

  // 6. Display active post
  showPost(currentIndex, false);
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
 * Display Single Post at index
 */
async function showPost(index, shouldScroll = true) {
  if (index < 0 || index >= allPosts.length) return;
  currentIndex = index;
  const post = allPosts[currentIndex];

  const container = document.getElementById('single-post-container');
  if (!container) return;

  // Render Post HTML
  container.innerHTML = `
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
  `;

  // Compile Mermaid Diagram for this post
  try {
    await mermaid.run({
      nodes: container.querySelectorAll('.mermaid')
    });
  } catch (err) {
    console.warn("Mermaid compile notice:", err);
  }

  // Update UI Controls
  updateNavigationState();

  // Update URL hash without scrolling
  history.replaceState(null, null, `#${post.id}`);

  // Scroll to top of article if user clicked next/prev
  if (shouldScroll) {
    const toolbar = document.querySelector('.reader-toolbar-sticky');
    const offset = toolbar ? toolbar.offsetHeight + 60 : 100;
    const top = container.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  }
}

/**
 * Update Nav State (Pills, Counter, Pager Buttons, Bottom Cards)
 */
function updateNavigationState() {
  const total = allPosts.length;
  const post = allPosts[currentIndex];

  // 1. Counter badge & Dropdown
  const counter = document.getElementById('postCounter');
  if (counter) counter.textContent = `Dispatch ${currentIndex + 1} of ${total}`;

  const dropdown = document.getElementById('postDropdown');
  if (dropdown) dropdown.value = currentIndex;

  // 2. Toolbar buttons
  const prevBtn = document.getElementById('prevBtnTop');
  const nextBtn = document.getElementById('nextBtnTop');
  if (prevBtn) prevBtn.disabled = (currentIndex === 0);
  if (nextBtn) nextBtn.disabled = (currentIndex === total - 1);

  // 3. Top pills active state
  document.querySelectorAll('#levelTabs .tab-btn').forEach((btn, idx) => {
    btn.classList.toggle('active', idx === currentIndex);
  });

  // 4. Bottom Next/Prev Navigation Cards
  const prevCard = document.getElementById('footerPrevCard');
  const nextCard = document.getElementById('footerNextCard');
  const prevTitle = document.getElementById('footerPrevTitle');
  const nextTitle = document.getElementById('footerNextTitle');

  if (currentIndex > 0) {
    prevCard.classList.remove('disabled');
    prevTitle.textContent = allPosts[currentIndex - 1].title;
  } else {
    prevCard.classList.add('disabled');
    prevTitle.textContent = "You're at the first dispatch";
  }

  if (currentIndex < total - 1) {
    nextCard.classList.remove('disabled');
    nextTitle.textContent = allPosts[currentIndex + 1].title;
  } else {
    nextCard.classList.add('disabled');
    nextTitle.textContent = "You're at the latest dispatch";
  }
}

/**
 * Render Bookmark Pills in Hero
 */
function renderNavPills() {
  const container = document.getElementById('levelTabs');
  if (!container) return;

  container.innerHTML = allPosts.map((post, idx) => {
    const shortLabel = post.level.split(':')[1]?.trim() || post.title.slice(0, 16);
    return `
      <button class="tab-btn ${idx === currentIndex ? 'active' : ''}" onclick="showPost(${idx})">
        <span class="tab-num">L${idx + 1}</span>
        <span class="tab-label">${escapeHtml(shortLabel)}</span>
      </button>
    `;
  }).join('');
}

/**
 * Initialize Dropdown Menu
 */
function initDropdown() {
  const dropdown = document.getElementById('postDropdown');
  if (!dropdown) return;

  dropdown.innerHTML = allPosts.map((p, idx) => `
    <option value="${idx}">L${idx + 1}: ${escapeHtml(p.title)}</option>
  `).join('');

  dropdown.addEventListener('change', (e) => {
    showPost(parseInt(e.target.value, 10));
  });
}

/**
 * Initialize Toolbar Buttons
 */
function initToolbarButtons() {
  const prevBtn = document.getElementById('prevBtnTop');
  const nextBtn = document.getElementById('nextBtnTop');

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (currentIndex > 0) showPost(currentIndex - 1);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      if (currentIndex < allPosts.length - 1) showPost(currentIndex + 1);
    });
  }
}

/**
 * Initialize Bottom Cards
 */
function initBottomCards() {
  const prevCard = document.getElementById('footerPrevCard');
  const nextCard = document.getElementById('footerNextCard');

  if (prevCard) {
    prevCard.addEventListener('click', () => {
      if (currentIndex > 0) showPost(currentIndex - 1);
    });
  }

  if (nextCard) {
    nextCard.addEventListener('click', () => {
      if (currentIndex < allPosts.length - 1) showPost(currentIndex + 1);
    });
  }
}

/**
 * Keyboard Navigation (Left / Right Arrow Keys)
 */
function initKeyboardNav() {
  window.addEventListener('keydown', (e) => {
    // Avoid interfering with typing in the search input
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT')) {
      return;
    }

    if (e.key === 'ArrowLeft') {
      if (currentIndex > 0) {
        showPost(currentIndex - 1);
        showToast("← Previous Dispatch");
      }
    } else if (e.key === 'ArrowRight') {
      if (currentIndex < allPosts.length - 1) {
        showPost(currentIndex + 1);
        showToast("Next Dispatch →");
      }
    }
  });
}

/**
 * Search & Jump Dropdown
 */
function initSearch() {
  const searchInput = document.getElementById('searchInput');
  const searchResults = document.getElementById('searchResults');
  if (!searchInput || !searchResults) return;

  searchInput.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) {
      searchResults.classList.add('hidden');
      searchResults.innerHTML = '';
      return;
    }

    const matches = allPosts
      .map((p, idx) => ({ post: p, index: idx }))
      .filter(({ post }) => 
        post.title.toLowerCase().includes(q) ||
        post.lead.toLowerCase().includes(q) ||
        post.level.toLowerCase().includes(q) ||
        (post.mentalModel && post.mentalModel.text.toLowerCase().includes(q))
      );

    if (matches.length === 0) {
      searchResults.innerHTML = `<div class="search-result-item" style="color: var(--text-muted); cursor: default;">No matching dispatches found</div>`;
      searchResults.classList.remove('hidden');
      return;
    }

    searchResults.innerHTML = matches.map(({ post, index }) => `
      <div class="search-result-item" onclick="jumpToPost(${index})">
        <span class="search-item-level">L${index + 1} • ${escapeHtml(post.level)}</span>
        <div class="search-item-title">${escapeHtml(post.title)}</div>
      </div>
    `).join('');

    searchResults.classList.remove('hidden');
  });

  // Close dropdown on outside click
  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.classList.add('hidden');
    }
  });
}

function jumpToPost(index) {
  const searchResults = document.getElementById('searchResults');
  const searchInput = document.getElementById('searchInput');
  if (searchResults) searchResults.classList.add('hidden');
  if (searchInput) searchInput.value = '';
  showPost(index);
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
 * Copy Post for Slack / Teams / Confluence
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
    showToast(`✓ Copied "${post.title.slice(0, 22)}..." ready for Slack/Teams!`);
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
      showPost(currentIndex, false);
    });
  }
}
