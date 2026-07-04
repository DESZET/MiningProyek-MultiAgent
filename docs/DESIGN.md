# Design System Inspired by Supabase

## 1. Visual Theme & Atmosphere

Supabase's website is a dark-mode-native developer platform that channels the aesthetic of a premium code editor — deep black backgrounds (`#0f0f0f`, `#171717`) with emerald green accents (`#3ecf8e`, `#00c573`) that reference the brand's open-source, PostgreSQL-green identity. The design system feels like it was born in a terminal window and evolved into a sophisticated marketing surface without losing its developer soul.

The typography is built on "Circular" — a geometric sans-serif with rounded terminals that softens the technical edge. At 72px with a 1.00 line-height, the hero text is compressed to its absolute minimum vertical space, creating dense, impactful statements that waste nothing. The monospace companion (Source Code Pro) appears sparingly for uppercase technical labels with 1.2px letter-spacing, creating the "developer console" markers that connect the marketing site to the product experience.

What makes Supabase distinctive is its sophisticated HSL-based color token system. Rather than flat hex values, Supabase uses HSL with alpha channels for nearly every color (`--colors-crimson4`, `--colors-purple5`, `--colors-slateA12`), enabling a nuanced layering system where colors interact through transparency. This creates depth through translucency — borders at `rgba(46, 46, 46)`, surfaces at `rgba(41, 41, 41, 0.84)`, and accents at partial opacity all blend with the dark background to create a rich, dimensional palette from minimal color ingredients.

The green accent (`#3ecf8e`) appears selectively — in the Supabase logo, in link colors (`#00c573`), and in border highlights (`rgba(62, 207, 142, 0.3)`) — always as a signal of "this is Supabase" rather than as a decorative element. Pill-shaped buttons (9999px radius) for primary CTAs contrast with standard 6px radius for secondary elements, creating a clear visual hierarchy of importance.

**Key Characteristics:**
- Dual-mode design: dark-mode-native identity, with a complementary light mode for daytime / printed-context use
- Near-black backgrounds (`#0f0f0f`, `#171717`) in dark mode; near-white surfaces (`#ffffff`, `#fafafa`) in light mode — never pure black or pure white-on-white
- Emerald green brand accent (`#3ecf8e`, `#00c573`) used sparingly as identity marker — slightly darkened (`#008556`) on light backgrounds for AA contrast
- Circular font — geometric sans-serif with rounded terminals
- Source Code Pro for uppercase technical labels (1.2px letter-spacing)
- HSL-based color token system with alpha channels for translucent layering
- Pill buttons (9999px) for primary CTAs, 6px radius for secondary
- Inverted neutral scale: dark mode `#171717 → #898989 → #fafafa`; light mode `#171717 ← #737373 ← #fafafa` (same hue family, mirrored)
- Border system using dark grays (`#2e2e2e`, `#363636`, `#393939`) in dark; light grays (`#ececec`, `#e5e5e5`, `#d4d4d4`) in light
- Minimal shadows in dark (depth via borders); subtle shadows in light (depth via soft elevation, since borders alone read flat on white)
- Radix color primitives (crimson, purple, violet, indigo, yellow, tomato, orange, slate)

## 2. Color Palette & Roles

### Brand (Mode-Agnostic)
- **Supabase Green** (`#3ecf8e`): Primary brand color, logo, decorative accent — works on both dark and light surfaces as a non-text element
- **Green Link – Dark Mode** (`#00c573`): Interactive green for links/actions on dark surfaces — passes AA on `#171717`
- **Green Link – Light Mode** (`#008556`): Darkened emerald variant for links/actions on light surfaces — passes AA on `#ffffff`
- **Green Button BG – Light Mode** (`#00875a`): Slightly darker emerald for primary CTA backgrounds on light surfaces, paired with white text
- **Green Border – Dark Mode** (`rgba(62, 207, 142, 0.3)`): 30% emerald — visible on near-black
- **Green Border – Light Mode** (`rgba(0, 133, 86, 0.4)`): 40% darkened emerald — visible on near-white
- **Green Focus Ring** (`rgba(62, 207, 142, 0.2)`): Used in both modes as the focus indicator (3px outer ring)

