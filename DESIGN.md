---
name: InboxOps One-Bit Workstation
description: A warm-paper command desk for high-trust email operations.
colors:
  paper: "#f4f4ef"
  paper-raised: "#fafaf7"
  ink: "#151515"
  muted-ink: "#656663"
  line: "#c9cac5"
  line-strong: "#92938f"
  action-blue: "#2d5cff"
  action-blue-weak: "#edf1ff"
  danger: "#b73a32"
  success: "#147a52"
  warning: "#996515"
typography:
  headline:
    fontFamily: "Spline Sans, sans-serif"
    fontSize: "clamp(18px, 2vw, 24px)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Spline Sans, sans-serif"
    fontSize: "11px"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "Martian Mono, monospace"
    fontSize: "8px"
    fontWeight: 600
    letterSpacing: "0.08em"
rounded:
  status: "2px"
  control: "3px"
  container: "4px"
  panel: "6px"
  system: "8px"
spacing:
  micro: "5px"
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "20px"
  xl: "30px"
components:
  button-primary:
    backgroundColor: "{colors.action-blue}"
    textColor: "#ffffff"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  message-selected:
    backgroundColor: "{colors.action-blue-weak}"
    textColor: "{colors.ink}"
    rounded: "0"
---

# Design System: InboxOps One-Bit Workstation

## Overview

**Creative North Star: “The Command Desk”**

InboxOps is a dense, precise operating surface: warm paper fields sit inside near-black workstation chrome, with crisp inked separators and one electric-blue action signal. It should feel like a contemporary dispatch ledger—serious, tactile, and fast—without becoming nostalgic pixel art or a theatrical “hacker” interface.

The system is optimized for operating, not presenting. Account provenance, the message queue, the active thread, approval boundaries, and follow-up state remain legible at the moment of action. Human approval and local-first privacy are rendered as interface state, never buried as decorative reassurance.

**Key characteristics:**

- Flat, paper-like surfaces divided by explicit one-pixel rules.
- Compact information density with strong typographic role separation.
- Electric blue reserved for selection, focus, and consequential primary actions.
- Tiny bitmap-like details only for identity and state; production readability always wins.
- Minimal elevation, used only when a surface genuinely overlays the desk.

## Colors

The palette is intentionally one-bit in spirit, not literally monochrome: warm neutrals and hard ink carry structure, while blue and semantic colors carry state.

### Primary

- **Electric Action Blue** (`#2d5cff`): primary actions, keyboard focus, active markers, toggles, and explicit selected/action states.
- **Selection Wash** (`#edf1ff`): selected message rows and low-emphasis AI controls; pair it with an ink or blue edge so selection never depends on tint alone.

### Neutral

- **Warm Paper** (`#f4f4ef`): base workspace and nested intelligence surfaces.
- **Raised Paper** (`#fafaf7`): navigation, ledger, reader, dialogs, and utility surfaces.
- **Desk Ink** (`#151515`): primary text, structural borders, dark command chrome, and inverse labels.
- **Muted Ink** (`#656663`): metadata, explanatory copy, and secondary status.
- **Rule** (`#c9cac5`): ordinary dividers and field separators.
- **Strong Rule** (`#92938f`): interactive outlines and container boundaries.
- Pure white is limited to message content, avatars, and high-clarity inner surfaces; near-black (`#090a0c`–`#202124`) belongs to command-bar controls.

### Semantic

- **Danger Red** (`#b73a32`): urgent or high-risk score states.
- **Protected Green** (`#147a52`): confirmed privacy/protection status.
- **Waiting Amber** (`#996515`): follow-up and waiting states, usually on a pale warm background.

**The One-Blue Rule.** Do not introduce competing brand accents. Blue must remain rare enough to read immediately as action or state.

**The Semantic Redundancy Rule.** Never communicate urgency, success, selection, or waiting by color alone; retain labels, icons, scores, borders, or position.

## Typography

**Workhorse / body font:** Spline Sans with a `sans-serif` fallback.  
**Instrument / label font:** Martian Mono with a `monospace` fallback.

Spline Sans carries subjects, names, prose, headings, fields, and actions. Martian Mono is instrumentation: compact metadata, counts, timestamps, state labels, eyebrow copy, and system readouts. The pairing should feel contemporary and operational, never code-themed.

### Hierarchy

