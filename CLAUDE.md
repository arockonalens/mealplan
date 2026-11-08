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
- **No pork as a cut** — mince, loin, chops, roast, belly. Stated 1 Nov 2026
  after a pork loin dish had already been built into a week.
  **Bacon, ham and chorizo are fine** — he confirmed that immediately after,
  so the line is fresh pork, not cured. Do not widen it back out.
- **No lentils** — they bloat him. **Chickpeas are fine and he loves them.**
- Dairy limited *in dishes*; no daily glass of milk.
- **Pack sizes must be buyable**: 500 g / 1 kg trays. Never "700 g of mince".
  He is not going to the deli.
- **No repeats week to week — ever, not just three weeks running.** Before
  choosing a single dish, dump every title the project has ever shipped and
  pick from outside it:

  ```bash
  for c in $(git rev-list --all); do git show $c:index.html 2>/dev/null \
    | grep -o 't:"[^"]*"'; done | sed 's/t:"//;s/"$//' | sort -u
  ```

  That is ~103 dishes as of 1 Nov 2026. A renamed version of one on the list
  still counts as a repeat. His words: *"you are being lazy, we can rotate
  receipes but you need to be orignal each week."* Pick a cuisine region the
  recent weeks have not used and favour proteins never used at all.
- Equipment: oven, cooktop, air fryer, slow cooker, stand mixer.

**The gym**
- **No legs. Ever.** He hates them.
- **No Friday.** Current split, since 5 Nov 2026: **Mon chest heavy,
  Tue back+abs, Wed chest upper, Thu shoulders+abs, Fri rest,
  Sat chest lower + back, Sun rest.**
- **Chest is the priority.** He asked for it directly: *"for fitness, i
  really just want to focus on chest."* Chest runs **three times a week**,
  never on consecutive days, and the three sessions are deliberately
  different (heavy / upper / lower). Arms lost their day to make room.
- **Back stays twice a week and is not negotiable** — Tuesday and the back
  half of Saturday. Pressing three times a week with no pulling rolls the
  shoulders forward. Do not let a future "more chest" request delete it.
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

**Do not oversell a number.** "High protein" was claimed for a sweet snack
that had 8.8 g a square — less than the loaf it replaced. He checked. State
what a thing is good at and what it is not, with the figure beside it.

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

**Computed at runtime, never hand-edit:** `#t-total`, `#r-total`,
`#t-permeal`, `#r-owed`, `#r-lines`, every `.r-price`, every `.r-qty`, each
`[data-sub]`. **Hand-maintained and silently stale:** `#t-pro`, `Hands-on
Sun`, `Energy`, and every `.rpro` / `data-pro` on a row.

**Recompute the shop total in code.** Hand-quoted figures have been wrong
three times ($83 vs $92, $110 vs $124, $109 vs $116).

**Verifying the live site**: wait on a marker that exists **only in the new
version**. Twice a wait-condition matched text present in both and reported
success against a stale page.

---

## This rebuilds itself every Sunday

Scheduled task `sunday-meal-plan` (`~/.claude/scheduled-tasks/`), Sundays at
07:10 local, builds and ships the whole week without being asked. It only
fires while the desktop app is open — otherwise on next launch. Greg asked
for this on 1 Nov 2026: *"Go build do this every Sunday without me telling
you."* Do not stop to ask whether to build the week.

## The page is a mobile app, not a web page (8 Nov 2026)

Greg uses this on an iPhone, installed to the home screen. Treat it as an app:

- **Navigation is a fixed bottom tab bar** (`.tabbar` / `.tab`), inside
  `env(safe-area-inset-bottom)`, where a thumb reaches. It is **not** a row
  under the header any more. Six tabs, icon + label, 44px minimum targets.
- **The nav markup must sit above the inline `<script>`.** The script runs
  immediately and collects `.tab` at parse time; put the nav after it and the
  query returns nothing, `show()` no-ops silently, **and nothing throws**.
  That bug shipped once and was only caught by clicking a tab in a test.
- **Each tab keeps its own scroll position** (`sessionStorage`,
  `cu-scroll-v1`) and restores it with `behavior:"instant"`. It must be
  instant: `html{scroll-behavior:smooth}` is set, so a plain `scrollTo`
  animates the new panel in front of you on every tab change.
- **Re-tapping the active tab scrolls to top**, smoothly. That one is meant
  to animate.
- `body` carries `padding-bottom: calc(52px + safe-area-inset-bottom)` so the
  bar never covers content. The share sheet is z-index 60 and the scrim 50,
  so the tab bar must stay **below 50** (it is 45).

Test it at 390x844 before shipping. Desktop Chrome will not resize a
maximised window — replace `document.documentElement.innerHTML` with a
same-origin 390x844 iframe and drive that.

## Techniques worth reaching for

- **Velveting** — bicarb through raw sliced meat 40 min, **rinsed off**,
  then cornflour + egg white, then a second dry dusting, fried at 120–140 °C.
  It rescues cheap, tough cuts. **On a good cut it is a waste** — say so
  rather than using it because it is new.

## Recipe format — grouped ingredients, method only in the method (8 Nov 2026)

This is the format Greg asked for, and it is now the format for every recipe,
every week. Do not go back to a flat list.

- **`i:` is grouped by component**, the way a recipe names its own parts:
  `[["Velveting marinade",[[q,u,name],...]],["Sauce",[...]],["Stir-fry",[...]]]`.
  A quantity of **0 renders no number** — for "oil, for flash-frying" or
  "rice, to serve". Fractions are **real numbers** (`0.5`, `0.25`); `qty()`
  prints them as ½ and ¼. Never put the fraction in the name string.
- **`s:` is `[title, html, timerMinutes]`.** The title is one or two words
  (Slice, Marinate, Flash-fry). **Each step names its own ingredients**, so he
  never has to read back up to the list while his hands are wet.
- **`n:` is `[title, html]`** — every fact, flag, macro, caveat, correction and
  substitution. **Nothing factual belongs in a method step.** Greg told me
  "i dont need facts in the method" weeks ago and it crept straight back in.
- **`src:`** credits the source when the recipe is someone else's.

Prep words in an ingredient name ("cabbage, shredded") are safe: the shop
cross-check normalises on the part before the first comma or em dash, both
sides, so a prep word cannot silently break a quantity match.

### Why this format exists — the 460 g mistake

I flattened the Goose Theory velveting recipe into one prose ingredient array
and prose steps. Once it was flat **every number looked like a number I was
free to scale**, so when Greg's beef came in at 460 g instead of 500 g I
"rescaled" it and got five things wrong at once:

- white pepper at **1 tsp, four times** the source's ¼ tsp
- **a whole bunch** of spring onions instead of the source's 3
- marinade soy and sauce soy **merged into one 45 ml line** (it is 1 tbsp + 2 tbsp)
- the **cornflour slurry dropped entirely** — then I wrote a note telling him to
  hold sauce back to stop it going loose, which is what the slurry is for
- worst: the recipe has **two bicarb routes** — ½ tsp that *stays in*, and 1½ tsp
  that gets *washed off*. I welded them into one method, used the washed-off
  dose, and then invented a "round the dose down, never up" rule for it. That
  rule is backwards: the dose only matters on the version that stays in.

**Scaling the main protein does not scale tablespoons.** At 460 g versus 500 g
the only line that changes is the beef. Keep the source's structure and the
source's quantities, and the card stays recognisable as that recipe.

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