### Neutral Scale (Dark Mode)
- **Near Black** (`#0f0f0f`): Primary button background, deepest surface
- **Dark** (`#171717`): Page background, primary canvas
- **Dark Border** (`#242424`): Horizontal rule, section dividers
- **Border Dark** (`#2e2e2e`): Card borders, tab borders
- **Mid Border** (`#363636`): Button borders, dividers
- **Border Light** (`#393939`): Secondary borders
- **Charcoal** (`#434343`): Tertiary borders, dark accents
- **Dark Gray** (`#4d4d4d`): Heavy secondary text
- **Mid Gray** (`#898989`): Muted text, link color
- **Light Gray** (`#b4b4b4`): Secondary link text
- **Near White** (`#efefef`): Light border, subtle surface
- **Off White** (`#fafafa`): Primary text, button text

### Neutral Scale (Light Mode)
The light scale is the **mirror inverse** of the dark scale — same hue family, reversed positions. This preserves the design's identity while adapting to white-base surfaces.

- **Pure White** (`#ffffff`): Primary canvas, page background, card surfaces
- **Off White** (`#fafafa`): Alternate surface, hover state on white, button base
- **Subtle Surface** (`#f5f5f5`): Secondary canvas, code blocks, inset wells
- **Near White Border** (`#ececec`): Hairline dividers, ultra-subtle separators
- **Light Border** (`#e5e5e5`): Card borders, tab borders — the standard light-mode border
- **Mid Border** (`#d4d4d4`): Button borders, prominent dividers
- **Border Heavy** (`#bdbdbd`): Emphasized borders (used sparingly)
- **Light Gray** (`#a3a3a3`): Disabled text, placeholder
- **Mid Gray** (`#737373`): Muted text, tertiary link color
- **Dark Gray** (`#525252`): Secondary text, body de-emphasized
- **Charcoal** (`#404040`): Heavy secondary text
- **Near Black** (`#171717`): Primary text on light surfaces — matches dark-mode primary surface (intentional symmetry)
- **Deep Black** (`#0f0f0f`): Reserved for extreme contrast use, e.g., button text on light pill

### Radix Color Tokens (HSL-based)
- **Slate Scale**: `--colors-slate5` through `--colors-slateA12` — neutral progression
- **Purple**: `--colors-purple4`, `--colors-purple5`, `--colors-purpleA7` — accent spectrum
- **Violet**: `--colors-violet10` (`hsl(251, 63.2%, 63.2%)`) — vibrant accent
- **Crimson**: `--colors-crimson4`, `--colors-crimsonA9` — warm accent / alert
- **Indigo**: `--colors-indigoA2` — subtle blue wash
- **Yellow**: `--colors-yellowA7` — attention/warning
- **Tomato**: `--colors-tomatoA4` — error accent
- **Orange**: `--colors-orange6` — warm accent

### Surface & Overlay (Dark Mode)
- **Glass Dark** (`rgba(41, 41, 41, 0.84)`): Translucent dark overlay
- **Slate Alpha** (`hsla(210, 87.8%, 16.1%, 0.031)`): Ultra-subtle blue wash
- **Fixed Scale Alpha** (`hsla(200, 90.3%, 93.4%, 0.109)`): Light frost overlay

### Surface & Overlay (Light Mode)
- **Glass Light** (`rgba(255, 255, 255, 0.84)`): Translucent white overlay for sticky headers, modals
- **Slate Wash** (`hsla(210, 87.8%, 96.5%, 0.4)`): Ultra-subtle cool wash for hero sections
- **Hover Tint** (`rgba(0, 0, 0, 0.02)`): Barely-there hover state on white surfaces — preferred over heavier hovers
- **Pressed Tint** (`rgba(0, 0, 0, 0.04)`): Active/pressed state for clickable surfaces

### Shadows

**Dark Mode**: Supabase uses **almost no shadows** in dark theme. Depth comes from border contrast and surface color differences. Focus states use `rgba(0, 0, 0, 0.1) 0px 4px 12px` — minimal, functional.

