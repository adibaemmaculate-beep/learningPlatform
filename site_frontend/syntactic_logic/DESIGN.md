---
name: Syntactic Logic
colors:
  surface: '#f8f9ff'
  surface-dim: '#ccdbf3'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e6eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d5e3fc'
  on-surface: '#0d1c2e'
  on-surface-variant: '#45464d'
  inverse-surface: '#233144'
  inverse-on-surface: '#eaf1ff'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#735c00'
  on-secondary: '#ffffff'
  secondary-container: '#fed01b'
  on-secondary-container: '#6f5900'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#191c1e'
  on-tertiary-container: '#818486'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#ffe083'
  secondary-fixed-dim: '#eec200'
  on-secondary-fixed: '#231b00'
  on-secondary-fixed-variant: '#574500'
  tertiary-fixed: '#e0e3e5'
  tertiary-fixed-dim: '#c4c7c9'
  on-tertiary-fixed: '#191c1e'
  on-tertiary-fixed-variant: '#444749'
  background: '#f8f9ff'
  on-background: '#0d1c2e'
  surface-variant: '#d5e3fc'
typography:
  headline-xl:
    fontFamily: Geist
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Geist
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  container-max: 1280px
  gutter: 24px
---

## Brand & Style

The design system is built for a high-performance AI and coding education environment. It balances the technical precision required by developers with the accessibility needed for learners. The aesthetic is rooted in **Modern Minimalism**, prioritizing clarity, code-readability, and focus. 

The interface evokes an "IDE-plus" atmosphere—highly functional and structured, yet polished and inviting. It utilizes generous whitespace to reduce cognitive load during complex coding tasks, while maintaining a sophisticated, authoritative tone through a disciplined color palette and sharp typography.

## Colors

The palette is designed for deep focus and clear hierarchy. 
- **Primary Blue (#0F172A):** Used for structural elements like navigation, sidebars, and primary headings to establish a grounded, professional foundation.
- **Accent Yellow (#FACC15):** Reserved strictly for high-priority actions, active states, and progress indicators. This high-visibility color ensures users can always identify the "next step."
- **Backgrounds:** The system uses a dual-layer background approach. **White (#FFFFFF)** is used for the main content containers and cards to ensure maximum text contrast, while **Light Grey (#F1F5F9)** is used for the page canvas to provide subtle depth.
- **Typography:** Body text uses **Dark Grey (#334155)** to reduce eye strain compared to pure black, while maintaining a high AA/AAA accessibility rating.

## Typography

This design system utilizes a pairing of **Geist** for technical precision and **Inter** for reading endurance. 
- **Headings:** Set in Geist Bold. These are always Primary Blue to maintain visual weight and hierarchy.
- **Body Text:** Set in Inter Regular. This ensures that long-form educational content and documentation are highly legible.
- **Labels & Badges:** Use Geist Medium in uppercase with slight letter spacing. This differentiates meta-data and system statuses from content text.
- **Code Blocks:** (Suggested) Use a monospaced variant of Geist for all code snippets to ensure character alignment and clarity.

## Layout & Spacing

The layout follows a **Fixed-Fluid Hybrid** model. The main content area lives within a centered 1280px container on desktop, while sidebars for navigation and file trees are fixed-width to ensure consistency.

- **Grid:** A 12-column grid is used for dashboard layouts and course galleries.
- **Rhythm:** An 8px base unit governs all dimensions.
- **Mobile:** Margins scale down to 16px. Content stacks vertically, and secondary sidebars transition into bottom sheets or overlay drawers to preserve screen real estate for the code editor/content.

## Elevation & Depth

To maintain a clean, minimal aesthetic, the design system avoids heavy shadows. Instead, it uses **Tonal Layering** and **Low-Contrast Outlines**.

- **Level 0 (Canvas):** Light Grey (#F1F5F9).
- **Level 1 (Cards/Content):** White (#FFFFFF) with a 1px solid border (#E2E8F0). No shadow.
- **Level 2 (Modals/Popovers):** White (#FFFFFF) with a soft, diffused ambient shadow (0px 10px 15px -3px rgba(15, 23, 42, 0.05)) and a Primary Blue border (#0F172A) at 10% opacity.
- **Dividers:** 1px solid lines using Light Grey (#F1F5F9) to separate sections without breaking visual flow.

## Shapes

The shape language is **Soft and Precise**. A 0.25rem (4px) base radius is applied to all interactive elements to provide a modern feel that isn't overly "bubbly" or informal.

- **Buttons & Inputs:** 4px (rounded-sm)
- **Cards & Modals:** 8px (rounded-lg)
- **Badges/Tags:** 4px or fully pill-shaped depending on the context of the metadata.

## Components

### Buttons
- **Primary:** Accent Yellow background with Primary Blue text. Bold, high-contrast, for main actions like "Submit Code" or "Start Lesson."
- **Secondary:** White background with a 1px Primary Blue border and Primary Blue text. Used for "Cancel," "Back," or "Save Draft."
- **Destructive:** White background with a 1px Error Red border and Error Red text. Used for "Delete Repository" or "Reset Progress."

### Input Fields
Inputs use a white background, a 1px light grey border, and a 4px corner radius. On focus, the border shifts to Primary Blue with a subtle 2px outer glow in Accent Yellow (at 20% opacity).

### Chips & Badges
Small, uppercase labels. Status badges (Success, Warning, Error) use a light tinted background of their respective status color with dark text for high readability.

### Cards
Cards are the primary container for course modules and AI insights. They feature a white background, a subtle border, and 24px of internal padding (spacing-lg) to ensure content feels uncrowded.

### Code Editor (Specific Component)
The editor should use a dark theme even in the light mode design system (Primary Blue background) to align with developer preferences, featuring syntax highlighting that utilizes the Accent Yellow and Status Green colors.