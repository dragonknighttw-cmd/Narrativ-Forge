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