**Light Mode**: Borders alone read flat on white, so subtle shadows DO play a role. Use a restrained 4-level scale, all very low-alpha to maintain the minimal philosophy:

| Level | Shadow | Use |
|---|---|---|
| 0 | `none` | Default flat surface — page-level content |
| 1 | `0 1px 2px rgba(15, 15, 15, 0.04)` | Cards at rest, input fields |
| 2 | `0 4px 8px rgba(15, 15, 15, 0.06)` | Hovered card, dropdown, tooltip |
| 3 | `0 8px 24px rgba(15, 15, 15, 0.08)` | Popover, dialog, modal |
| Focus | `0 0 0 3px rgba(62, 207, 142, 0.25)` | Keyboard focus ring (both modes) |

## 3. Typography Rules

### Font Families
- **Primary**: `Circular`, with fallbacks: `custom-font, Helvetica Neue, Helvetica, Arial`
- **Monospace**: `Source Code Pro`, with fallbacks: `Office Code Pro, Menlo`

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|------|--------|-------------|----------------|-------|
| Display Hero | Circular | 72px (4.50rem) | 400 | 1.00 (tight) | normal | Maximum density, zero waste |
| Section Heading | Circular | 36px (2.25rem) | 400 | 1.25 (tight) | normal | Feature section titles |
| Card Title | Circular | 24px (1.50rem) | 400 | 1.33 | -0.16px | Slight negative tracking |
| Sub-heading | Circular | 18px (1.13rem) | 400 | 1.56 | normal | Secondary headings |
| Body | Circular | 16px (1.00rem) | 400 | 1.50 | normal | Standard body text |
| Nav Link | Circular | 14px (0.88rem) | 500 | 1.00–1.43 | normal | Navigation items |
| Button | Circular | 14px (0.88rem) | 500 | 1.14 (tight) | normal | Button labels |
| Caption | Circular | 14px (0.88rem) | 400–500 | 1.43 | normal | Metadata, tags |
| Small | Circular | 12px (0.75rem) | 400 | 1.33 | normal | Fine print, footer links |
| Code Label | Source Code Pro | 12px (0.75rem) | 400 | 1.33 | 1.2px | `text-transform: uppercase` |

### Principles
- **Weight restraint**: Nearly all text uses weight 400 (regular/book). Weight 500 appears only for navigation links and button labels. There is no bold (700) in the detected system — hierarchy is created through size, not weight.
- **1.00 hero line-height**: The hero text is compressed to absolute zero leading. This is the defining typographic gesture — text that feels like a terminal command: dense, efficient, no wasted vertical space.
- **Negative tracking on cards**: Card titles use -0.16px letter-spacing, a subtle tightening that differentiates them from body text without being obvious.
- **Monospace as ritual**: Source Code Pro in uppercase with 1.2px letter-spacing is the "developer console" voice — used sparingly for technical labels that connect to the product experience.
- **Geometric personality**: Circular's rounded terminals create warmth in what could otherwise be a cold, technical interface. The font is the humanizing element.

## 4. Component Stylings

### Buttons

#### Dark Mode

**Primary Pill (Dark)**
- Background: `#0f0f0f`
- Text: `#fafafa`
- Padding: 8px 32px
- Radius: 9999px (full pill)
- Border: `1px solid #fafafa` (white border on dark)
- Focus shadow: `rgba(0, 0, 0, 0.1) 0px 4px 12px`
- Use: Primary CTA ("Start your project")

**Secondary Pill (Dark, Muted)**
- Background: `#0f0f0f`
- Text: `#fafafa`
- Padding: 8px 32px
- Radius: 9999px
- Border: `1px solid #2e2e2e` (dark border)
- Opacity: 0.8
- Use: Secondary CTA alongside primary

**Ghost Button (Dark)**
- Background: transparent
- Text: `#fafafa`
- Padding: 8px
- Radius: 6px
- Border: `1px solid transparent`
- Use: Tertiary actions, icon buttons

#### Light Mode