- **Thread headline:** Spline Sans 700, `clamp(18px, 2vw, 24px)`, `1.15` line-height, approximately `-0.035em` tracking.
- **Panel headline:** Spline Sans 700, 18–21px, tight negative tracking.
- **Section/title:** Spline Sans 600–700, 11–14px; compact but visibly stronger than metadata.
- **Body/email text:** Spline Sans 400, 11px/1.65, with readable content constrained to about `72ch`.
- **Interface text:** Spline Sans 500–700, typically 9–12px.
- **Instrument label:** Martian Mono 500–600, 7–10px, often uppercase with `0.05em`–`0.11em` tracking.
- **Instrument value:** Martian Mono 600–700, 9–17px for timestamps, counts, scores, and status figures.

**The Instrument Rule.** Martian Mono labels operational facts; it does not replace body copy or turn the UI into a terminal.

## Layout

The desktop topology is a command desk with persistent context:

1. A `224px` account/navigation rail.
2. A flexible work area under a `58px` dark command bar.
3. Inside the work area, a message ledger at `44%` (minimum `390px`) and a persistent reader (minimum `430px`).
4. A fixed `76px` operations band along the bottom; the shell reserves that height.

The rail, ledger, reader, and operations utilities remain simultaneously visible when space permits. Dividers—not floating cards—define regions. The common spacing rhythm is compact: 5–9px for control gaps and metadata, 10–16px for component padding, and 18–30px for reader or modal interiors. Use the observed values rather than expanding the interface into a low-density dashboard.

At `1100px` and below, compress the rail to `72px`, reduce the ledger to about `42%` with a `350px` minimum, hide secondary rail labels/status, and keep the reader persistent. At `760px` and below, use sequential list/reader views: the reader replaces the ledger after selection, controls become full-screen or edge-to-edge where appropriate, the account rail becomes a `52px` bottom navigation row, and the operations band becomes a `50px` row immediately above it. The mobile shell reserves `102px` for both rows. Avoid horizontal page scrolling; local nav strips may scroll when required.

## Elevation & Depth

The workstation is flat by default. Surface hierarchy comes from paper tone, one-pixel borders, and adjacency. Only dialogs, transient notices, and floating utility panels rise above the desk, using the single ambient shadow `0 18px 55px rgba(14,15,17,.18)` over a dark scrim (`rgba(10,11,13,.74)` for modal overlays). Do not add shadows to ordinary cards, navigation, buttons, or the operations band.

**The Structural Depth Rule.** A shadow means “temporarily above the desk,” not “important.” Importance is expressed with typography, ink, blue, and position.

## Shapes

Geometry is crisp and nearly square. One-pixel borders are the default structural device. The system radius token is `8px`, but shipped components deliberately use tighter values: `2px` for status marks, avatars, and small badges; `3px` for controls and fields; `4px` for contained cards; `5–6px` for floating panels and dialogs. Full-screen mobile dialogs have no radius.

Avoid pills except where a truly categorical compact token requires one; current labels use small rectangular outlines. Avoid borderless surface stacking. Preserve hard edges and visible separators without making every element heavy: ordinary dividers use Rule, interactive outlines use Strong Rule, and major topology uses Desk Ink.

## Components

### Buttons

- **Primary:** Electric blue fill, white text, 3–4px radius, strong compact label; used for compose, reply, send review, scheduling, and saving consequential settings.
- **Secondary:** transparent or white paper fill with an ink/strong-rule border; used for reversible utilities.
- **Ghost:** transparent with a border introduced on hover; appropriate in dark command chrome and reader tools.
- **Hover:** a modest tonal shift; the compose action may lift by `1px`. Never add glow.
- **Focus:** a visible `2px` Electric Blue outline with `2px` offset. Interactive pseudo-buttons receive the same focus treatment.
- **Disabled/busy:** preserve label clarity and expose busy state with text or the Lucide loader, not animation alone.

### Message Ledger

Rows are border-separated, not card-separated. Each row uses a compact three-column grid for state icon, avatar, and content. Hover changes the paper tone; selection uses Selection Wash plus a blue leading rule. Unread state uses weight. Subjects and snippets truncate rather than destabilize the grid.

### Thread Reader and Message Cards

The reader is persistent on desktop and sequential on mobile. Thread subjects lead with a small ink status tag. Message cards use a white surface, 1px Strong Rule, 4px radius, and no shadow. Headers disclose/collapse content and must remain keyboard operable with an exposed expanded state. Long-form message content uses generous line-height and a maximum width near `72ch`.

### Inputs and Fields

