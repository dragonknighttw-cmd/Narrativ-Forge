# UI Design System & Components

Target UI system for Narrativ Forge. This document describes the intended design language and screen/component coverage; it is not by itself proof that every screen is production-complete.

## Design tokens

### Colors
- Primary: Blue
- Success: Green
- Warning: Yellow
- Error: Red

### Typography
- Inter
- Noto Sans Myanmar

### Spacing
- 4
- 8
- 12
- 16
- 24
- 32
- 48
- 64

## Screen coverage

Target: **26 screens**

| Area | Count |
|---|---:|
| Auth | 2 |
| Dashboard | 1 |
| Content | 5 |
| Production | 6 |
| Processing | 1 |
| Review | 2 |
| Export | 2 |
| Intelligence | 4 |
| System | 3 |
| **Total** | **26** |

## Component coverage

Target: **33 components**

| Group | Count |
|---|---:|
| Layout | 4 |
| Forms | 8 |
| Data | 6 |
| Media | 5 |
| Feedback | 5 |
| States | 5 |
| **Total** | **33** |

## Implementation rule

These counts are target coverage, not proof of completion. Applicable loading, empty, error, success, permission, responsive, and accessibility states must also be reviewed.


## Expanded Auto Production UI
The original 26-screen baseline is superseded as a provisional target by the requirements in 09. Candidate additions include Story Upload, Episode Split Review, SEO Optimization, Hook Library, Thumbnail Selection, A/B Test, Series Bible, Continuity Check, Trending Topics, Sound Design, Emotional Arc, Pacing Analysis, Cross-Platform Export, Series Calendar, Voice Profile, Music Library, Video Generation Queue, Provider Status, Watermark Check, and Batch Generation.

Before implementation, consolidate duplicate concepts into tabs/panels where appropriate and publish a new final screen count. Every new screen must support relevant loading, empty, error, success, permission, responsive, and accessibility states.


## Explicit remaining UI requirements

The Design System and Component Library are tracked as implementation work, not documentation-only work:

- **Design System — TODO/VERIFY:** Colors, Typography, Spacing, semantic states, responsive rules, and accessibility rules must be implemented in actual UI code and audited.
- **Component Library — TODO/VERIFY:** the **33-component target** must exist as reusable components/variants and cover applicable loading, empty, error, success, disabled, permission, responsive, keyboard, and screen-reader states.
- A documented target count is not proof of completion.


## Implementation Foundation

The frontend now has a semantic design-token layer and reusable accessible primitives in `components/ui-primitives.tsx`: Stack, Row, Card, Button, TextInput, Badge, and Alert. Global CSS includes focus-visible treatment, minimum 44px interactive targets for primitives, semantic tones, and reduced-motion handling. These are the base layer for the documented 33-component library; they do not replace the remaining component/state audit.
\n\n## Latest implementation foundation update — 2026-10-07\n\nThe reusable primitive layer now covers:\n- Layout: Stack, Row, Card\n- Forms: Button, TextInput, Select, Textarea, Checkbox, Switch\n- Feedback/status: Badge, Alert, Spinner, Progress, Skeleton, EmptyState, StatusDot\n- Accessibility helpers: VisuallyHidden, Tooltip\n- Data/navigation overlays: Table, Tabs, Tab, Modal, Divider\n\nThis is an expanded implementation foundation for the 33-component target. It is not a claim that all 33 production components are fully wired across every screen; screen-level state, responsive, permission, keyboard, and screen-reader audits remain required.

## Latest UI implementation audit — 2026-10-07

- Auto Mode now uses the shared accessible design-system primitives and the authenticated AppShell instead of page-local form/button/alert markup.
- The shared primitive layer remains the implementation foundation; full screen-by-screen 33-component adoption is still a release-track audit item.


---

# Canonical UI Implementation Specification — 2026-10-07