**Primary Pill (Light) — Brand-emphasized**
- Background: `#00875a` (darkened emerald, AA on white text)
- Text: `#ffffff`
- Padding: 8px 32px
- Radius: 9999px
- Border: `1px solid #00875a`
- Hover: background `#006b48`
- Focus ring: `0 0 0 3px rgba(62, 207, 142, 0.25)`
- Shadow at rest: `0 1px 2px rgba(15, 15, 15, 0.06)`
- Use: Primary CTA — pushes the brand identity ("Mulai Kuis", "Generate Quiz")

**Primary Pill (Light) — Neutral alternate**
- Background: `#171717` (mirrors dark-mode primary pill, inverted)
- Text: `#fafafa`
- Padding: 8px 32px
- Radius: 9999px
- Border: `1px solid #171717`
- Use: When emerald is already used elsewhere in the same view (avoid double-emphasis)

**Secondary Pill (Light)**
- Background: `#ffffff`
- Text: `#171717`
- Padding: 8px 32px
- Radius: 9999px
- Border: `1px solid #d4d4d4`
- Hover: background `#fafafa`, border `#a3a3a3`
- Use: Secondary CTA paired with a primary

**Ghost Button (Light)**
- Background: transparent
- Text: `#171717`
- Padding: 8px
- Radius: 6px
- Border: `1px solid transparent`
- Hover: background `rgba(0, 0, 0, 0.04)`
- Use: Tertiary actions, icon buttons

**Destructive (Both Modes)**
- Light: background `#dc2626`, text `#ffffff`, border same as bg
- Dark: background `#1a0a0a`, text `#fca5a5`, border `#7f1d1d`
- Use: Reset, delete, irreversible actions

### Cards & Containers

**Dark Mode**
- Background: dark surfaces (`#171717` or slightly lighter)
- Border: `1px solid #2e2e2e` or `#363636`
- Radius: 8px–16px
- No visible shadows — borders define edges
- Internal padding: 16px–24px

**Light Mode**
- Background: `#ffffff` (primary), `#fafafa` (alternate / nested)
- Border: `1px solid #e5e5e5` (default) or `#d4d4d4` (prominent)
- Radius: 8px–16px
- Resting shadow: `0 1px 2px rgba(15, 15, 15, 0.04)` — soft, almost imperceptible
- Hover shadow (interactive cards): `0 4px 8px rgba(15, 15, 15, 0.06)`
- Internal padding: 16px–24px

### Tabs

**Dark Mode**
- Border: `1px solid #2e2e2e`
- Radius: 9999px (pill tabs)
- Active: green accent or lighter surface
- Inactive: dark, muted

**Light Mode**
- Border: `1px solid #e5e5e5`
- Radius: 9999px (pill tabs)
- Active: `#171717` background, `#fafafa` text — OR emerald variant `#00875a` background, white text
- Inactive: `#ffffff` background, `#737373` text
- Hover (inactive): `#fafafa` background

### Links

**Dark Mode**
- **Green**: `#00c573` — branded links
- **Primary Light**: `#fafafa` — standard links on dark
- **Secondary**: `#b4b4b4` — muted links
- **Muted**: `#898989` — tertiary links, footer

**Light Mode**
- **Green**: `#008556` — branded links (AA contrast on white)
- **Primary Dark**: `#171717` — standard links, often with underline-on-hover
- **Secondary**: `#525252` — muted links
- **Muted**: `#737373` — tertiary links, footer
- **Visited** (optional): `#5b21b6` (Tailwind violet 800) for academic/long-form pages

### Navigation

**Dark Mode**
- Background matching page (`#171717`)
- Brand logo with green icon
- Circular 14px weight 500 for nav links
- Clean horizontal layout
- Green pill CTA right-aligned
- Sticky header behavior

**Light Mode**
- Background: `#ffffff` with bottom border `1px solid #e5e5e5` (instead of relying on the dark contrast that defines the dark nav)
- OR translucent: `rgba(255, 255, 255, 0.84)` with `backdrop-filter: blur(8px)` for sticky behavior
- Brand logo with full-color emerald icon
- Circular 14px weight 500, text `#171717`
- Hover state on nav links: text becomes `#008556` (brand green)
- Light-mode primary pill CTA right-aligned (emerald `#00875a` bg)
- Sticky header behavior, with shadow appearing only on scroll: `0 1px 2px rgba(15, 15, 15, 0.04)`

