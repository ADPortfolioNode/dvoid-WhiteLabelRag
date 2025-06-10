# WhiteLabelRAG Color Palette Guide

This document provides guidance on using the standard color palette in the WhiteLabelRAG application.

## Core Color Scheme

The application's core color scheme consists of:
- White backgrounds (`--bg-primary`, `--bg-secondary`, `--bg-light`)
- Dark gray/black text (`--text-primary`, `--text-secondary`)
- Navy blue borders (`--border-primary`)

## Color Variables

### Semantic Color Variables

Use these semantic variables in your components for consistency:

| Variable | Purpose | Example Usage |
|----------|---------|---------------|
| `--text-primary` | Main text color | Body text, headings |
| `--text-secondary` | Secondary text | Subtitles, captions |
| `--text-muted` | Less prominent text | Timestamps, metadata |
| `--bg-primary` | Main background color | Page background, cards |
| `--bg-secondary` | Secondary backgrounds | Alternate sections |
| `--border-primary` | Main border color | Containers, dividers |

### Status Colors

Use these for status indicators and alerts:

| Variable | Purpose |
|----------|---------|
| `--status-success-bg` | Background for success messages |
| `--status-success-text` | Text color for success messages |
| `--status-warning-bg` | Background for warning messages |
| `--status-warning-text` | Text color for warning messages |
| `--status-danger-bg` | Background for error messages |
| `--status-danger-text` | Text color for error messages |
| `--status-info-bg` | Background for informational messages |
| `--status-info-text` | Text color for informational messages |

### Chat Interface Colors

Specialized variables for the chat interface:

| Variable | Purpose |
|----------|---------|
| `--chat-user-bg` | Background for user messages |
| `--chat-user-text` | Text color for user messages |
| `--chat-assistant-bg` | Background for assistant messages |
| `--chat-assistant-text` | Text color for assistant messages |
| `--chat-assistant-border` | Border color for assistant messages |

## Grayscale Palette

For fine-grained control, use the grayscale palette:

- `--color-gray-100` through `--color-gray-900`: Ranging from lightest to darkest gray

## Accent Colors

Use accent colors sparingly to draw attention to important elements:

- `--accent-blue`: Primary accent color
- `--accent-green`, `--accent-yellow`, `--accent-red`: For success, warning, and error states
- Additional accent colors: `--accent-indigo`, `--accent-purple`, `--accent-pink`, `--accent-orange`, `--accent-teal`, `--accent-cyan`

## Usage Guidelines

1. **Consistency**: Always use color variables instead of hardcoded hex values
2. **Accessibility**: Ensure sufficient contrast between text and background colors
3. **Semantics**: Use colors based on their meaning, not just for decoration
4. **Dark Mode**: The palette is designed to maintain white backgrounds in both light and dark modes

## Implementation Example

```css
.my-component {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.my-component-header {
  color: var(--text-secondary);
}

.my-component-status.success {
  background-color: var(--status-success-bg);
  color: var(--status-success-text);
}
```