This file is the detailed UI/design reference. `README.md` summarizes the current state; `roadmap.md` owns requirements/status. This file must not become a second roadmap.

## 1. Actual frontend tooling

| Concern | Current implementation |
|---|---|
| Framework | Next.js 16.3.8 |
| UI runtime | React 19.1.0 |
| Language | TypeScript 5.7.3 |
| Icons | lucide-react 0.468.0 |
| Browser E2E | Playwright 1.63.0 |
| Styling | Native CSS + CSS custom properties |
| Fonts | Inter + Noto Sans Myanmar |
| Component base | `components/ui-primitives.tsx` |
| Utility styling framework | None declared |
| Design-system package | None; project-owned primitives/tokens |
| Figma/runtime dependency | None |

## 2. Visual direction

Narrativ Forge is a production workspace, not a consumer social feed.

- Dark-first interface.
- High information density without visual clutter.
- Acid/lime brand accent for primary actions and active workflow emphasis.
- Neutral dark surfaces for canvas, cards, elevated panels, and inputs.
- Semantic green/yellow/red/blue states for success/warning/error/info.
- Burmese text must remain legible at normal UI sizes; Noto Sans Myanmar is paired with Inter.

## 3. Canonical tokens

### Color

| Token | Value | Use |
|---|---|---|
| Canvas | `#0b0d10` | page background |
| Surface | `#12161b` | cards / panels |
| Elevated | `#181d23` | raised controls / KPI surfaces |
| Inset | `#090b0e` | input/inset background |
| Text primary | `#f2f4f7` | primary text |
| Text secondary | `#aab3bd` | secondary text |
| Text muted | `#7d8792` | supporting labels |
| Border | `#29313a` | default borders |
| Border strong | `#3a4550` | hover/focused structural borders |
| Brand | `#d8ff4f` | primary action / active indicator |
| Success | `#63d38a` | completed/safe |
| Warning | `#f2c14e` | caution / quota |
| Danger | `#ff6b6b` | blocking/error |
| Info | `#65b9ff` | informational state |

Legacy blue/green/yellow/red descriptions in older docs are semantic categories only; the actual implemented token values above are canonical.

### Typography

- Inter: Latin/UI text.
- Noto Sans Myanmar: Burmese content/UI.
- Weight range: 400, 500, 600, 700.
- Page title target: 22–28px.
- Section title target: 16–20px.
- Body target: 13–15px.
- Supporting metadata: 11–13px.
- Avoid excessively small Burmese text.

### Spacing

4px base scale:
`4, 8, 12, 16, 20, 24, 32, 40` with 48/64 available for larger layout spacing.

### Radius / elevation

- Small: 6px.
- Medium: 8px.
- Large: 12px.
- Extra large: 16px.
- Small shadow for normal cards; stronger shadow only for dialogs/overlays.
- Avoid decorative shadows on every element.

## 4. Layout system

### Desktop

- Persistent left sidebar: approximately 250px.
- Topbar: approximately 84px.
- Main content max-width: approximately 1400px.
- Content padding: approximately 34px.
- KPI/dashboard grids use 4 columns at wide desktop.
- Forms may use 2fr/1fr/1fr/action layouts where appropriate.
- Tables are horizontally scrollable rather than squeezed.

### Responsive

- ≤900px: sidebar narrows; 4-column grids collapse to 2.
- ≤800px: dense form grids collapse to 1 column.
- ≤760px: inline forms stack.
- ≤640px: sidebar hides, content/topbar padding reduces, KPI/grid collapses to 1.
- Every important workflow must remain usable with touch targets of at least 44px.

### AppShell

`Sidebar → Topbar → Main content`.

Primary navigation is grouped by production workflow. The current shell must not imply public social browsing.

## 5. Core component patterns

### Cards
Use cards for workflow summaries, KPI groups, review blocks, metadata, and production panels. Default: surface background + 1px border + 12px radius + 20px padding.