## 5. Layout Principles

### Spacing System
- Base unit: 8px
- Scale: 1px, 4px, 6px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px, 90px, 96px, 128px
- Notable large jumps: 48px → 90px → 96px → 128px for major section spacing

### Grid & Container
- Centered content with generous max-width
- Full-width dark sections with constrained inner content
- Feature grids: icon-based grids with consistent card sizes
- Logo grids for "Trusted by" sections
- Footer: multi-column on dark background

### Breakpoints
| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile | <600px | Single column, stacked layout |
| Desktop | >600px | Multi-column grids, expanded layout |

*Note: Supabase uses a notably minimal breakpoint system — primarily a single 600px breakpoint, suggesting a mobile-first approach with progressive enhancement.*

### Whitespace Philosophy
- **Dramatic section spacing**: 90px–128px between major sections creates a cinematic pacing — each section is its own scene in the dark void.
- **Dense content blocks**: Within sections, spacing is tight (16px–24px), creating concentrated information clusters.
- **Border-defined space**: Instead of whitespace + shadows for separation, Supabase uses thin borders on dark backgrounds — separation through line, not gap.

### Border Radius Scale
- Standard (6px): Ghost buttons, small elements
- Comfortable (8px): Cards, containers
- Medium (11px–12px): Mid-size panels
- Large (16px): Feature cards, major containers
- Pill (9999px): Primary buttons, tab indicators

## 6. Depth & Elevation

### Dark Mode (Border-defined depth)

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat (Level 0) | No shadow, border `#2e2e2e` | Default state, most surfaces |
| Subtle Border (Level 1) | Border `#363636` or `#393939` | Interactive elements, hover |
| Focus (Level 2) | `rgba(0, 0, 0, 0.1) 0px 4px 12px` | Focus states only |
| Green Accent (Level 3) | Border `rgba(62, 207, 142, 0.3)` | Brand-highlighted elements |

**Dark Shadow Philosophy**: In dark-mode-native design, shadows are nearly invisible and serve no purpose. Instead, depth is communicated through a sophisticated border hierarchy — from `#242424` (barely visible) through `#2e2e2e` (standard) to `#393939` (prominent). The green accent border (`rgba(62, 207, 142, 0.3)`) at 30% opacity is the "elevated" state — the brand color itself becomes the depth signal.

### Light Mode (Shadow + Border combined)

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat (Level 0) | No shadow, border `#e5e5e5` | Default surface, page-level content |
| Resting (Level 1) | Border `#e5e5e5` + shadow `0 1px 2px rgba(15, 15, 15, 0.04)` | Cards at rest, input fields |
| Hover (Level 2) | Border `#d4d4d4` + shadow `0 4px 8px rgba(15, 15, 15, 0.06)` | Hovered card, dropdown |
| Floating (Level 3) | Border `#e5e5e5` + shadow `0 8px 24px rgba(15, 15, 15, 0.08)` | Popover, dialog, modal |
| Green Accent (Level 4) | Border `rgba(0, 133, 86, 0.4)` + shadow Level 1 | Brand-highlighted elements |
| Focus | Outline `0 0 0 3px rgba(62, 207, 142, 0.25)` | Keyboard focus on interactive elements |

**Light Shadow Philosophy**: Borders alone read flat on white, so a soft 4-level shadow scale provides perceptible elevation. Shadows are kept low-alpha (4%–8%) and offset minimally — the goal is "depth you feel before you see." Borders still anchor every surface; shadows complement, never replace them. Avoid Material Design–style heavy shadows (no `0.2`+ alpha values).

## 7. Do's and Don'ts

### Do (Both Modes)
- Apply emerald green sparingly — it's an identity marker, not a decoration. Use the mode-correct variant (`#00c573` dark / `#008556` light) for text, `#3ecf8e` for icons.
- Use Circular at weight 400 for nearly everything — 500 only for buttons and nav
- Set hero text to 1.00 line-height — the zero-leading is the typographic signature
- Use pill shape (9999px) exclusively for primary CTAs and tabs
- Employ HSL-based colors with alpha for translucent layering effects
- Use Source Code Pro uppercase labels for developer-context markers
- Pair every surface with a border (light or dark) — borders are the structural element across both modes

