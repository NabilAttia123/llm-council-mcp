# Theme Architecture

This document describes the theming system implemented in LLM Council, including how it works, the color palettes for both light and dark modes, and how to integrate theming into future components.

## Overview

The application uses a **CSS Custom Properties (CSS Variables)** based theming system that allows users to switch between light and dark modes. The theme preference is persisted to `localStorage` and automatically applied on page load.

## Architecture

### Theme State Management

Theme state is managed in the root React component ([App.jsx](file:///Users/nabilattia/My/developer/llm-council/frontend/src/App.jsx)):

```javascript
const [theme, setTheme] = useState(() => {
  return localStorage.getItem('theme') || 'light';
});

useEffect(() => {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}, [theme]);
```

**Key Points:**
- Theme state initializes from `localStorage`, defaulting to `'light'`
- Theme changes apply a `data-theme` attribute to the document root (`<html>`)
- The `data-theme` attribute value is either `"light"` or `"dark"`
- Theme preference persists across sessions via `localStorage`

### CSS Variable System

All theme colors are defined as CSS custom properties in [index.css](file:///Users/nabilattia/My/developer/llm-council/frontend/src/index.css).

**Implementation:**
```css
:root {
  /* Light theme colors (default) */
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  /* ... more variables */
}

[data-theme="dark"] {
  /* Dark theme colors (override when data-theme="dark") */
  --bg-primary: #1a1a1a;
  --bg-secondary: #242424;
  /* ... more variables */
}
```

When the `data-theme` attribute changes, all CSS variables automatically update, triggering smooth transitions throughout the application.

## Color Palettes

### Theme Variables Reference

| Variable Name | Purpose | Light Mode | Dark Mode |
|---------------|---------|------------|-----------|
| `--bg-primary` | Primary background (cards, containers) | `#ffffff` | `#1a1a1a` |
| `--bg-secondary` | Secondary background (page background) | `#f5f5f5` | `#242424` |
| `--bg-tertiary` | Tertiary background (loading states, subtle containers) | `#e8e8e8` | `#2e2e2e` |
| `--text-primary` | Primary text color | `#333333` | `#e0e0e0` |
| `--text-secondary` | Secondary text (labels, metadata) | `#666666` | `#b0b0b0` |
| `--text-muted` | Muted text (placeholders, disabled states) | `#999999` | `#808080` |
| `--border-color` | Borders and dividers | `#e0e0e0` | `#3a3a3a` |
| `--hover-bg` | Hover state backgrounds | `#ebebeb` | `#333333` |
| `--code-bg` | Code block backgrounds | `#f5f5f5` | `#2e2e2e` |
| `--quote-border` | Blockquote border color | `#dddddd` | `#4a4a4a` |
| `--quote-text` | Blockquote text color | `#666666` | `#a0a0a0` |

### Light Theme Palette

```css
:root {
  --bg-primary: #ffffff;      /* Pure white */
  --bg-secondary: #f5f5f5;    /* Very light gray */
  --bg-tertiary: #e8e8e8;     /* Light gray */
  --text-primary: #333333;    /* Dark gray (main text) */
  --text-secondary: #666666;  /* Medium gray */
  --text-muted: #999999;      /* Light gray text */
  --border-color: #e0e0e0;    /* Light borders */
  --hover-bg: #ebebeb;        /* Hover state */
  --code-bg: #f5f5f5;         /* Code backgrounds */
  --quote-border: #dddddd;    /* Quote border */
  --quote-text: #666666;      /* Quote text */
}
```

### Dark Theme Palette

```css
[data-theme="dark"] {
  --bg-primary: #1a1a1a;      /* Very dark gray */
  --bg-secondary: #242424;    /* Dark gray */
  --bg-tertiary: #2e2e2e;     /* Medium dark gray */
  --text-primary: #e0e0e0;    /* Light gray (main text) */
  --text-secondary: #b0b0b0;  /* Medium light gray */
  --text-muted: #808080;      /* Medium gray text */
  --border-color: #3a3a3a;    /* Dark borders */
  --hover-bg: #333333;        /* Hover state */
  --code-bg: #2e2e2e;         /* Code backgrounds */
  --quote-border: #4a4a4a;    /* Quote border */
  --quote-text: #a0a0a0;      /* Quote text */
}
```

## Implementation Guidelines

### For New Components

When creating new components that should support theming:

#### 1. Use CSS Variables for All Colors

**✅ DO:**
```css
.my-component {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}
```

**❌ DON'T:**
```css
.my-component {
  background-color: #ffffff;  /* Hard-coded color */
  color: #333333;             /* Won't adapt to dark mode */
  border: 1px solid #e0e0e0;  /* No theme support */
}
```

#### 2. Add Smooth Transitions

Add transitions to color properties for smooth theme switching:

```css
.my-component {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
}
```

**Recommended transition duration:** `0.3s` for consistent UX

#### 3. Choose the Right Variable

Use semantic variable names based on the element's purpose:

- **Backgrounds:**
  - `--bg-primary`: Cards, modals, primary containers
  - `--bg-secondary`: Page backgrounds, subtle sections
  - `--bg-tertiary`: Loading states, disabled backgrounds
  
- **Text:**
  - `--text-primary`: Main content, headings
  - `--text-secondary`: Labels, metadata, secondary info
  - `--text-muted`: Placeholders, less important text

- **Borders:**
  - `--border-color`: All borders and dividers

- **Interactive States:**
  - `--hover-bg`: Hover backgrounds for buttons, list items

#### 4. Test Both Themes

Always test your component in both light and dark modes to ensure:
- Sufficient contrast ratios (WCAG AA: 4.5:1 for normal text)
- Readability in both themes
- Consistent visual hierarchy
- Proper transition effects

### Adding New Theme Variables

If you need new color variables for specific use cases:

1. Add to both `:root` and `[data-theme="dark"]` in `index.css`
2. Use descriptive, semantic names (e.g., `--success-bg`, `--error-text`)
3. Follow the existing naming convention
4. Document the new variable in this file

**Example:**
```css
:root {
  --success-bg: #d4edda;
  --error-text: #721c24;
}

[data-theme="dark"] {
  --success-bg: #1e4620;
  --error-text: #f8d7da;
}
```

## Theme Toggle Component

The theme toggle is implemented in the [Toolbar](file:///Users/nabilattia/My/developer/llm-council/frontend/src/components/Toolbar.jsx) component:

- Shows a **moon icon** in light mode (click to enable dark mode)
- Shows a **sun icon** in dark mode (click to enable light mode)
- Includes hover animations and accessibility attributes
- Theme state is passed down from `App.jsx`

## Best Practices

### 1. Avoid Hard-Coded Colors
Never use hard-coded hex/rgb values in component stylesheets. Always use CSS variables.

### 2. Maintain Contrast
Ensure text remains readable on all backgrounds in both themes. Use browser DevTools to check contrast ratios.

### 3. Consistent Transitions
Use `0.3s ease` for theme-related transitions to maintain consistency across the app.

### 4. Semantic Variables
Choose variables based on semantic meaning, not visual appearance. This ensures proper theme adaptation.

### 5. Test Edge Cases
Test components with:
- Long text content
- Empty states
- Loading states
- Error states
- All in both themes

## Browser Support

CSS Custom Properties are supported in all modern browsers:
- Chrome/Edge 49+
- Firefox 31+
- Safari 9.1+

The theme system gracefully degrades to light mode in unsupported browsers.

## Future Enhancements

Potential improvements to the theme system:

1. **System Preference Detection:**
   ```javascript
   const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches 
     ? 'dark' 
     : 'light';
   ```

2. **Additional Themes:**
   - High contrast mode
   - Custom color schemes
   - User-defined themes

3. **Theme-Specific Images:**
   - Different logo colors per theme
   - Theme-aware illustrations

4. **Reduced Motion:**
   - Respect `prefers-reduced-motion` for transitions
