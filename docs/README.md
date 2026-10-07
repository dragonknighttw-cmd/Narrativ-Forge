# Narrativ Forge Documentation

This directory contains supporting documentation for the Narrativ Forge master roadmap and current implementation.

## Source hierarchy

1. `roadmap.md` — **single master roadmap and source of truth for planned work, execution order, future capabilities, status, and release gates**.
2. `README.md` — current implementation, deployment state, verified blockers, and operational summary.
3. `docs/21-master-completion-matrix.md` — detailed audit/evidence matrix derived from the roadmap; it is not a competing roadmap.
4. `docs/*.md` — supporting specifications that retain detail which is useful outside the master roadmap.
5. `infra/*.md` — infrastructure provisioning and operational runbooks.
6. `mobile/README.md` — reserved mobile workspace note.

## Supporting documents

- [01-product.md](./01-product.md) — product identity, boundaries, and output.
- [02-stack.md](./02-stack.md) — stack and worker/runtime strategy.
- [03-architecture.md](./03-architecture.md) — architecture and domain responsibilities.
- [04-current-vs-target.md](./04-current-vs-target.md) — detailed current-vs-target reconciliation.
- [05-execution-roadmap.md](./05-execution-roadmap.md) — **legacy supporting roadmap; the root `roadmap.md` is authoritative**.
- [06-future-reserve.md](./06-future-reserve.md) — **legacy reserve detail; future work is now scheduled in the root roadmap**.
- [07-ui-design.md](./07-ui-design.md) — UI/design-system target and implementation notes.
- [08-manual-mode.md](./08-manual-mode.md) — manual validation and exit gate.
- [09-auto-production-expansion.md](./09-auto-production-expansion.md) — expanded Auto Production specification.
- [10-runtime-and-storage-lifecycle-plan.md](./10-runtime-and-storage-lifecycle-plan.md) — runtime/storage lifecycle detail.
- [11-release-readiness-checklist.md](./11-release-readiness-checklist.md) — release-readiness detail.
- [21-master-completion-matrix.md](./21-master-completion-matrix.md) — detailed completion/evidence matrix.
- [production-readiness.md](./production-readiness.md) — legacy production-readiness detail; reconcile before removal.

## Governance

Do not create another master roadmap.

When a requirement is discovered in a supporting document:
1. Add or reconcile it in `roadmap.md`.
2. Keep only implementation-specific detail in the supporting document.
3. Update links/status references when the requirement changes.
4. Remove obsolete or duplicated roadmap content only after reconciliation.

The roadmap's release rule remains: **code existing is not production evidence**. Real credentials, real media, worker execution, external integrations, backups/restores, security evidence, accessibility, legal review, and other live gates must be verified explicitly.
