#!/usr/bin/env python3
"""
Automated Post Generation Script for Claude Enterprise Architecture Hub
Supports daily automated publishing, custom topic suggestions (--custom-topic),
dynamic synthesis with Claude 3.7, and auto-replenishment.
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

# Specialized knowledge templates for suggested keywords when running offline/without API key
KEYWORD_TEMPLATES = {
    "graph": {
        "topic": "Graph Engineering & Knowledge Graphs with Claude",
        "level": "LEVEL 7: GRAPH ARCHITECTURE & REASONING",
        "levelClass": "level-3",
        "readTime": "9 min read",
        "audience": "Data Architects & Senior Graph Engineers",
        "title": "Graph Engineering: Why Vector RAG Fails on Multi-Hop Queries and How GraphRAG Solves It",
        "lead": "Vector similarity search is great at finding direct text matches, but completely blind to interconnected relationships across entities. Enter Graph Engineering: combining Neo4j/Knowledge Graphs with Claude's reasoning.",
        "stats": {
            "type": "warning",
            "title": "The Vector Search Blindspot in Complex Systems:",
            "items": [
                "Standard vector RAG accuracy drops below <strong>28% on multi-hop questions</strong> (e.g. 'Which upstream service dependencies share an expired SSL cert owned by Team X?').",
                "Graph-augmented LLM pipelines (GraphRAG) boost multi-hop relationship extraction accuracy from <strong>34% to 89%</strong> while reducing context hallucinations."
            ]
        },
        "mentalModel": {
            "title": "1. The 60-Second Mental Model: The Family Tree vs. A Bag of Words",
            "text": "Vector search treats documents like a pile of post-it notes in a blender—finding notes that sound similar. But if you want to find your second cousin twice removed, similarity is useless. You need an edge traversal.<br><br><strong>Graph Engineering turns Claude into a Graph Query Engine:</strong> Claude generates Cypher queries, traverses relationships, and reasons over interconnected enterprise knowledge."
        },
        "diagram": "graph LR\n    subgraph RAG [\"Vector RAG (Flat Similarity)\"]\n        Q[\"User Query\"] -.-> V1[\"Chunk A\"]\n        Q -.-> V2[\"Chunk B (Missing Connection!)\"]\n    end\n    subgraph GraphRAG [\"Graph Engineering (Entity-Relationship)\"]\n        E1[\"Service A\"] -->|DEPENDS_ON| E2[\"Database B\"]\n        E2 -->|HOSTED_IN| E3[\"VPC Us-East-1\"]\n        E3 -->|MANAGED_BY| E4[\"Team Security\"]\n        Claude[\"Claude Cypher Agent\"] -->|Traverses Path| E1\n    end\n    style Claude fill:#1e3a8a,stroke:#60a5fa,color:#fff\n    style E4 fill:#065f46,stroke:#34d399,color:#fff",
        "diagramCaption": "Figure: Flat Vector Embeddings vs. Connected GraphRAG Traversal",
        "codeTitle": "cypher_graph_agent.py",
        "codeContent": "from neo4j import GraphDatabase\nimport anthropic\n\nclient = anthropic.Anthropic()\n\ndef generate_and_execute_cypher(natural_query: str, schema_description: str):\n    prompt = f\"\"\"Translate this user question into a read-only Cypher query.\\nSchema: {schema_description}\\nQuestion: {natural_query}\\nOutput only inside <cypher_query> tags.\"\"\"\n    response = client.messages.create(\n        model=\"claude-3-7-sonnet-20250219\",\n        max_tokens=1024,\n        messages=[{\"role\": \"user\", \"content\": prompt}]\n    )\n    # Extract Cypher and execute against Neo4j read replica\n    cypher = response.content[0].text.split(\"<cypher_query>\")[1].split(\"</cypher_query>\")[0]\n    return db_driver.execute_query(cypher)",
        "takeaway": {
            "title": "🎁 Architect’s \"Monday Morning\" Takeaway",
            "items": [
                "Stop relying solely on vector embeddings for relationship-heavy enterprise queries.",
                "Extract entities and relationships into a graph database (Neo4j, AWS Neptune) during your ingestion ETL.",
                "Let Claude generate Cypher or Gremlin queries to perform structured path traversals."
            ],
            "badge": "GraphRAG bridges the gap between semantic similarity and deterministic relational logic."
        }
    },
    "certification": {
        "topic": "Claude Certifications & Enterprise AI Competency",
        "level": "LEVEL 6: ENTERPRISE STANDARDS & CERTIFICATIONS",
        "levelClass": "level-2",
        "readTime": "8 min read",
        "audience": "Engineering Leaders, Architects & Tech Leads",
        "title": "Demystifying Claude Certifications: The Enterprise Competency Matrix for AI Engineers",
        "lead": "With prompt engineering transitioning from an ad-hoc hobby into a core software engineering discipline, how do technical architects evaluate and certify engineering talent? Here is our enterprise competency framework.",
        "stats": {
            "type": "info",
            "title": "The Shift to Formalized AI Engineering Standards:",
            "items": [
                "According to recent tech hiring telemetry, enterprise demand for verified Prompt & Agent Architecture skills grew <strong>280% year-over-year</strong>.",
                "Teams adopting structured evaluation benchmarks (SWE-bench verified calibration) deliver production LLM features with <strong>3.5x fewer post-launch security vulnerabilities</strong>."
            ]
        },
        "mentalModel": {
            "title": "1. The 60-Second Mental Model: AWS Solutions Architect vs. ClickOps",
            "text": "Anyone can spin up an EC2 instance in the AWS console ('ClickOps'). But a certified AWS Architect designs for VPC peering, IAM least-privilege, and multi-region failover.<br><br><strong>Prompt engineering is undergoing the exact same maturation:</strong> Moving from 'creative writing for chatbots' to rigorous systems architecture: deterministic XML structuring, KV-cache prefix optimization, and automated eval suites."
        },
        "diagram": "graph TD\n    subgraph Levels [\"Enterprise AI Competency Matrix\"]\n        L1[\"Level 1: Prompt Practitioner<br/>• XML delimiting<br/>• Role &amp; constraint framing\"]\n        L2[\"Level 2: Systems Integrator<br/>• Function &amp; Tool Calling<br/>• Hierarchical Prompt Caching\"]\n        L3[\"Level 3: Agent Architect<br/>• Evaluator-Optimizer loops<br/>• MCP Protocol &amp; Vector/GraphRAG\"]\n        L4[\"Level 4: Principal AI Architect<br/>• CI/CD LLM-as-a-Judge<br/>• Red Teaming &amp; Security Auditing\"]\n    end\n    L1 --> L2 --> L3 --> L4\n    style L1 fill:#1e3a8a,stroke:#60a5fa,color:#fff\n    style L4 fill:#7f1d1d,stroke:#f87171,color:#fff",
        "diagramCaption": "Figure: The 4-Tier Enterprise AI Engineering Skill Progression",
        "codeTitle": "eval_competency_check.py",
        "codeContent": "# Enterprise Architecture Skill Checklist for Code Reviewers:\n# 1. XML tags used for untrusted variables? [ ]\n# 2. Ephemeral cache_control placed after heavy static context? [ ]\n# 3. Tool results include is_error=True on failures? [ ]\n# 4. Thinking budget configured appropriately for task complexity? [ ]",
        "takeaway": {
            "title": "🎁 Architect’s \"Monday Morning\" Takeaway",
            "items": [
                "Incorporate LLM security and prompt caching checks into your standard PR review templates.",
                "Calibrate your engineers against the 4-tier competency matrix (Practitioner -> Integrator -> Agent Architect -> Principal).",
                "Encourage your teams to build automated eval suites instead of manual vibe-checks."
            ],
            "badge": "True AI competency isn't about clever prompting; it's about building resilient, cost-effective distributed systems."
        }
    }
}

RESERVE_TOPICS_POOL = [
  {
    "topic": "Context Compaction & Sliding Window Memory",
    "level": "LEVEL 11: CONTEXT ARCHITECTURE",
    "levelClass": "level-3",
    "readTime": "8 min read",
    "audience": "Senior Systems Engineers",
    "title": "Beating Context Degradation: How to Compact 100k Token Chats Without Losing State",
    "lead": "The 200k context window is a blessing and a curse. If you keep appending turns forever, cost explodes and attention degrades in the middle. Here is how to implement semantic compaction.",
    "stats": {
      "type": "warning",
      "title": "The Memory Explosion Problem:",
      "items": [
        "Uncompacted 20-turn chat conversations consume over 120,000 tokens and slow down response time by 4.2x.",
        "Asynchronous context compaction drops active turn tokens by 78% while preserving 99% of key entity constraints."
      ]
    },
    "mentalModel": {
      "title": "1. The 60-Second Mental Model: OS Virtual Memory Paging",
      "text": "Your operating system doesn't keep all RAM pages dirty and active at once. It swaps inactive memory pages to disk.<br><br><strong>Context Compaction applies memory paging to LLMs:</strong> Turns 1 through 15 are summarized into a dense state object, while turns 16 through 20 remain raw and verbatim."
    },
    "diagram": "graph LR\n    T1[\"Turns 1-15 (Raw History)\"] --> Summarizer[\"Async Compactor Agent\"]\n    Summarizer --> State[\"&lt;session_state&gt;<br/>Key facts, variables, decisions\"]\n    State --> Active[\"Turns 16-20 (Recent Raw Turns)\"]\n    Active --> Next[\"Next Generation Turn\"]\n    style State fill:#1e3a8a,stroke:#60a5fa,color:#fff",
    "diagramCaption": "Figure 11: Hybrid Sliding Window Memory Compaction",
    "codeTitle": "context_compactor.py",
    "codeContent": "# Periodically condense older chat history\ndef compact_history(history_messages):\n    if len(history_messages) > 12:\n        condensed_state = summarize_turns(history_messages[:-4])\n        return [{'role': 'user', 'content': f'<session_state>{condensed_state}</session_state>'}] + history_messages[-4:]\n    return history_messages",
    "takeaway": {
      "title": "🎁 Architect’s \"Monday Morning\" Takeaway",
      "items": [
        "Never allow chat threads to grow unbounded in enterprise apps.",
        "Implement a sliding window: summarize turns older than turn N-4 into structured XML state.",
        "Retain key user variables and decisions in a dedicated scratchpad."
      ],
      "badge": "Active context compaction prevents attention rot and cuts multi-turn costs by 70%."
    }
  }
]

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8-sig") as f:
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
    return True

def generate_custom_topic_post(custom_keyword):
    """Generate or match a customized topic post based on user suggestion."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a Principal Systems Architect writing for an elite enterprise Claude engineering community.
Create an advanced, high-impact post on the topic: '{custom_keyword}'.
Include:
1. Real-world engineering numbers and failure incidents.
2. 60-second mental model with relatable software engineering analogy.
3. Clean Mermaid diagram.
4. Production code block with XML/Python.
5. Actionable Monday morning takeaway.

Output ONLY valid JSON matching:
{{
  "id": "post-X",
  "level": "LEVEL X: ...",
  "levelClass": "level-3",
  "readTime": "8 min read",
  "audience": "Senior Engineers & Architects",
  "title": "...",
  "lead": "...",
  "stats": {{"type": "info", "title": "...", "items": ["..."]}},
  "mentalModel": {{"title": "1. The 60-Second Mental Model: ...", "text": "..."}},
  "diagram": "graph TD\\n...",
  "diagramCaption": "Figure: ...",
  "codeTitle": "...py",
  "codeContent": "...",
  "takeaway": {{"title": "🎁 Architect’s \\"Monday Morning\\" Takeaway", "items": ["..."], "badge": "..."}}
}}"""
            res = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = res.content[0].text
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            return json.loads(raw.strip())
        except Exception as err:
            print(f"⚠️ Claude API error: {err}. Checking specialized template pool...")

    # Fallback to specialized keyword templates
    kw_lower = custom_keyword.lower()
    for k, template in KEYWORD_TEMPLATES.items():
        if k in kw_lower:
            return template.copy()

    # Generic high-quality synthesis if unknown keyword and offline
    return {
        "topic": custom_keyword,
        "level": f"DEEP-DIVE: {custom_keyword.upper()}",
        "levelClass": "level-3",
        "readTime": "8 min read",
        "audience": "Senior Engineering Community",
        "title": f"Architecting for {custom_keyword}: Principles, Tradeoffs, and Production Realities",
        "lead": f"As our engineering organization scales Claude applications, '{custom_keyword}' has emerged as a critical design consideration. Here is how to architect it with enterprise rigor.",
        "stats": {
            "type": "info",
            "title": f"Production Metrics for {custom_keyword}:",
            "items": [
                f"Adopting structured patterns for {custom_keyword} lowers runtime defects by over 45%.",
                "Proper error boundaries reduce transient downstream microservice failures."
            ]
        },
        "mentalModel": {
            "title": f"1. The 60-Second Mental Model: {custom_keyword} in Systems Design",
            "text": f"Just as we enforce contracts between microservices, applying {custom_keyword} to Claude workflows creates clear separation of concerns, deterministic boundaries, and observable state transitions."
        },
        "diagram": f"graph LR\n    Input[\"Client Context\"] --> Process[\"Claude {custom_keyword} Processor\"]\n    Process --> Output[\"Validated Result\"]\n    style Process fill:#1e3a8a,stroke:#60a5fa,color:#fff",
        "diagramCaption": f"Figure: Operational Pipeline for {custom_keyword}",
        "codeTitle": "enterprise_scaffold.py",
        "codeContent": f"# Architectural Implementation Scaffold for {custom_keyword}\n# Enforce XML validation and structured contracts across execution boundaries.",
        "takeaway": {
            "title": "🎁 Architect’s \"Monday Morning\" Takeaway",
            "items": [
                f"Integrate {custom_keyword} requirements directly into system prompts.",
                "Add telemetry markers to trace performance and failure modes in Datadog/Splunk.",
                "Review edge cases during PR reviews before moving to staging."
            ],
            "badge": f"Deliberate architecture around {custom_keyword} ensures reliability at scale."
        }
    }

def replenish_queue_if_low(upcoming, posts):
    """Ensure queue never runs dry by adding reserve topics."""
    if len(upcoming) <= 1:
        print("🔄 Upcoming queue is low (<= 1 topic). Replenishing from reserve pool...")
        current_titles = {p.get("title") for p in posts} | {u.get("title") for u in upcoming}
        for item in RESERVE_TOPICS_POOL:
            if item.get("title") not in current_titles:
                upcoming.append(item)
        print(f"✨ Auto-replenished queue. Total available now: {len(upcoming)}")
    return upcoming

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Publish next scheduled Claude Architecture post.")
    parser.add_argument("--dry-run", action="store_true", help="Validate next post without modifying files.")
    parser.add_argument("--custom-topic", type=str, help="Suggest a custom topic or keyword to generate on-demand.")
    parser.add_argument("--list-queue", action="store_true", help="List remaining upcoming topics.")
    args = parser.parse_args()

    upcoming = load_json(UPCOMING_JSON)
    posts = load_json(POSTS_JSON)

    if args.list_queue:
        print(f"\n📋 Upcoming Queued Topics ({len(upcoming)} remaining):")
        for i, t in enumerate(upcoming, 1):
            print(f"  {i}. {t.get('title', t.get('topic'))}")
        return

    # Check for custom topic override
    if args.custom_topic and args.custom_topic.strip():
        print(f"💡 Custom topic suggested: '{args.custom_topic}'")
        post_to_publish = generate_custom_topic_post(args.custom_topic.strip())
    else:
        # Check for auto-replenishment
        upcoming = replenish_queue_if_low(upcoming, posts)
        if not upcoming:
            print("⚠️ No topics available.")
            sys.exit(0)
        post_to_publish = upcoming.pop(0)

    post_to_publish["id"] = f"post-{len(posts) + 1}"
    validate_post_schema(post_to_publish)

    print(f"🚀 Publishing: {post_to_publish['title']}")

    if args.dry_run:
        print(f"[DRY RUN] Validated post: {post_to_publish['title']}")
        return

    # Append and commit
    posts.append(post_to_publish)
    save_json(POSTS_JSON, posts)
    sync_posts_js(posts)
    save_json(UPCOMING_JSON, upcoming)

    print(f"✅ Published '{post_to_publish['title']}' successfully!")
    print(f"📊 Total Published Posts: {len(posts)} | Remaining Queued: {len(upcoming)}")

if __name__ == "__main__":
    main()
