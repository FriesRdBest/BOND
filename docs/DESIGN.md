# BOND visual and content standards

## Direction

Use the supplied Cortex website screenshots as visual references, not an official brand specification. BOND remains independently identified. Do not copy the Cortex logo or imply endorsement. Use near black backgrounds, charcoal surfaces, fine borders, generous spacing, clear hierarchy, and restrained violet and lavender accents.

## Established primitives

| Role | Value |
| --- | --- |
| Canvas baseline | #111216 |
| Elevated surface | #1A1C23 |
| Passing state | #10B981 |
| Operational warning | #F59E0B |

Emerald and amber communicate status. Violet and lavender establish the accent direction. Exact accent shades, typography, border colors, and complete contrast pairs require selection and testing.

## Token hierarchy

Define primitives, map them to semantic roles, then apply component tokens. Avoid arbitrary component values that bypass the system. Keep token checks separate from domain policy enforcement.

## Accessibility

Support keyboard navigation, visible focus, readable contrast, meaningful labels, responsive containment, and status cues beyond color. Give charts textual context. Test custom components rather than assuming accessibility. Combine automated checks with manual review. Do not claim conformance without scoped evidence.

## Motion

Use brief, restrained transitions to explain state changes. Respect reduced motion preferences. Avoid decorative loops, delayed access, exaggerated hover effects, and optimistic success claims before confirmation.

## Writing

Use headings, short paragraphs, and tables. Avoid dot point lists and hyphenated words in authored human facing prose. Preserve valid technical syntax and the original license. Explain unfamiliar terms, label simulations, and prefer honest specifics to prestige language.

## Component states

Design loading, empty, error, success, stale evidence, missing evidence, and denied action states deliberately. Never conceal a failed operation behind motion or styling.

## Locked implementation specification

The following values are BOND implementation choices, not official Cortex tokens. The packaged design_tokens.json file is the executable source. Update this record when an accessibility correction changes a value.

| Primitive | Value |
| --- | --- |
| canvas | `#111216` |
| surface | `#1A1C23` |
| raised | `#22252E` |
| text | `#F4F3F8` |
| secondary | `#B9B7C8` |
| muted | `#9693A8` |
| violet | `#A78BFA` |
| lavender | `#C4B5FD` |
| emerald | `#10B981` |
| amber | `#F59E0B` |
| red | `#F87171` |
| border | `#343744` |
| font_body | `Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` |
| font_mono | `ui-monospace, SFMono-Regular, Consolas, monospace` |
| space_unit | `4px` |
| space_control | `16px` |
| space_card | `24px` |
| space_section | `32px` |
| text_small | `12px` |
| text_body | `14px` |
| text_explanation | `16px` |
| text_section | `20px` |
| text_page | `28px` |
| text_metric | `36px` |
| radius_control | `8px` |
| radius_card | `12px` |
| radius_panel | `16px` |
| motion_control | `120ms` |
| motion_state | `180ms` |
| focus_width | `2px` |

Inter is used when available, with the recorded system fallbacks. No remote font request is required for a usable interface. Use tabular numerals for comparable metrics. Use readable labels and icons with status colors. Body line height is 1.5 and heading line height is 1.2. Control and state transitions use an ease out timing curve. Reduced motion disables nonessential motion. Focus uses a 2 px lavender outline with a 2 px offset. Ordinary borders are not a substitute for visible interactive boundaries. Normal text pairs must meet at least 4.5 to 1 contrast. This test does not constitute a complete accessibility audit.
