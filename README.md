# Meal Planner

A seven-day high-protein meal plan for two, built around one Sunday batch cook
and a single Coles/Woolworths shop.

Single self-contained `index.html` — no build step, no dependencies, no bundler.
Fonts load from Google Fonts; everything else is inline.

## Features

- Seven day dockets, lunch / dinner / savoury snack / sweet snack
- Tap any meal for a cook sheet: scaled ingredients, method, per-step timers
- Pax counter (1–6) rescales the whole shopping list and every recipe
- Adjustable daily protein target with per-day bars
- Shopping receipt with running total and tick-off state
- All state persists in localStorage, per device

## Local preview

    python3 -m http.server 8000

Then open <http://localhost:8000>.

## Deploy

Pushed to `main`, served by GitHub Pages from the repository root.
