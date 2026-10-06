# Narrativ Forge Docs

Reconciled documentation for implementation, target roadmap, production-readiness state, operations, and UI system.

## Source hierarchy
1. `roadmap.md` — desired product / master target.
2. `README.md` — actual repository implementation and deployment state.
3. `web-platform/docs/` — implementation-specific technical/runbook docs.
4. `docs/` — reconciled target/current/remaining documentation.

## Documents
- [01-product.md](./01-product.md)
- [02-stack.md](./02-stack.md)
- [03-architecture.md](./03-architecture.md)
- [04-current-vs-target.md](./04-current-vs-target.md)
- [05-execution-roadmap.md](./05-execution-roadmap.md)
- [06-future-reserve.md](./06-future-reserve.md)
- [07-ui-design.md](./07-ui-design.md)
- [08-manual-mode.md](./08-manual-mode.md)
- [09-auto-production-expansion.md](./09-auto-production-expansion.md)
- [10-runtime-and-storage-lifecycle-plan.md](./10-runtime-and-storage-lifecycle-plan.md)

## Operational source of truth

`docs/10-runtime-and-storage-lifecycle-plan.md` is the single authoritative plan for:

- Local PC worker deployment
- Future paid worker migration
- Storage / space cleanup and retention

Do not create competing Local Worker or Storage master plans.

**Rule:** code existing is not enough for production Done; real integration/runtime/security/DR verification must pass.

## Reconciliation rule

The Add-On requirements are part of the target plan. Their detailed specification lives in 09; 04 and 05 classify and schedule what is actually remaining.

The runtime/storage plan in 10 does not replace product, architecture, or feature requirements. It defines how processing infrastructure can move from free local compute to paid compute later without an application rewrite.

- **11-release-readiness-checklist.md** — Phase 8 production hardening and Phase 9 release-candidate / production-ready gates.
