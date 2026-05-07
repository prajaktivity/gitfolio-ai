from jinja2 import Environment, BaseLoader
from typing import Dict, Any
import os

PDF_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Inter', sans-serif; color: #1a1a2e; background: white; font-size: 10pt; }
  
  .header { background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%); color: white; padding: 32px 40px; }
  .header-top { display: flex; align-items: center; gap: 20px; margin-bottom: 16px; }
  .avatar { width: 60px; height: 60px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.3); }
  .name { font-size: 22pt; font-weight: 700; letter-spacing: -0.5px; }
  .username { font-size: 11pt; color: rgba(255,255,255,0.6); margin-top: 2px; }
  .headline { font-size: 12pt; color: rgba(255,255,255,0.85); margin-top: 8px; }
  .career-badge { display: inline-block; background: rgba(99,102,241,0.3); color: #a5b4fc; padding: 4px 12px; border-radius: 20px; font-size: 9pt; margin-top: 8px; border: 1px solid rgba(99,102,241,0.4); }
  
  .content { padding: 28px 40px; }
  
  .section { margin-bottom: 24px; }
  .section-title { font-size: 9pt; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #6366f1; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #e5e7eb; }
  
  .summary { font-size: 10.5pt; line-height: 1.7; color: #374151; }
  
  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
  .stat-card { background: #f9fafb; border-radius: 8px; padding: 12px; text-align: center; border: 1px solid #f3f4f6; }
  .stat-num { font-size: 18pt; font-weight: 700; color: #1a1a2e; }
  .stat-label { font-size: 8pt; color: #6b7280; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }
  
  .scores-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .score-item { display: flex; align-items: center; gap: 10px; }
  .score-label { font-size: 9.5pt; color: #374151; width: 80px; flex-shrink: 0; }
  .score-bar-bg { flex: 1; height: 6px; background: #e5e7eb; border-radius: 3px; }
  .score-bar { height: 6px; background: linear-gradient(90deg, #6366f1, #8b5cf6); border-radius: 3px; }
  .score-val { font-size: 9.5pt; font-weight: 600; width: 30px; text-align: right; color: #4f46e5; }
  
  .lang-grid { display: flex; flex-wrap: wrap; gap: 8px; }
  .lang-tag { display: flex; align-items: center; gap: 5px; background: #f9fafb; border: 1px solid #e5e7eb; padding: 4px 10px; border-radius: 6px; font-size: 9pt; }
  .lang-dot { width: 8px; height: 8px; border-radius: 50%; }
  
  .skills-grid { display: flex; flex-wrap: wrap; gap: 6px; }
  .skill-tag { background: #ede9fe; color: #5b21b6; padding: 3px 10px; border-radius: 20px; font-size: 8.5pt; font-weight: 500; }
  
  .repos-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .repo-card { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; }
  .repo-name { font-size: 10pt; font-weight: 600; color: #1a1a2e; }
  .repo-desc { font-size: 8.5pt; color: #6b7280; margin-top: 4px; line-height: 1.4; }
  .repo-meta { display: flex; gap: 10px; margin-top: 8px; font-size: 8pt; color: #9ca3af; }
  
  .list-items { display: flex; flex-direction: column; gap: 6px; }
  .list-item { display: flex; align-items: flex-start; gap: 8px; font-size: 9.5pt; color: #374151; line-height: 1.5; }
  .list-dot-green { color: #10b981; font-size: 12pt; line-height: 1; }
  .list-dot-amber { color: #f59e0b; font-size: 12pt; line-height: 1; }
  
  .roles-grid { display: flex; flex-wrap: wrap; gap: 8px; }
  .role-tag { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; padding: 4px 12px; border-radius: 20px; font-size: 9pt; font-weight: 500; }
  
  .footer { margin-top: 28px; padding: 16px 40px; background: #f9fafb; border-top: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }
  .footer-brand { font-size: 8.5pt; color: #9ca3af; }
  .footer-brand span { color: #6366f1; font-weight: 600; }
  .footer-date { font-size: 8pt; color: #9ca3af; }
</style>
</head>
<body>

<div class="header">
  <div class="header-top">
    {% if avatar_url %}
    <img class="avatar" src="{{ avatar_url }}" />
    {% endif %}
    <div>
      <div class="name">{{ name or github_username }}</div>
      <div class="username">@{{ github_username }}</div>
    </div>
  </div>
  {% if headline %}<div class="headline">{{ headline }}</div>{% endif %}
  {% if career_level %}<div><span class="career-badge">{{ career_level }}</span></div>{% endif %}
</div>

<div class="content">

  {% if summary %}
  <div class="section">
    <div class="section-title">About</div>
    <div class="summary">{{ summary }}</div>
  </div>
  {% endif %}

  <div class="section">
    <div class="section-title">GitHub Stats</div>
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-num">{{ public_repos }}</div><div class="stat-label">Repos</div></div>
      <div class="stat-card"><div class="stat-num">{{ total_stars }}</div><div class="stat-label">Stars</div></div>
      <div class="stat-card"><div class="stat-num">{{ total_commits }}</div><div class="stat-label">Commits</div></div>
      <div class="stat-card"><div class="stat-num">{{ followers }}</div><div class="stat-label">Followers</div></div>
    </div>
  </div>

  {% if scores %}
  <div class="section">
    <div class="section-title">Profile Scores</div>
    <div class="scores-grid">
      {% for score_name, score_val in scores.items() %}
      <div class="score-item">
        <div class="score-label">{{ score_name.title() }}</div>
        <div class="score-bar-bg"><div class="score-bar" style="width: {{ score_val }}%"></div></div>
        <div class="score-val">{{ score_val|int }}</div>
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  {% if top_languages %}
  <div class="section">
    <div class="section-title">Languages</div>
    <div class="lang-grid">
      {% for lang in top_languages[:6] %}
      <div class="lang-tag">
        <div class="lang-dot" style="background: {{ lang.color }};"></div>
        {{ lang.name }} {{ lang.percentage }}%
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  {% if skill_tags %}
  <div class="section">
    <div class="section-title">Skills & Technologies</div>
    <div class="skills-grid">
      {% for skill in skill_tags[:16] %}
      <span class="skill-tag">{{ skill }}</span>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  {% if top_repos %}
  <div class="section">
    <div class="section-title">Featured Repositories</div>
    <div class="repos-grid">
      {% for repo in top_repos[:4] %}
      <div class="repo-card">
        <div class="repo-name">{{ repo.name }}</div>
        {% if repo.description %}
        <div class="repo-desc">{{ repo.description[:100] }}</div>
        {% endif %}
        <div class="repo-meta">
          <span>⭐ {{ repo.stars }}</span>
          <span>🍴 {{ repo.forks }}</span>
          {% if repo.language %}<span>{{ repo.language }}</span>{% endif %}
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  {% if strengths %}
  <div class="section">
    <div class="section-title">Strengths</div>
    <div class="list-items">
      {% for s in strengths %}
      <div class="list-item"><span class="list-dot-green">●</span> {{ s }}</div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  {% if recommended_roles %}
  <div class="section">
    <div class="section-title">Recommended Roles</div>
    <div class="roles-grid">
      {% for role in recommended_roles %}
      <span class="role-tag">{{ role }}</span>
      {% endfor %}
    </div>
  </div>
  {% endif %}

</div>

<div class="footer">
  <div class="footer-brand">Generated by <span>GitFolio</span> · gitfolio.app/@{{ github_username }}</div>
  <div class="footer-date">{{ generated_date }}</div>
</div>

</body>
</html>
"""


async def generate_pdf(data: Dict[str, Any]) -> bytes:
    """Render profile HTML and convert to PDF."""
    try:
        from weasyprint import HTML
    except ImportError:
        raise RuntimeError("WeasyPrint is not installed. Run: pip install weasyprint")

    from datetime import datetime
    env = Environment(loader=BaseLoader())
    template = env.from_string(PDF_TEMPLATE)

    scores = {
        "Activity": data.get("activity_score", 0),
        "Quality": data.get("quality_score", 0),
        "Diversity": data.get("diversity_score", 0),
        "Impact": data.get("impact_score", 0),
        "Overall": data.get("overall_score", 0),
    }

    html_content = template.render(
        github_username=data.get("github_username", ""),
        name=data.get("name"),
        avatar_url=data.get("avatar_url"),
        headline=data.get("headline"),
        summary=data.get("summary"),
        career_level=data.get("career_level"),
        public_repos=data.get("public_repos", 0),
        total_stars=data.get("total_stars", 0),
        total_commits=data.get("total_commits", 0),
        followers=data.get("followers", 0),
        scores=scores,
        top_languages=data.get("top_languages", []),
        skill_tags=data.get("skill_tags", []),
        top_repos=data.get("top_repos", []),
        strengths=data.get("strengths", []),
        recommended_roles=data.get("recommended_roles", []),
        generated_date=datetime.now().strftime("%B %d, %Y"),
    )

    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes
