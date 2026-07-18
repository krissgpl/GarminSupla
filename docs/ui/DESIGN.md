# GarminSupla Design System

## Design Principles
Keep it simple.
One primary action per screen.
Use Bootstrap before writing custom CSS.
Consistency over creativity.
Accessibility is not optional.

## Philosophy

GarminSupla should provide a clean, modern and responsive user interface.

The application should focus on:

- Simplicity
- Security
- Speed

The interface should guide the user through the configuration process step by step without overwhelming them.

---

## Themes

Supported themes:

- System (default)
- Light
- Dark

The application should automatically follow the operating system theme whenever possible.

---

## Layout

Every page should use the same layout.

```
Header

↓

Centered Content

↓

Footer
```

The content should always be displayed inside a centered Bootstrap Card.

---

## Colors

The application should use Bootstrap color palette whenever possible.

Primary colors:

- Primary
- Success
- Warning
- Danger
- Secondary

Custom CSS should only define GarminSupla-specific colors when Bootstrap defaults are not sufficient.

---

## Typography

Use Bootstrap typography.

Preferred hierarchy:

- display-* (landing pages only)
- h1
- h2
- h3
- body
- small

Avoid custom font sizes whenever Bootstrap utilities are sufficient.

---

## Components

Preferred components:

- Cards
- Buttons
- Forms
- Alerts
- Badges
- Tables
- Progress Bars

Bootstrap components should always be preferred over custom implementations.

---

## Icons

Bootstrap Icons will be used throughout the application.

Icons should improve usability and never replace text.

---

## Accessibility

The interface should remain readable and usable in both Light and Dark themes.

General rules:

- sufficient color contrast
- keyboard-friendly navigation
- meaningful button labels
- responsive layout

---

## Responsive Design

GarminSupla should work correctly on:

- Desktop
- Tablet
- Mobile

Bootstrap responsive grid should be preferred over custom layouts.

---

## Custom CSS

Bootstrap is responsible for layout and components.

Custom CSS should only define GarminSupla identity.

Avoid overriding Bootstrap unless necessary.

---

## Future Ideas

- Light / Dark / System theme
- Multi-language support
- Progressive Web App (PWA)
- Dashboard
- Notifications
- Garmin watch preview
- User profile

---

## Decisions

### 2026-07-18

- Bootstrap 5 selected
- Bootstrap Icons selected
- Bootstrap Cards selected
- Bootstrap Forms selected
- Bootstrap Buttons selected
- Bootstrap-first approach approved
- System / Light / Dark theme approved
- Header / Content / Footer layout approved
