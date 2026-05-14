<div align="center">

# Build Your Meta Repo Skill

Create an auto-updating GitHub "repo of repos": a project atlas, release hub, Pages gallery, and skills registry for any GitHub owner.

[Skill](./SKILL.md) · [Builder Script](./scripts/build_meta_repo.py) · [Blueprint](./references/meta_repo_blueprint.md)

![Skill](https://img.shields.io/badge/Codex%20Skill-ready-111111?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/Actions-auto_update-2D9CDB?style=for-the-badge)
![Privacy](https://img.shields.io/badge/privacy-public_by_default-6B8E23?style=for-the-badge)

</div>

## What It Builds

| Output Repository | Purpose |
|---|---|
| `<owner>-project-atlas` | Categorized top-level map of public repositories, with forks at the tail. |
| `<owner>-release-hub` | Latest GitHub releases and version entry points. |
| `<owner>-pages-hub` | Visual GitHub Pages gallery with deployable `docs/index.html`. |
| `<owner>-skills-hub` | Codex skills, workflow skills, and agent recipes. |

## Quick Start

```powershell
python scripts/build_meta_repo.py --owner Harzva --output D:\work\meta-repos
```

The generated repositories include:

- `scripts/update_meta.py`
- `.github/workflows/update-meta.yml`
- `data/repos.json` and `data/classified.json`
- GitHub Pages deployment workflow for atlas and pages hub
- README files designed as GitHub homepages

## Privacy Model

The default output is safe for public repositories: private repository names, descriptions, and local machine paths are not published.

For private coverage, keep the generated meta repository private and set:

```powershell
$env:META_INCLUDE_PRIVATE = "true"
$env:META_GITHUB_TOKEN = "<token>"
```

In GitHub Actions, store the token as `META_GITHUB_TOKEN`.

## Validation

```powershell
python -m py_compile scripts/build_meta_repo.py scripts/update_meta_template.py
```

The skill itself validates with Codex's skill validator.

## License

MIT
