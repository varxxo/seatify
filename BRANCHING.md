# Branching Strategy for Freecorner

We use a simple Gitflow-inspired branching model suitable for a small team:

- `main` — production branch. Only merged code that is released or hotfixed should land here.
- `develop` — integration branch for ongoing work. All feature branches are merged here.
- `feature/*` — short-lived branches for individual features or tasks, branched from `develop`.
- `hotfix/*` — branches for urgent fixes off `main` and merged into both `main` and `develop`.
- `release/*` — optional branches created from `develop` to prepare a release.

Workflow
1. Create a `feature/<name>` branch from `develop` for your task.
2. Work and push your feature branch to remote.
3. Open a PR into `develop`, request reviews, and merge after approval.
4. When `develop` is stable, create `release/<version>` or merge into `main` (depending on your release cadence).

Tips
- Keep feature branches small and focused.
- Rebase locally to keep history tidy, but avoid rewriting shared branch history.
- Label PRs clearly and link related issues.