### KPI cards
Use for bounded production metrics only. Never show fake production numbers. Four-column desktop grid → two → one.

### Lists
Use for ideas, series, episodes, jobs, assets, and activity. Keep title/status/metadata visually separated and make the whole row actionable when appropriate.

### Tables
Use for analytics, logs, audit records, and dense structured data. Keep table headers clear, preserve horizontal scrolling, and never rely on color alone for state.

### Forms
Use explicit labels, 44px minimum controls, inline validation, error text, disabled/loading states, and keyboard-visible focus.

### Buttons
- Primary = brand/lime.
- Secondary = elevated neutral.
- Danger = explicit destructive/error action.
- Small = 36px, default = 44px minimum, large = 48px.
- Disabled state must remain legible.

### Badges / status
Use semantic tone plus text/icon; never encode meaning by color alone.

### Alerts
Use for blocking issues, quota warnings, integration failures, and success confirmations. Danger alerts use `role=alert` where appropriate.

### Tabs
Use for related subviews that should not become separate routes. Active state uses text + underline, not color alone.

### Modals
Use only for focused confirmation/edit flows. Dialog must have a labelled title, modal semantics, keyboard escape/close behavior, and focus management before release.

### Progress / loading / empty
- Spinner for short indeterminate work.
- Progress bar for known upload/processing progress.
- Skeleton for page/data loading.
- EmptyState must explain what is empty and the next useful action.

## 6. Workflow-specific screen rules

### Episode Detail
The workflow control center: status timeline, quick actions, current version, production blockers, next action.

### Script Studio
Editor-first layout: script body, version/history context, AI suggestions, save/conflict state.

### Subtitle Studio
Transcript/subtitle editor + timing context + validation warnings + preset controls. Burmese readability is the primary visual constraint.

### Processing Queue
Jobs grouped by status with progress, retry/failure reason, queue age, and worker/runtime state.

### Review Center / Approval
Video player + checklist + critical issue blockers + version context. Approval must be visually stronger than non-critical actions.

### Export
Approved output summary + export manifest + Drive connection/status + retry/recovery state. Never imply publication.

### Intelligence
Hook/SEO/thumbnail/analytics surfaces should show evidence and source metrics, not unsupported recommendations.

## 7. Required state matrix

Every relevant screen/control must be audited for:
- loading
- empty
- uploading
- processing
- completed
- failed
- retrying
- rejected
- offline/read-only
- permission denied
- session expired
- Drive disconnected
- Drive export failed
- storage warning
- unsupported file
- critical quality issue
- validation error
- disabled
- success confirmation

## 8. Accessibility

- WCAG 2.2 AA target.
- Keyboard navigation for all interactive controls.
- `:focus-visible` treatment is implemented with a high-contrast outline.
- Minimum 44px interactive target for shared primitives.
- Labels and semantic roles for inputs/dialogs/progress/tabs.
- Screen-reader-only helper available.
- Reduced-motion mode is implemented.
- Burmese content must not be truncated or made illegible by fixed heights.
- Color must not be the only signal for status.
- Full screen-reader and manual keyboard audit remains a release gate.

## 9. Current implementation vs target

Implemented foundation:
- Stack, Row, Card.
- Button, TextInput, Select, Textarea, Checkbox, Switch.
- Badge, Alert, Spinner, Progress, Skeleton, EmptyState, StatusDot.
- VisuallyHidden, Tooltip, Table, Tabs, Tab, Modal, Divider.
- Shared token layer and focus/reduced-motion rules.

Still audit/verify:
- 33-component target coverage across actual screens.
- All 23 original MVP screens.
- The 26-screen design-system baseline.
- Expanded Auto Production screens after deduplication.
- Permission/session/offline/integration states screen-by-screen.
- Responsive desktop/tablet/mobile behavior.
- WCAG 2.2 AA automated and manual evidence.
- Visual consistency and final polish.

