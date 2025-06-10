# WhiteLabelRAG Color System

This folder contains the WhiteLabelRAG application's color system. The system provides a standardized approach to color usage throughout the application.

## Files

- `color-palette.css`: Defines the complete color palette as CSS variables
- `COLOR_PALETTE_GUIDE.md`: Documentation on how to use the color variables
- `color-examples.css`: Example components using the color system (for reference)

## Implementation Details

The color system follows a hierarchical structure:

1. **Core Colors**: Base colors like white, black, navy, and grayscale
2. **Semantic Colors**: Meaningful abstractions like text-primary, bg-primary, etc.
3. **Component Colors**: Specialized variables for specific UI components

This approach separates the specific colors from their usage, making it easier to maintain consistent styling and update the theme in the future.

## Usage

To use the color system:

1. Reference the semantic color variables in your CSS:
   ```css
   .my-component {
     background-color: var(--bg-primary);
     color: var(--text-primary);
     border: 1px solid var(--border-primary);
   }
   ```

2. For specific components or states, use the specialized variables:
   ```css
   .status.success {
     background-color: var(--status-success-bg);
     color: var(--status-success-text);
   }
   ```

3. Avoid using raw hex color values or the direct color variables (like --color-white) when possible. Instead, use the semantic variables which express the purpose of the color.

## Customization

If you need to customize the color scheme:

1. Edit the values in `color-palette.css` 
2. Maintain the mapping between core colors and semantic variables

See the `COLOR_PALETTE_GUIDE.md` for more detailed usage information.
