---
name: 'Syntactic Logic: Teacher Portal'
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45464d'
  inverse-surface: '#213145'
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
  tertiary-container: '#271901'
  on-tertiary-container: '#98805d'
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
  tertiary-fixed: '#fcdeb5'
  tertiary-fixed-dim: '#dec29a'
  on-tertiary-fixed: '#271901'
  on-tertiary-fixed-variant: '#574425'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-lg:
    fontFamily: Geist
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Geist
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.03em
  table-data:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 24px
  gutter: 16px
  row-height-dense: 32px
  row-height-standard: 48px
---

## Brand & Style

The brand personality for this design system is authoritative yet enabling—a high-utility environment designed to reduce the cognitive load of educators. It prioritizes clarity and logical flow, positioning the interface as a silent, efficient partner in classroom management.

The design style is **Corporate / Modern** with a lean toward **Minimalism**. It leverages high-density layouts and a systematic hierarchy to handle complex administrative data without visual clutter. The aesthetic is defined by precision, using sharp Geist typography and disciplined spacing to ensure that critical information—like student performance and grading deadlines—is immediately legible.

## Colors

The palette is anchored by a deep Primary Blue (#0F172A) to project stability and professionalism. An Accent Yellow (#FACC15) is used sparingly for high-priority actions and highlighting active states.

For the grading ecosystem, a specific semantic triad is introduced:
- **Success (Green):** Indicates completed grading and verified submissions.
- **Warning (Orange):** Signals late submissions or pending actions nearing a deadline.
- **Error (Red):** Flags missing work, failing marks, or critical system alerts.

Background surfaces utilize a very light neutral gray (#F8FAFC) to maintain separation from pure white content cards, reducing eye strain during long grading sessions.

## Typography

This design system utilizes **Geist** exclusively to capitalize on its technical precision and exceptional legibility at small sizes. 

- **Headlines:** Use tight letter-spacing and semi-bold weights to anchor page sections.
- **Body:** Standardized at 14px for administrative forms to balance density and readability.
- **Data/Labels:** A specialized `table-data` role is defined for high-density gradebooks, ensuring numbers and names remain distinct even in compact views. Labels use a slightly heavier weight to stand out against data values.

## Layout & Spacing

The layout follows a **Fluid Grid** model with a 12-column structure for desktop. To accommodate data-heavy tables, the system uses a 4px baseline shift.

- **Desktop:** 24px outer margins with 16px gutters. Large tables may span the full 12 columns.
- **Tablet:** 16px margins; sidebars collapse into a compact icon-rail.
- **Mobile:** 12px margins; data tables transition to card-based stacks or horizontal scroll containers.

Spacing for forms is strictly vertical to emphasize the sequence of data entry. Tables utilize "Dense" (32px) and "Standard" (48px) row heights to allow teachers to toggle between high-overview and focused-detail modes.

## Elevation & Depth

Visual hierarchy is established through **Tonal Layers** and **Low-contrast outlines**. 

- **Level 0 (Background):** Soft gray (#F8FAFC).
- **Level 1 (Cards/Tables):** Pure white background with a 1px border (#E2E8F0). No shadow.
- **Level 2 (Popovers/Modals):** Pure white with a subtle, tight ambient shadow (0px 4px 12px rgba(15, 23, 42, 0.08)) to indicate temporary interaction.

This flat, bordered approach ensures that the interface remains performant and crisp on a variety of monitor types found in educational settings.

## Shapes

In accordance with the "Round Four" requirement, the system adopts a consistent 8px (0.5rem) corner radius for primary containers and inputs. 

- **Small elements (Buttons, Chips):** 8px (rounded-md).
- **Medium elements (Cards, Modals):** 16px (rounded-lg).
- **Large elements (Outer Wrappers):** 24px (rounded-xl).

This level of roundedness softens the technical nature of the Geist typeface, making the portal feel approachable while maintaining a professional structure.

## Components

### Buttons
- **Primary:** Solid Primary Blue with white text. 8px corner radius.
- **Secondary:** Accent Yellow background with Primary Blue text for high-importance "Add" or "Submit" actions.
- **Ghost:** Transparent background with 1px gray border for secondary navigation.

### Gradebook Tables
- Use alternating row stripes (Zebra striping) in 50% opacity of the background neutral.
- **Status Chips:** Small, condensed labels with a subtle background tint (10% opacity) of the status color and a 100% opacity text label (e.g., Green background at 10% with Dark Green text for "Graded").

### Inputs & Forms
- Input fields use a 1px border (#CBD5E1) that thickens to 2px Primary Blue on focus.
- Labels are positioned above the input using the `label-md` typography.

### Progress Indicators
- Vertical and horizontal progress bars use the Accent Yellow for "In Progress" and Success Green for "100% Complete."

### Cards
- Standard student cards include a `headline-sm` for the name and `label-sm` for IDs or metadata, wrapped in a 1px border container.