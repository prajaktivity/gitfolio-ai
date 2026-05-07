import { notFound } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { Github, Star, GitFork, Users, Code, ExternalLink, Download } from "lucide-react";
import { Metadata } from "next";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getProfile(slug: string) {
  try {
    const res = await fetch(`${API_URL}/api/profile/public/${slug}`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const data = await getProfile(params.slug);
  if (!data) return { title: "Profile Not Found — GitFolio" };
  const { user, analysis } = data;
  return {
    title: `${user.name || user.github_username} — GitFolio`,
    description: analysis.headline || `${user.github_username}'s developer profile on GitFolio`,
    openGraph: {
      title: `${user.name || user.github_username} on GitFolio`,
      description: analysis.summary || analysis.headline,
      images: user.avatar_url ? [user.avatar_url] : [],
    },
  };
}

export default async function PublicProfilePage({ params }: { params: { slug: string } }) {
  const data = await getProfile(params.slug);
  if (!data) notFound();

  const { user, github_profile: profile, analysis } = data;

  return (
    <div className="min-h-screen bg-[#0a0a14]">
      {/* Top bar */}
      <nav className="border-b border-white/5 bg-[#0d0d1a]/80 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-6 h-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Github className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-sm font-semibold text-white">GitFolio</span>
          </Link>
          <Link
            href="/"
            className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg transition-colors"
          >
            Analyze My GitHub →
          </Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Profile Header */}
        <div className="flex flex-col md:flex-row items-start gap-6 mb-10">
          {user.avatar_url && (
            <Image
              src={user.avatar_url}
              alt={user.github_username}
              width={96}
              height={96}
              className="rounded-2xl border border-white/10 flex-shrink-0"
            />
          )}
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-white">{user.name || user.github_username}</h1>
              {analysis.career_level && (
                <span className="bg-indigo-500/15 text-indigo-300 text-xs px-2.5 py-1 rounded-full border border-indigo-500/20">
                  {analysis.career_level}
                </span>
              )}
            </div>
            <a
              href={`https://github.com/${user.github_username}`}
              target="_blank"
              className="text-gray-400 text-sm hover:text-white flex items-center gap-1 mb-4"
            >
              @{user.github_username}
              <ExternalLink className="w-3 h-3" />
            </a>
            {analysis.headline && (
              <p className="text-base text-gray-200 font-medium mb-3">{analysis.headline}</p>
            )}
            {analysis.summary && (
              <p className="text-sm text-gray-400 leading-relaxed max-w-2xl">{analysis.summary}</p>
            )}
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { icon: Code, label: "Repos", value: profile.public_repos },
            { icon: Star, label: "Stars", value: profile.total_stars },
            { icon: GitFork, label: "Commits", value: profile.total_commits },
            { icon: Users, label: "Followers", value: profile.followers },
          ].map((stat) => (
            <div key={stat.label} className="bg-white/3 border border-white/8 rounded-xl p-4 text-center">
              <div className="text-xl font-bold text-white">{stat.value.toLocaleString()}</div>
              <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Main content */}
          <div className="md:col-span-2 space-y-6">
            {/* Scores */}
            <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
              <h2 className="font-semibold text-white text-sm mb-5">Profile Scores</h2>
              <div className="space-y-3">
                {Object.entries({
                  Activity: analysis.scores.activity,
                  Quality: analysis.scores.quality,
                  Diversity: analysis.scores.diversity,
                  Impact: analysis.scores.impact,
                }).map(([label, score]) => (
                  <div key={label} className="flex items-center gap-4">
                    <span className="text-xs text-gray-400 w-16">{label}</span>
                    <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                        style={{ width: `${score}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-white w-8 text-right">{Math.round(score as number)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Languages */}
            {profile.top_languages?.length > 0 && (
              <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
                <h2 className="font-semibold text-white text-sm mb-4">Languages</h2>
                <div className="flex flex-wrap gap-2">
                  {profile.top_languages.slice(0, 8).map((lang: any) => (
                    <div key={lang.name} className="flex items-center gap-2 bg-white/5 border border-white/8 px-3 py-1.5 rounded-lg">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ background: lang.color }} />
                      <span className="text-xs text-gray-300">{lang.name}</span>
                      <span className="text-xs text-gray-500">{lang.percentage}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Top Repos */}
            {profile.top_repos?.length > 0 && (
              <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
                <h2 className="font-semibold text-white text-sm mb-4">Featured Repos</h2>
                <div className="grid md:grid-cols-2 gap-3">
                  {profile.top_repos.slice(0, 4).map((repo: any) => (
                    <a
                      key={repo.name}
                      href={repo.url}
                      target="_blank"
                      className="bg-white/3 border border-white/8 hover:border-indigo-500/30 rounded-xl p-4 transition-colors group"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-sm text-white group-hover:text-indigo-300 transition-colors">
                          {repo.name}
                        </span>
                        <ExternalLink className="w-3 h-3 text-gray-600 group-hover:text-gray-400" />
                      </div>
                      {repo.description && (
                        <p className="text-xs text-gray-500 mb-3 line-clamp-2">{repo.description}</p>
                      )}
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        {repo.language && (
                          <span className="flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full bg-indigo-400" />
                            {repo.language}
                          </span>
                        )}
                        <span>⭐ {repo.stars}</span>
                        <span>🍴 {repo.forks}</span>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Overall Score */}
            <div className="bg-white/3 border border-white/8 rounded-2xl p-6 text-center">
              <div className="text-5xl font-bold text-white mb-1">
                {Math.round(analysis.scores.overall)}
              </div>
              <div className="text-xs text-gray-500 mb-3">Overall Score</div>
              <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                  style={{ width: `${analysis.scores.overall}%` }}
                />
              </div>
            </div>

            {/* Skills */}
            {profile.skill_tags?.length > 0 && (
              <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
                <h2 className="font-semibold text-white text-sm mb-4">Skills</h2>
                <div className="flex flex-wrap gap-2">
                  {profile.skill_tags.slice(0, 16).map((skill: string) => (
                    <span key={skill} className="text-xs bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2.5 py-1 rounded-full">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Roles */}
            {analysis.recommended_roles?.length > 0 && (
              <div className="bg-white/3 border border-white/8 rounded-2xl p-6">
                <h2 className="font-semibold text-white text-sm mb-4">Best For</h2>
                <div className="space-y-2">
                  {analysis.recommended_roles.map((role: string) => (
                    <div key={role} className="text-xs text-emerald-300 bg-emerald-500/8 border border-emerald-500/15 px-3 py-2 rounded-lg">
                      {role}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* GitFolio CTA */}
            <div className="bg-gradient-to-b from-indigo-600/15 to-purple-600/10 border border-indigo-500/25 rounded-2xl p-5 text-center">
              <div className="text-xs text-gray-400 mb-3">Want your own GitFolio?</div>
              <Link
                href="/"
                className="block bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 rounded-xl text-sm font-medium transition-colors"
              >
                Analyze My GitHub — Free
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
