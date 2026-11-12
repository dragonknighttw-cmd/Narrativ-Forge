# Narrativ Forge — UI Design System

> Owner: Frontend maintainers  
> Update when: visual tokens, components, layouts, or accessibility rules change  
> Last Updated: 2026-11-12  
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

Canvas: `#090c10`  
Surface: `#111820`  
Elevated: `#17212b`  
Brand: `#d8ff4f`  
Success: `#63d38a`  
Warning: `#f2c14e`  
Danger: `#ff6b6b`  
Info: `#65b9ff`

Spacing: 4, 8, 12, 16, 24, 32, 48, 64.

Default card: 14px radius, 1px border, 20–22px padding. Hero panels use up to 20px radius.

## Layout

Desktop application shell:
- 276px desktop sidebar, collapsing into an accessible overlay drawer below 760px.
- ~82px sticky topbar with workspace context and page title.
- Main content max-width ~1500px with fluid horizontal padding.
- Navigation uses grouped icon links and an explicit active-route state.
- Dashboard uses a narrative hero, live API-backed episode/provider metrics, production stages, and clearly qualified integration status.

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

- Visible keyboard focus with high-contrast accent outline.
- Semantic labels and roles, including `aria-current` on the active navigation item.
- Mobile navigation supports Escape-to-close, explicit close controls, and focusable links.
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

Design-token and reusable primitive foundations are implemented. The shared application shell and dashboard received a responsive visual refresh on 2026-11-12: grouped icon navigation, active-route indication, mobile overlay navigation, consistent lime-accent dark studio tokens, and API-backed dashboard counts/provider priority. This is repository implementation (DONE); exact-SHA typecheck/build/E2E, live responsive browser QA, and full screen-by-screen WCAG audit remain VERIFY until fresh evidence is recorded.

## Construction rules

Prefer existing primitives over one-off controls. Preserve semantic tokens. Do not introduce Tailwind/shadcn/MUI/Chakra as a parallel runtime system without an explicit architecture decision. Keep loading/error/empty/permission states first-class.
