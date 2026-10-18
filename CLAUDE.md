# Meal Planner — working rules

Greg's weekly meal plan + gym app. Two copies ship from this one source:
**GitHub Pages** (`index.html`, the real document) and a **Claude artifact**
(a stripped `<body>` fragment). Both must be updated on every change.

- Live: https://arockonalens.github.io/mealplan/
- Artifact: https://claude.ai/artifact/Fa7LmgpkupEjoUkgvteGY4

This repo is deliberately **not** in iCloud — iCloud sync corrupts `.git`.

---

## Standing constraints — check these on EVERY recipe added

These are Greg's, learned the hard way. Do not quietly drop one because a new
recipe or an inspiration menu wants to.

**The eating**
- Two people. Australia, Coles/Woolworths prices and pack sizes.
- **No breakfast.** Lunch + dinner + snacks only. A "breakfast" dish from an
  external menu becomes lunch.
- **Goal is fat loss with muscle gain.** 185 cm, 70 kg, 35, trains 5 days,
  desk job with a lot of walking.
- **Protein target 112–154 g/day** (1.6–2.2 g/kg). Plans have been landing
  85–100. Say so plainly when a week lands short; do not round up and hope.
- **Anything fat-heavy must be flagged before it ships**, with calories per
  serve. A 343 kcal / 14 g fat slice went into a weight-loss week once because
  it was on a menu he pasted. He caught it. Don't repeat that.
- **No lentils** — they bloat him. **Chickpeas are fine and he loves them.**
- Dairy limited *in dishes*; no daily glass of milk.
- **Pack sizes must be buyable**: 500 g / 1 kg trays. Never "700 g of mince".
  He is not going to the deli.
- **No repeats week to week.** Same dinner, same dip, same snack three weeks
  running gets rejected. Rotate the focaccia topping too.
- Equipment: oven, cooktop, air fryer, slow cooker, stand mixer.

**The gym**
- **No legs. Ever.** He hates them.
- **No Friday.** Current split: Mon chest, Tue back+abs, Wed arms,
  Thu shoulders+abs, Fri rest, Sat upper, Sun rest.
- No warm-up or stretching sections — he removed them.
- His machines: **Vertical Traction** (the pulldown), **Low Row**, and the
  **Abdominal Crunch**. Build around what he actually uses.
- Exercise images must be **public domain** (free-exercise-db). Never
  reproduce Technogym product photography.

---

## How to work on this

**Act, don't block.** State assumptions and deliver. He has said directly that
asking questions and waiting is "blocking us". If a detail is unknown, pick a
sensible value, say what you picked, and build.

**Methods are instructions, not essays.** No justification, no mechanism, no
asides. Keep only what changes what he does ("chickpeas cooked in plain water
first", "bare simmer never a boil"). Target ~12 words a step.

**Measurements**: cups lead, grams in small type beside them. The
**Australian tablespoon is 20 ml = 4 tsp**, not 3. Only things people scoop
convert — never meat, eggs, tins or whole vegetables.

**Look at visual changes in a browser before shipping.** A 4-child row in a
3-column grid shipped once and he had to report it.

---

## Pre-ship audit — run it, don't eyeball it

Every one of these has caught a real bug. Run them all after any plan change.

```bash
# 1. Page script parses
python3 -c "import re,io,sys; s=io.open('index.html',encoding='utf-8').read(); \
sys.stdout.write(re.search(r'<script>(.*)</script>', s, re.S).group(1))" > /tmp/p.js && node --check /tmp/p.js

# 2. Every data-meal resolves to a card, no dangling links
# 3. Ingredient totals vs the shop list  (eggs, meat, tins, flour)
# 4. Batch yield vs meal slots: portions x people x days
# 5. Snack yield vs days  (a 10-slice loaf does not cover 14 servings)
# 6. Protein per person per day, per day, and flag the low ones
# 7. Shop subtotals + total recomputed from data-p IN CODE, never by hand
# 8. Stale references after any swap: old dish names left in the prep tab,
#    shop notes, spice table, notes placeholder
# 9. Every img/ file referenced actually exists
```

**Recompute the shop total in code.** Hand-quoted figures have been wrong
three times ($83 vs $92, $110 vs $124, $109 vs $116).

**Verifying the live site**: wait on a marker that exists **only in the new
version**. Twice a wait-condition matched text present in both and reported
success against a stale page.

---

## Shipping

```bash
git add -A && git commit -F /tmp/msg.txt && git push origin HEAD
```

Use a **message file**, not `-m` — quotes in the message have broken the
shell. Then rebuild the artifact fragment (body + fonts links + style,
favicon rewritten absolute) and publish it to the artifact URL above.
GitHub Pages takes about 30–60 seconds.

The page has a **network-first service worker** (`sw.js`) so the phone
home-screen shortcut always gets the newest version and still works offline.
Registration is guarded to `github.io` so the artifact copy never registers
it. A freshness stamp at the foot of the page reads `document.lastModified`.
