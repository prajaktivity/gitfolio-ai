import anthropic
import json
from typing import Dict, Any, List
from app.core.config import settings


client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _build_profile_context(profile_data: Dict[str, Any]) -> str:
    top_langs = ", ".join(
        f"{l['name']} ({l['percentage']}%)" for l in profile_data.get("top_languages", [])[:5]
    )
    top_repos = "\n".join(
        f"  - {r['name']}: {r.get('description', 'No description')} | ⭐{r['stars']} | {r.get('language', 'N/A')}"
        for r in profile_data.get("top_repos", [])[:6]
    )
    skills = ", ".join(profile_data.get("skill_tags", [])[:15])
    contrib = profile_data.get("contribution_data", {})

    return f"""
GitHub Profile Data:
- Username: {profile_data['github_username']}
- Public Repos: {profile_data['public_repos']}
- Total Stars: {profile_data['total_stars']}
- Total Forks: {profile_data['total_forks']}
- Followers: {profile_data['followers']}
- Total Commits (last year): {profile_data['total_commits']}
- PRs Opened: {contrib.get('total_prs', 0)}
- Issues Opened: {contrib.get('total_issues', 0)}
- Account Age: {profile_data['account_age_days']} days
- Top Languages: {top_langs}
- Detected Skills/Technologies: {skills}
- Top Repositories:
{top_repos}
"""


async def generate_profile_analysis(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI analysis of a GitHub profile."""
    context = _build_profile_context(profile_data)

    prompt = f"""You are an expert technical recruiter and developer career coach. 
Analyze this GitHub profile and provide a structured assessment.

{context}

Return ONLY valid JSON with this exact structure (no markdown, no explanation):
{{
  "headline": "One-line professional headline (max 80 chars, specific to their stack)",
  "summary": "3-4 sentence professional narrative about this developer. Be specific about what they build, their strengths, and their experience level. Write in third person.",
  "career_level": "one of: Student, Junior Developer, Mid-level Developer, Senior Developer, Full-stack Developer",
  "strengths": ["strength 1", "strength 2", "strength 3", "strength 4"],
  "improvement_areas": ["specific actionable improvement 1", "improvement 2", "improvement 3"],
  "recommended_roles": ["role 1", "role 2", "role 3"],
  "scores": {{
    "overall": 0-100,
    "activity": 0-100,
    "quality": 0-100,
    "diversity": 0-100,
    "impact": 0-100
  }},
  "score_explanations": {{
    "activity": "one sentence explaining activity score",
    "quality": "one sentence explaining quality score",
    "diversity": "one sentence explaining diversity score",
    "impact": "one sentence explaining impact score"
  }}
}}

Scoring guidance:
- activity: frequency of commits, PRs, issues, consistency
- quality: repo documentation, descriptions, organized code structure
- diversity: variety of technologies, languages, project types
- impact: stars, forks, followers, community engagement
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()
    # Strip markdown code fences if present
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
    
    return json.loads(response_text.strip())


async def generate_job_match(
    profile_data: Dict[str, Any],
    analysis_data: Dict[str, Any],
    job_description: str,
) -> Dict[str, Any]:
    """Analyze how well a developer matches a job description."""
    context = _build_profile_context(profile_data)
    
    prompt = f"""You are a technical recruiter evaluating a candidate for a job.

Candidate GitHub Profile:
{context}

AI Profile Summary: {analysis_data.get('summary', '')}
Detected Skills: {', '.join(profile_data.get('skill_tags', []))}
Career Level: {analysis_data.get('career_level', '')}

Job Description:
{job_description[:3000]}

Return ONLY valid JSON:
{{
  "match_score": 0-100,
  "feedback": "2-3 sentences on overall fit for this role",
  "matching_skills": ["skill that matches", "another matching skill"],
  "missing_skills": ["skill gap 1", "skill gap 2"],
  "recommendation": "Strong Match / Good Potential / Skill Gap / Not Recommended",
  "tips": ["specific tip to improve match 1", "tip 2"]
}}
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]

    return json.loads(response_text.strip())


async def generate_profile_slug(username: str, headline: str) -> str:
    """Generate a clean URL slug from username."""
    import re
    base = f"{username}-{headline[:30]}".lower()
    slug = re.sub(r"[^a-z0-9-]", "-", base)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:80]
