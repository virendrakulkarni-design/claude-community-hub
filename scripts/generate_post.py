#!/usr/bin/env python3
"""
Automated Post Generation Script for Claude Enterprise Architecture Hub
Pulls the next topic from data/upcoming_topics.json, validates schemas,
updates data/posts.json and data/posts.js, and logs telemetry.
"""

import os
import sys
import json
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
POSTS_JSON = os.path.join(DATA_DIR, "posts.json")
POSTS_JS = os.path.join(DATA_DIR, "posts.js")
UPCOMING_JSON = os.path.join(DATA_DIR, "upcoming_topics.json")

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sync_posts_js(posts):
    """Write posts array as JavaScript variable for offline/file:// preview."""
    js_content = "// Auto-generated data sync for direct local file:// and offline execution\n"
    js_content += f"window.POSTS_DATA = {json.dumps(posts, indent=2, ensure_ascii=False)};\n"
    with open(POSTS_JS, "w", encoding="utf-8") as f:
        f.write(js_content)

def validate_post_schema(post):
    """Validate that required fields exist and are formatted properly."""
    required = ["id", "level", "readTime", "audience", "title", "lead", "stats", "mentalModel", "diagram", "diagramCaption", "codeTitle", "codeContent", "takeaway"]
    for field in required:
        if field not in post:
            raise ValueError(f"Post is missing required field: '{field}'")
    
    if not isinstance(post["stats"].get("items"), list):
        raise ValueError("post.stats.items must be a list of strings")
    if not isinstance(post["takeaway"].get("items"), list):
        raise ValueError("post.takeaway.items must be a list of strings")
    return True

def generate_with_claude_api(topic_title):
    """
    If ANTHROPIC_API_KEY is available in environment, calls Claude 3.7
    to generate a brand-new post adhering to our architectural standard.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""You are a Principal Systems Architect writing for an elite enterprise Claude engineering community.
Write a deep, technically rigorous, and engaging post about: '{topic_title}'.

Include:
1. Passionate human architect voice (debunk myths, use relatable developer analogies, zero generic fluff).
2. Real-world stats or high-profile failure incidents.
3. 60-second mental model (e.g. comparing to CPU caches, SQL injection, OS syscalls).
4. Mermaid diagram syntax (valid graph LR or sequenceDiagram).
5. Clean Python/XML production code snippet.
6. Actionable 'Monday Morning' takeaway.

Output ONLY valid JSON matching this exact structure:
{{
  "id": "post-X",
  "level": "LEVEL X: ...",
  "levelClass": "level-3",
  "readTime": "8 min read",
  "audience": "Senior Backend & AI Engineers",
  "title": "...",
  "lead": "...",
  "stats": {{
    "type": "danger",
    "title": "...",
    "items": ["..."]
  }},
  "mentalModel": {{
    "title": "1. The 60-Second Mental Model: ...",
    "text": "..."
  }},
  "diagram": "graph TD\\n...",
  "diagramCaption": "Figure X: ...",
  "codeTitle": "...py",
  "codeContent": "...",
  "takeaway": {{
    "title": "🎁 Architect’s \\"Monday Morning\\" Takeaway",
    "items": ["..."],
    "badge": "..."
  }}
}}"""

        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        raw_text = response.content[0].text
        # Strip potential markdown code fences from response
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0]
        return json.loads(raw_text.strip())
    except Exception as e:
        print(f"⚠️ Claude API generation failed or not configured: {e}. Falling back to curated queue.")
        return None

def main():
    parser = argparse.ArgumentParser(description="Publish next scheduled Claude Architecture post.")
    parser.add_argument("--dry-run", action="store_true", help="Validate next post without modifying files.")
    parser.add_argument("--force-topic", type=str, help="Publish a specific topic name or ID.")
    parser.add_argument("--list-queue", action="store_true", help="List remaining upcoming topics.")
    args = parser.parse_args()

    upcoming = load_json(UPCOMING_JSON)
    posts = load_json(POSTS_JSON)

    if args.list_queue:
        print(f"\n📋 Upcoming Queued Topics ({len(upcoming)} remaining):")
        for i, t in enumerate(upcoming, 1):
            print(f"  {i}. [{t.get('id', 'new')}] {t.get('topic', t.get('title'))}")
        return

    if not upcoming:
        print("⚠️ No more topics in upcoming_topics.json queue! Please add new topics.")
        sys.exit(0)

    # Pick next topic
    if args.force_topic:
        target_idx = next((i for i, t in enumerate(upcoming) if args.force_topic.lower() in t.get('topic', '').lower() or args.force_topic == t.get('id')), 0)
        next_topic = upcoming.pop(target_idx)
    else:
        next_topic = upcoming.pop(0)

    print(f"🚀 Processing scheduled post: {next_topic.get('title', next_topic.get('topic'))}")

    # Check if API generation is preferred
    generated_post = None
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("🤖 Attempting dynamic synthesis via Claude 3.7 API...")
        generated_post = generate_with_claude_api(next_topic.get('topic', next_topic.get('title')))

    post_to_publish = generated_post if generated_post else next_topic

    # Assign correct incremental ID
    post_to_publish["id"] = f"post-{len(posts) + 1}"
    validate_post_schema(post_to_publish)

    if args.dry_run:
        print("\n[DRY RUN] Successfully validated post schema:")
        print(f"Title: {post_to_publish['title']}")
        print(f"Level: {post_to_publish['level']}")
        print(f"Diagram lines: {len(post_to_publish['diagram'].splitlines())}")
        print("\nDry run completed successfully. No files written.")
        return

    # Append and commit to disk
    posts.append(post_to_publish)
    save_json(POSTS_JSON, posts)
    sync_posts_js(posts)
    save_json(UPCOMING_JSON, upcoming)

    print(f"✅ Published '{post_to_publish['title']}' to data/posts.json and data/posts.js.")
    print(f"📊 Total Published Posts: {len(posts)} | Remaining Queued: {len(upcoming)}")

if __name__ == "__main__":
    main()