### Do (Dark Mode)
- Use near-black backgrounds (`#0f0f0f`, `#171717`) — depth comes from the gray border hierarchy
- Create depth through border color differences (`#242424` → `#2e2e2e` → `#363636`)

### Do (Light Mode)
- Use pure white (`#ffffff`) for primary surfaces and `#fafafa` for nested or alternate surfaces
- Use the inverted border scale (`#ececec` → `#e5e5e5` → `#d4d4d4`) — same hierarchical thinking, lighter values
- Apply subtle low-alpha shadows (Levels 1–3) for elevation — they replace the border-only depth that works in dark
- Darken text-bearing greens to `#008556` for AA contrast — never use `#3ecf8e` for body links or button text on white
- Use translucent white (`rgba(255, 255, 255, 0.84)` + backdrop-blur) for sticky headers

### Don't (Both Modes)
- Don't use bold (700) text weight — the system uses 400 and 500 only
- Don't apply green to large background surfaces — it's for borders, links, and small accents
- Don't use warm colors (crimson, orange) as primary design elements — they exist as semantic tokens for states (e.g., "Sedang", "Rendah")
- Don't increase hero line-height above 1.00 — the density is intentional
- Don't use large border radius (16px+) on buttons — pills (9999px) or standard (6px), nothing in between
- Don't forget the translucent borders — `rgba` border colors are the layering mechanism

### Don't (Dark Mode)
- Don't add box-shadows — they're invisible on dark backgrounds and break the border-defined depth system
- Don't lighten the background above `#171717` for primary surfaces — the darkness is structural

### Don't (Light Mode)
- Don't use heavy shadows (alpha > 0.1) — they break the minimal philosophy and make the design feel like generic Material UI
- Don't use pure black (`#000000`) for text — `#171717` matches the dark-mode primary surface and reads warmer
- Don't use `#3ecf8e` directly for links or button text on white — fails AA contrast (use `#008556` instead)
- Don't omit borders just because shadows exist — borders + shadows together define the surface
- Don't use the dark-mode green link `#00c573` on white — it's tuned for dark surfaces

## 8. Responsive Behavior

### Breakpoints
| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile | <600px | Single column, stacked features, condensed nav |
| Desktop | >600px | Multi-column grids, full nav, expanded sections |

### Collapsing Strategy
- Hero: 72px → scales down proportionally
- Feature grids: multi-column → single column stacked
- Logo row: horizontal → wrapped grid
- Navigation: full → hamburger
- Section spacing: 90–128px → 48–64px
- Buttons: inline → full-width stacked

## 9. Agent Prompt Guide

### Quick Color Reference — Dark Mode
- Background: `#0f0f0f` (button), `#171717` (page)
- Text: `#fafafa` (primary), `#b4b4b4` (secondary), `#898989` (muted)
- Brand green: `#3ecf8e` (icon/decorative), `#00c573` (links)
- Borders: `#242424` (subtle), `#2e2e2e` (standard), `#363636` (prominent)
- Green border: `rgba(62, 207, 142, 0.3)` (accent)
- Shadow: avoid

### Quick Color Reference — Light Mode
- Background: `#ffffff` (page/card), `#fafafa` (alternate/nested), `#f5f5f5` (subtle surface)
- Text: `#171717` (primary), `#525252` (secondary), `#737373` (muted)
- Brand green: `#3ecf8e` (icon/decorative), `#008556` (text/links — AA on white), `#00875a` (button bg)
- Borders: `#ececec` (subtle), `#e5e5e5` (standard), `#d4d4d4` (prominent)
- Green border: `rgba(0, 133, 86, 0.4)` (accent)
- Shadows: `0 1px 2px rgba(15, 15, 15, 0.04)` (resting), `0 4px 8px rgba(15, 15, 15, 0.06)` (hover), `0 8px 24px rgba(15, 15, 15, 0.08)` (modal)

