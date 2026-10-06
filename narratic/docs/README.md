# Narrativ Forge Documentation

> Documentation map for the implementation, target roadmap, and production-readiness state.

**Source hierarchy**
1. `roadmap.md` — product target / desired end state.
2. `README.md` — actual repository implementation and deployment state.
3. `web-platform/docs/` — implementation-specific architecture and operational runbooks.
4. `narratic/docs/` — reconciled project documentation: target vs current vs remaining work.

## Documents

| File | Purpose |
|---|---|
| [01-product.md](./01-product.md) | Product identity, boundaries, workflow, final definition |
| [02-stack.md](./02-stack.md) | Tools, providers, constraints, and selected stack |
| [03-manual-mode.md](./03-manual-mode.md) | Manual production workflow and validation gate |
| [04-auto-architecture.md](./04-auto-architecture.md) | Auto-mode architecture, responsibilities, status flow |
| [05-data-and-versioning.md](./05-data-and-versioning.md) | Data model, versioning, selective regeneration |
| [06-ui.md](./06-ui.md) | Screens, design system, components, UI states |
| [07-quality-security-export.md](./07-quality-security-export.md) | Quality gates, security, Drive export rules |
| [08-current-vs-target.md](./08-current-vs-target.md) | Reconciled current implementation vs roadmap target |
| [09-execution-roadmap.md](./09-execution-roadmap.md) | What is done, what remains, and execution order |
| [10-future-reserve.md](./10-future-reserve.md) | Explicitly deferred / reserve technologies and features |

## Current reading order

`08-current-vs-target.md` → `09-execution-roadmap.md` → relevant domain document.

## Rule

Do not mark a target item complete merely because code exists. A production item becomes **Done** only after the required real integration, test, security, or operational verification has passed.
