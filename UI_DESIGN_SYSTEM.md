# Narrativ Forge — UI Design System

> Owner: Frontend maintainers  
> Update when: visual tokens, components, layouts, or accessibility rules change  
> Last Updated: 2026-10-08  
> Do NOT put here: product roadmap or live deployment status

## Stack

- Next.js 16.x line.
- React 19.x.
- TypeScript.
- lucide-react.
- Playwright.
- Native CSS custom properties and reusable React primitives.
- Inter + Noto Sans Myanmar.

## Tokens

Canvas: `#0b0d10`  
Surface: `#12161b`  
Elevated: `#181d23`  
Brand: `#d8ff4f`  
Success: `#63d38a`  
Warning: `#f2c14e`  
Danger: `#ff6b6b`  
Info: `#65b9ff`

Spacing: 4, 8, 12, 16, 24, 32, 48, 64.

Default card: 12px radius, 1px border, 20px padding.

## Layout

Desktop application shell:
- ~250px sidebar.
- ~84px topbar.
- Main content max-width ~1400px.

Responsive behavior must preserve task hierarchy rather than merely shrink desktop layouts.

Interactive targets: minimum 44px.

## Components

The reusable foundation includes layout, forms, feedback/status, accessibility helpers, data/navigation overlays, and media/workflow primitives. The target library is 33 components; target count is not completion evidence.

Required states where applicable:
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

## Accessibility

- Visible keyboard focus.
- Semantic labels and roles.
- Screen-reader support for interactive controls.
- 44px touch targets.
- Reduced-motion support.
- Burmese typography/readability review.
- Automated + manual WCAG review remains a release gate.

## Screen inventory

Historical baseline:
- 23 original MVP screens.
- 26-screen design-system baseline.
- Expanded Auto Production candidate surfaces.

These counts must not be conflated. The final inventory must distinguish standalone routes from tabs/panels and publish one deduplicated baseline.

## Implementation status

Design-token and reusable primitive foundations are implemented. Full 33-component adoption, screen-by-screen state coverage, responsive audit, and WCAG audit remain VERIFY/TODO.

## Construction rules

Prefer existing primitives over one-off controls. Preserve semantic tokens. Do not introduce Tailwind/shadcn/MUI/Chakra as a parallel runtime system without an explicit architecture decision. Keep loading/error/empty/permission states first-class.