### Mode-Switching Token Map
| Role | Dark Mode | Light Mode |
|---|---|---|
| Page bg | `#171717` | `#ffffff` |
| Card bg | `#171717` | `#ffffff` |
| Nested surface | `#1a1a1a` | `#fafafa` |
| Primary text | `#fafafa` | `#171717` |
| Secondary text | `#b4b4b4` | `#525252` |
| Muted text | `#898989` | `#737373` |
| Standard border | `#2e2e2e` | `#e5e5e5` |
| Prominent border | `#363636` | `#d4d4d4` |
| Brand link | `#00c573` | `#008556` |
| Brand button bg | `#0f0f0f` (with white border) | `#00875a` |
| Brand accent border | `rgba(62, 207, 142, 0.3)` | `rgba(0, 133, 86, 0.4)` |

### Example Component Prompts — Dark Mode
- "Create a hero section on #171717 background. Headline at 72px Circular weight 400, line-height 1.00, #fafafa text. Sub-text at 16px Circular weight 400, line-height 1.50, #b4b4b4. Pill CTA button (#0f0f0f bg, #fafafa text, 9999px radius, 8px 32px padding, 1px solid #fafafa border)."
- "Design a feature card: #171717 background, 1px solid #2e2e2e border, 16px radius. Title at 24px Circular weight 400, letter-spacing -0.16px. Body at 14px weight 400, #898989 text."
- "Build navigation bar: #171717 background. Circular 14px weight 500 for links, #fafafa text. Brand logo with green icon left-aligned. Green pill CTA 'Mulai Kuis' right-aligned."

### Example Component Prompts — Light Mode
- "Create a hero section on #ffffff background. Headline at 72px Circular weight 400, line-height 1.00, #171717 text. Sub-text at 16px Circular weight 400, line-height 1.50, #525252. Primary pill CTA: #00875a bg, #ffffff text, 9999px radius, 8px 32px padding, 1px solid #00875a border, shadow `0 1px 2px rgba(15, 15, 15, 0.06)`."
- "Design a feature card: #ffffff background, 1px solid #e5e5e5 border, 16px radius, shadow `0 1px 2px rgba(15, 15, 15, 0.04)`. Title at 24px Circular weight 400, letter-spacing -0.16px, #171717 text. Body at 14px weight 400, #737373 text. Hover state lifts to shadow `0 4px 8px rgba(15, 15, 15, 0.06)` with border #d4d4d4."
- "Build navigation bar: #ffffff background, bottom border 1px solid #e5e5e5. Circular 14px weight 500 for links, #171717 text, hover #008556. Brand logo with full-color emerald icon. Primary pill CTA 'Mulai Kuis' (bg #00875a, white text) right-aligned."
- "Create a result card showing 'Tingkat Pemahaman: Tinggi' — light mode. Background #ffffff, border 1px solid rgba(0, 133, 86, 0.4) (brand-accent border), shadow `0 1px 2px rgba(15, 15, 15, 0.04)`, 16px radius. Badge at top-left: bg #008556, text #ffffff, 9999px radius, 12px Source Code Pro uppercase letter-spacing 1.2px reading 'TINGGI'. Headline 24px #171717. Body 14px #525252."

### Iteration Guide
1. **Pick a mode first** — dark `#171717` or light `#ffffff` as the canvas. The whole token system flips from there.
2. Green is the brand identity marker — use the mode-correct text variant (`#00c573` dark / `#008556` light) for any text-bearing green; `#3ecf8e` is reserved for icon/decorative use across both modes
3. **Dark mode**: depth comes from borders (`#242424` → `#2e2e2e` → `#363636`), not shadows
4. **Light mode**: depth comes from borders (`#ececec` → `#e5e5e5` → `#d4d4d4`) PLUS subtle low-alpha shadows (Levels 1–3)
5. Weight 400 is the default for everything — 500 only for interactive elements
6. Hero line-height of 1.00 is the signature typographic move (mode-agnostic)
7. Pill (9999px) for primary actions, 6px for secondary, 8–16px for cards
8. HSL with alpha channels creates the sophisticated translucent layering — alpha values stay low (≤0.4) in light mode to preserve the minimal feel
