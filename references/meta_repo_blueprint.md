# Meta Repository Blueprint

## Standard Repository Set

Use four repositories when the owner has multiple kinds of work:

| Repository | Role |
|---|---|
| `<owner>-project-atlas` | Top-level categorized map of public repositories, with forks at the tail. |
| `<owner>-release-hub` | Latest releases, version tags, artifact entry points, and release-ready projects. |
| `<owner>-pages-hub` | Visual gallery of GitHub Pages sites, docs, demos, and live surfaces. |
| `<owner>-skills-hub` | Codex skills, workflow skills, prompt recipes, and agent operating procedures. |

Use one atlas repository when the owner has fewer than 15 repositories.

## Automation Policy

- Default schedule: daily.
- Always include `workflow_dispatch`.
- Default visibility: public metadata only.
- Private coverage requires a private meta repository and explicit token secret.
- Generated data should live in `data/*.json`.
- GitHub Pages sites should publish from `docs/` via `actions/deploy-pages`.

## Category Rules

Keep classification explainable and easy to edit:

- Forks are grouped at the end.
- Pages-enabled repositories can be promoted to the Pages hub.
- Repositories with latest releases can be promoted to the Release hub.
- Names or descriptions containing `skill`, `Codex skill`, `plugin`, or workflow-skill language belong in the Skills hub.
- AI, agent, RAG, LLM, Codex, Claude, GPT, and similar terms belong in AI/agent categories.
- Older public forks should remain visible but should not crowd the owner-created projects.

## README Guidance

Apply README design rules:

- First screen states owner, scope, and live links.
- Use compact badges for counts and update cadence.
- Use tables for scan-heavy repository lists.
- Use OpenGraph previews or real screenshots for pages/gallery repos.
- Do not claim private coverage in a public README.
