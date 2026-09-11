# The Architect's Guide to Claude | Community Knowledge Hub

[![Hub Impressions](https://hits.sh/virendrakulkarni-design.github.io/claude-community-hub-impressions.svg?label=Hub+Impressions&color=da7756)](https://github.com/virendrakulkarni-design/claude-community-hub)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A high-impact, data-driven engineering blog and community dispatch hub built for enterprise technical architects and senior engineers.

Includes real-world stats (the $1 Chevy Tahoe, DPD AI shutdown, OWASP LLM01), human-architect voice, interactive Mermaid vector diagrams, instant copy-to-clipboard for Slack/Teams, and an automated publishing pipeline.

---

## Humanizer Skill & Writing Standards

All post generation adheres to the **Humanizer Skill** located in [`skills/humanizer/SKILL.md`](skills/humanizer/SKILL.md) and [`.agents/skills/humanizer/SKILL.md`](.agents/skills/humanizer/SKILL.md):

- **Strict Zero Emoji Rule:** No emojis are permitted anywhere in generated posts, titles, takeaways, badges, diagrams, or lists. Technical documentation communicates through clear prose and rigorous diagrams, not decorative pictograms.
- **Natural Human Systems Voice:** Eliminates AI clichés such as staged run-ups ("Let's dive in", "As modern pipelines mature"), fake contrasts ("not just X, but Y"), and forced triads.
- **Concrete Technical Rigor:** Anchored in real engineering metrics, architecture boundaries, and production incident post-mortems.

---

## Automated Scheduling (8:30 AM IST / 03:00 UTC)

This repository is equipped with an automated pipeline to publish new posts on schedule:

- **Schedule Time:** `0 3 * * *` (03:00 UTC = 8:30 AM IST).
- **Automation Runner:** [`.github/workflows/schedule_post.yml`](.github/workflows/schedule_post.yml)
- **Generation Script:** [`scripts/generate_post.py`](scripts/generate_post.py) (Cross-platform Python) & [`scripts/generate_post.ps1`](scripts/generate_post.ps1) (Windows PowerShell).
- **Topic Backlog:** Stored in [`data/upcoming_topics.json`](data/upcoming_topics.json) (covering Loop Engineering, MCP, Citations API, Computer Use, and Streaming Tool Calling).

---

## How to Host & Deploy for Your Organization

### Option 1: GitHub Pages (Recommended for Dev Teams)
Zero maintenance, free SSL, and automatic deploys whenever a new post is published:
1. Push this folder to a GitHub repository (e.g. `your-org/claude-architect-hub`).
2. Go to **Settings > Pages > Build and deployment > Source** and select **GitHub Actions**.
3. (Optional for live synthesis) In **Settings > Secrets and variables > Actions**, add your `ANTHROPIC_API_KEY`.
4. The site will automatically publish to `https://<org>.github.io/<repo>/`.

---

### Option 2: Docker & Docker Compose (For Corporate Intranet / VPN)
If corporate security requires running strictly behind your internal company firewall:

```bash
# Build and run with Docker Compose
docker-compose up -d --build
```
The application will be live at `http://<your-internal-ip>:8080`.

---

### Option 3: Local Dev Server or Windows Server
Run with Python or PowerShell:
```powershell
# Using Python
python -m http.server 3000

# Open in browser:
http://localhost:3000
```
Or simply double-click `index.html` to open directly in any browser (supported offline via `data/posts.js`).

---

## CLI Utilities & Manual Publishing

```powershell
# Preview next topic without publishing
powershell -ExecutionPolicy Bypass -File scripts\generate_post.ps1 -DryRun

# Publish next topic immediately
powershell -ExecutionPolicy Bypass -File scripts\generate_post.ps1

# List remaining queued topics
powershell -ExecutionPolicy Bypass -File scripts\generate_post.ps1 -ListQueue
```
