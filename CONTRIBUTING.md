# Contributing to Freecorner

Thanks for joining the project! This document outlines the recommended workflow, commit conventions, and PR expectations for a small team.

Branching and workflow
- We follow a lightweight Gitflow-style workflow:
  - `main` — production-ready code only. Every commit on `main` should be a tagged release or hotfix.
  - `develop` — integration branch where completed features are merged for the next release.
  - `feature/<short-description>` — feature branches created from `develop`.
  - `release/<version>` — optional release preparation branches created from `develop`.
  - `hotfix/<short-description>` — urgent fixes created from `main` and merged back into `main` and `develop`.

Branch naming examples
- `feature/login-ui`
- `fix/camera-config`
- `hotfix/urgent-memory-leak`

Commit messages
- Use Conventional Commits for clarity. Examples:
  - `feat: add seat detection model loader`
  - `fix: correct camera index handling`
  - `chore: update dependencies`

Pull request process
- Open a PR from your feature branch into `develop` (unless it's an urgent hotfix targeting `main`).
- Include a short description and link any related issue.
- At least one approving review is required before merge.
- Use squash-and-merge for small features; preserve history for larger ones if desired.

Code style and tests
- Follow the existing project's style. Add or update unit tests for any new logic when practical.
- Run linters and quick smoke tests locally before opening a PR.

Onboarding notes for the team
- Sanjeetha, Moksha and you should each create a GitHub account (if not present) and be added as collaborators to the repository; I'll push once the remote exists.
