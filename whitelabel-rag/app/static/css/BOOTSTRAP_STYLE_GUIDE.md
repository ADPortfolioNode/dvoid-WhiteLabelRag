# Bootstrap Style Guide for WhiteLabelRAG

This document provides comprehensive guidance on using the Bootstrap-based style system in the WhiteLabelRAG application.

## Table of Contents

1. [Introduction](#introduction)
2. [Layout Principles](#layout-principles)
3. [Grid System](#grid-system)
4. [Typography](#typography)
5. [Color System](#color-system)
6. [Components](#components)
7. [Azure-Style Components](#azure-style-components)
8. [Utility Classes](#utility-classes)
9. [Accessibility Guidelines](#accessibility-guidelines)
10. [Responsive Design](#responsive-design)

## Introduction

This style guide follows Bootstrap 5.3 conventions and best practices to ensure consistent, responsive, and accessible UI components throughout the WhiteLabelRAG application. The guide standardizes spacing, typography, color usage, and component styling.

## Layout Principles

### Container System

Use the Bootstrap container system for consistent page layout:

```html
<!-- Full-width container -->
<div class="container-fluid">
  <!-- Content here -->
</div>

<!-- Responsive fixed-width container -->
<div class="container">
  <!-- Content here -->
</div>
```

### Spacing

Follow the standard spacing scale to maintain visual rhythm:

- `--bs-spacer-1`: 0.25rem (4px)
- `--bs-spacer-2`: 0.5rem (8px)
- `--bs-spacer-3`: 1rem (16px)
- `--bs-spacer-4`: 1.5rem (24px)
- `--bs-spacer-5`: 3rem (48px)

Apply spacing using utility classes:

```html
<div class="mb-3"><!-- Margin bottom 1rem --></div>
<div class="p-4"><!-- Padding 1.5rem --></div>
```

## Grid System

WhiteLabelRAG uses Bootstrap's 12-column grid system for layouts:

```html
<div class="standard-row">
  <div class="standard-col-12 standard-col-md-6 standard-col-lg-4">
    <!-- Column content -->
  </div>
  <div class="standard-col-12 standard-col-md-6 standard-col-lg-8">
    <!-- Column content -->
  </div>
</div>
```

Grid breakpoints:
- Extra Small (xs): < 576px
- Small (sm): ≥ 576px
- Medium (md): ≥ 768px
- Large (lg): ≥ 992px
- Extra Large (xl): ≥ 1200px
- Extra Extra Large (xxl): ≥ 1400px

## Typography

### Font Family

The application uses system fonts with fallbacks:

```css
font-family: var(--bs-font-sans-serif);
```

For monospace text (code, etc.):

```css
font-family: var(--bs-font-monospace);
```

### Heading Sizes

- `h1`: 2.5rem (40px)
- `h2`: 2rem (32px)
- `h3`: 1.75rem (28px)
- `h4`: 1.5rem (24px)
- `h5`: 1.25rem (20px)
- `h6`: 1rem (16px)

### Font Weights

- Light: 300
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

## Color System

WhiteLabelRAG uses a semantic color system:

```css
/* Base colors - from color-palette.css */
--color-white: #ffffff;
--color-black: #000000;
--color-navy: #000080;

/* Semantic colors */
--text-primary: var(--color-gray-900);
--bg-primary: var(--color-white);
--border-primary: var(--color-navy);
```

For consistent UI, use semantic color variables instead of direct color values.

## Components

### Cards

Use the standard card components for content containers:

```html
<div class="standard-card">
  <div class="standard-card-header">
    <h5 class="standard-card-title">Card Title</h5>
  </div>
  <div class="standard-card-body">
    Card content goes here
  </div>
  <div class="standard-card-footer">
    <button class="standard-btn standard-btn-primary">Action</button>
  </div>
</div>
```

### Buttons

Button variations:

```html
<!-- Primary button -->
<button class="standard-btn standard-btn-primary">Primary Action</button>

<!-- Secondary button -->
<button class="standard-btn standard-btn-secondary">Secondary Action</button>

<!-- Outline button -->
<button class="standard-btn standard-btn-outline-primary">Outline Button</button>
```

### Form Elements

Standard form components:

```html
<div class="standard-form-group">
  <label class="standard-form-label" for="exampleInput">Label</label>
  <input type="text" class="standard-form-control" id="exampleInput">
</div>
```

### Status Indicators

Use badges for status indication:

```html
<span class="standard-badge standard-badge-success">Success</span>
<span class="standard-badge standard-badge-danger">Error</span>
<span class="standard-badge standard-badge-warning">Warning</span>
```

## Azure-Style Components

This section contains components that follow Azure Portal design patterns for a consistent enterprise-level UI experience.

### Azure Cards

Azure-style cards feature a clean, flat design with subtle shadows and hover effects:

```html
<div class="azure-card">
  <div class="azure-card-header">
    <h5 class="azure-card-title">Resource Overview</h5>
  </div>
  <div class="azure-card-body">
    <p>This card follows Azure Portal design patterns with subtle shadows and clean lines.</p>
  </div>
  <div class="azure-card-footer">
    <button class="azure-btn azure-btn-primary">Configure</button>
    <button class="azure-btn azure-btn-secondary">Cancel</button>
  </div>
</div>
```

### Azure Panels

Azure panels are used for informational content with color-coded borders:

```html
<div class="azure-panel">
  <h5>Default Panel</h5>
  <p>This panel provides contextual information.</p>
</div>

<div class="azure-panel azure-panel-info">
  <h5>Information Panel</h5>
  <p>This panel provides important information.</p>
</div>

<div class="azure-panel azure-panel-success">
  <h5>Success Panel</h5>
  <p>This panel indicates a successful operation.</p>
</div>

<div class="azure-panel azure-panel-warning">
  <h5>Warning Panel</h5>
  <p>This panel warns about potential issues.</p>
</div>

<div class="azure-panel azure-panel-danger">
  <h5>Danger Panel</h5>
  <p>This panel alerts about critical issues.</p>
</div>
```

### Azure Blade Layout

The Azure blade layout is ideal for complex forms and configuration screens:

```html
<div class="azure-blade">
  <div class="azure-blade-header">
    <h5 class="azure-blade-title">Configuration</h5>
  </div>
  <div class="azure-blade-body">
    <div class="azure-content-section">
      <div class="azure-content-section-header">
        <h6 class="azure-content-section-title">General Settings</h6>
        <p class="azure-content-section-subtitle">Configure basic application parameters</p>
      </div>
      <!-- Form fields go here -->
    </div>
  </div>
</div>
```

### Azure Grid System

The Azure grid system uses CSS Grid for modern layouts:

```html
<div class="azure-grid azure-grid-3col">
  <div class="azure-card">
    <div class="azure-card-header">
      <h5 class="azure-card-title">Item 1</h5>
    </div>
    <div class="azure-card-body">
      <p>Grid item content</p>
    </div>
  </div>
  <div class="azure-card">
    <div class="azure-card-header">
      <h5 class="azure-card-title">Item 2</h5>
    </div>
    <div class="azure-card-body">
      <p>Grid item content</p>
    </div>
  </div>
  <div class="azure-card">
    <div class="azure-card-header">
      <h5 class="azure-card-title">Item 3</h5>
    </div>
    <div class="azure-card-body">
      <p>Grid item content</p>
    </div>
  </div>
</div>
```

### Azure Form Controls

Azure-style form controls feature clean borders and focused states:

```html
<div class="azure-form-group">
  <label for="azureInput">Input Label</label>
  <input type="text" class="azure-form-control" id="azureInput" placeholder="Enter value">
</div>

<div class="azure-form-group">
  <label for="azureSelect">Select Option</label>
  <select class="azure-form-control" id="azureSelect">
    <option>Option 1</option>
    <option>Option 2</option>
    <option>Option 3</option>
  </select>
</div>
```

## Utility Classes

### Display Utilities

```html
<div class="d-none">Hidden on all screen sizes</div>
<div class="d-none d-md-block">Hidden on mobile, visible on desktop</div>
<div class="d-md-none">Visible on mobile, hidden on desktop</div>
```

### Flex Utilities

```html
<div class="d-flex justify-content-between align-items-center">
  <div>Left content</div>
  <div>Right content</div>
</div>
```

### Spacing Utilities

```html
<div class="m-3">Margin 1rem all around</div>
<div class="mx-3">Horizontal margin 1rem</div>
<div class="my-3">Vertical margin 1rem</div>
<div class="mt-3">Top margin 1rem</div>
<div class="p-3">Padding 1rem all around</div>
```

### Text Utilities

```html
<p class="text-primary">Primary text color</p>
<p class="text-muted">Muted text color</p>
<p class="text-truncate">This text will be truncated if it's too long</p>
```

## Accessibility Guidelines

### Focus States

All interactive elements should have visible focus states:

```css
.focus-visible:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}
```

### Screen Reader Support

Use the `sr-only` class for content that should be available to screen readers but not visible:

```html
<span class="sr-only">Instructions for screen readers</span>
```

### Semantic HTML

Always use semantic HTML elements:
- `<button>` for clickable actions
- `<a>` for navigation links
- Heading tags (`<h1>` through `<h6>`) for hierarchical headings
- `<label>` elements properly associated with form controls

## Responsive Design

### Mobile-First Approach

WhiteLabelRAG follows Bootstrap's mobile-first approach. Start with the mobile layout, then enhance for larger screens:

```html
<div class="standard-col-12 standard-col-md-6">
  <!-- Full width on mobile, half width on tablets and up -->
</div>
```

### Responsive Utilities

Hide/show elements based on screen size:

```html
<div class="d-none d-md-block">Desktop only</div>
<div class="d-md-none">Mobile only</div>
```

### Touch Targets

Ensure all interactive elements have adequate touch targets (minimum 44x44px) for mobile users.

## Implementation Example

```html
<div class="container">
  <div class="standard-row mt-4">
    <div class="standard-col-12 standard-col-md-6">
      <div class="standard-card">
        <div class="standard-card-header">
          <h5 class="standard-card-title">Document Upload</h5>
        </div>
        <div class="standard-card-body">
          <div class="standard-form-group">
            <label class="standard-form-label" for="documentUpload">Select a document</label>
            <input type="file" class="standard-form-control" id="documentUpload">
          </div>
        </div>
        <div class="standard-card-footer">
          <button class="standard-btn standard-btn-primary">Upload</button>
        </div>
      </div>
    </div>
    <div class="standard-col-12 standard-col-md-6">
      <div class="standard-card">
        <div class="standard-card-header">
          <h5 class="standard-card-title">Status</h5>
        </div>
        <div class="standard-card-body">
          <div class="d-flex align-items-center">
            <span class="standard-badge standard-badge-success me-2">Active</span>
            <span class="text-muted">System is operational</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```
