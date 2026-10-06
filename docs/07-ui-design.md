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