Fields use white or transparent paper, a 1px Strong Rule where boxed, and 3px corners. Composer address fields may rely on horizontal rules instead of boxes. Focus is always visible. Labels stay adjacent to their control, validation is textual, and disabled account/source fields remain legible.

### Dialogs, Drawers, and Brief Panels

Dialogs use Raised Paper, a 1px ink border, 5–6px radius, the system overlay shadow, and an explicit header/close action. Composer and control center become full-screen at the mobile breakpoint. Non-modal brief panels remain anchored to the operations band and must not masquerade as modal dialogs.

### Operations Band

The fixed bottom band is part of the desktop topology, not a floating dock. It displays connected/waiting/protected state, opens the daily brief, and provides follow-up access. Desktop cells are divided with rules; mobile actions share the available width.

### Status, Intelligence, and Approval

Intelligence panels use paper, ink borders, mono labels, visible score/category context, and plain-language provider/privacy attribution. Approval mode is explicit in composer headers and safety copy. “Review & send” precedes a separate confirmation; no visual shortcut may imply autonomous sending. Calendar creation follows the same explicit-approval grammar.

### Icons

Use Lucide outline icons at compact sizes, inheriting the surrounding color, with the global stroke weight near `1.7`. Icons support labels and state; they do not replace ambiguous actions without an accessible name. Small initials/markers may use deliberately pixel-crisp rendering, but do not introduce decorative pixel-art icon sets.

### Motion

Motion behaves like routed paper and workstation shutters. The command bar and rail come online once through directional clipping; selecting a conversation prints its reader sheet from the ledger edge; expandable messages unfold from their header; brief and control panels deploy from their point of origin. Routine hover and press feedback runs for `150–220ms`; reader and overlay continuity runs for `280–380ms`; the initial desk sequence stays below `620ms`. Use `cubic-bezier(.16,1,.3,1)` for confident arrivals and avoid bounce. Persistent layout never animates its dimensions. Under `prefers-reduced-motion: reduce`, authored choreography is removed while essential loading indicators and immediate state feedback remain available.

### Accessibility Expectations

- Meet WCAG 2.1 AA contrast for text, controls, borders that convey state, and focus indicators.
- Preserve semantic buttons, labels, dialog names, `aria-modal` truthfulness, expanded state, and keyboard activation for custom interactive headers.
- Keep every action reachable and visible at 200% zoom and through responsive reflow.
- Maintain a clear `2px` blue focus indicator; never remove outlines without an equivalent.
- Treat email HTML as untrusted content and retain sandboxing/isolation in its reader surface.
- Keep confirmation and provider/privacy boundaries understandable without relying on color, motion, or icons.

## Do's and Don'ts

### Do

- **Do** preserve the command-desk topology and simultaneous operational context on desktop.
- **Do** use paper tone and one-pixel rules as the primary hierarchy system.
- **Do** reserve Electric Blue for action, focus, and active state.
- **Do** keep approval, account provenance, AI provider, privacy, and follow-up state visible at the point of use.
- **Do** preserve compact density, keyboard operation, readable email measure, and responsive sequential views.
- **Do** use Spline Sans for reading and Martian Mono for instrumentation.

### Don't

- **Don't** introduce generic rounded SaaS cards, large soft radii, floating navigation, or a grid of decorative dashboard tiles.
- **Don't** use gradients, glassmorphism, backdrop blur, neon glow, or cyberpunk styling.
- **Don't** overuse pixel motifs, monospace typography, uppercase labels, shadows, or animation.
- **Don't** add a second accent palette or use semantic colors decoratively.
- **Don't** hide human approval behind legal copy or imply that AI actions are automatic.
- **Don't** fabricate testimonials, benchmarks, providers, or capabilities in portfolio-visible states.
- **Don't** ship fonts, images, or icons that depend on development-only paths or secrets.

### Deployment-safe assets and fonts

The current stylesheet imports Spline Sans and Martian Mono from Google Fonts. That is deployment-compatible but network-dependent; every family declaration must retain its generic fallback, and layouts must tolerate fallback metrics. If fonts are later self-hosted, place versioned WOFF2 files in a Vite-served public/static path, use relative public URLs, declare `font-display: swap`, verify licensing, and do not reference local machine paths. Lucide remains the canonical icon source and should be bundled through the existing package imports. Keep secrets and provider credentials out of CSS, asset URLs, frontend bundles, and source control; verify all assets against Vercel’s case-sensitive production paths.
