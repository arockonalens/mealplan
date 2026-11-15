# -*- coding: utf-8 -*-
"""Build the week into index.html, and audit it before it goes in.

Lives in the repo on purpose. It used to live in a session scratchpad, which
gets wiped between sessions — and when it was wiped the audit below stopped
running without anything saying so. Run it from anywhere:

    python3 -I build/week.py

It reads the recipe data straight out of index.html, applies SWAP, regenerates
the day rail / shop list / prose from the tables here, asserts the week is
sound, and writes index.html back. Nothing is hand-counted.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "index.html")

# --------------------------------------------------------------- the week
# key: (title, protein/serve, kcal/serve, portions or None for a snack)
T = {
 "cheeks":  ("Cider-braised beef cheeks, fennel and apple", 56, 715,  2),
 "wings":   ("Lemon pepper wings",                          42, 600,  8),
 "harvest": ("Harvest chicken bowl, apple and pecan",       55, 588,  6),
 "grinder": ("Italian grinder sliders",                     42, 562,  6),
 "salmon":  ("Blackened salmon, charred corn salsa",        43, 525,  6),
 "edamame": ("Chilli-salt edamame",                         15, 170, None),
 "parfait": ("Apple cinnamon yoghurt parfait",              17, 235, None),
}
DAYS = [
 ("Sun", "Braise day",          "harvest", "cheeks"),
 ("Mon", "Blackened fresh",     "wings",   "salmon"),
 ("Tue", "Air fryer",           "grinder", "wings"),
 ("Wed", "Second salmon",       "harvest", "salmon"),
 ("Thu", "Air fryer",           "grinder", "wings"),
 ("Fri", "Out of the freezer",  "harvest", "salmon"),
 ("Sat", "Last of it",          "grinder", "wings"),
]
SNACK_P = T["edamame"][1] + T["parfait"][1]
SNACK_K = T["edamame"][2] + T["parfait"][2]
BAND = (112, 154)

# --------------------------------------------------- the dish being swapped
# Replaces whatever is currently keyed "mongolian" (last week's velveted beef,
# which Greg had already eaten). Source is Tim Laielli's 13 Nov cider braise,
# moved off pulled chicken because four pulled chickens have already shipped.
SWAP_OUT = "mongolian"
SWAP_IN = u'''"cheeks":{r:"Dinner \u00b7 2 portions",t:"Cider-braised beef cheeks, fennel and apple",p:56,c:42,sv:"2 portions \u00b7 tonight \u00b7 3\u00bd hours, nearly all of it unattended",m:["Slow cooker","3\u00bd hr","Flag \u00b7 715 kcal"],
      src:"Tim Laielli, the bare minimum, 13 Nov \u2014 his cider braise, moved onto beef cheeks",
      kp:"Better the next day \u00b7 freezes 3 months flat in its juices",al:"mustard",
      i:[["The rub",[
            [500,"g","beef cheeks, trimmed \u2014 one pack, about two"],
            [1,"ea","tsp salt"],
            [2,"ea","tsp smoked paprika"],
            [1,"ea","tbsp brown sugar"],
            [1,"ea","tsp black pepper"]]],
         ["The braise",[
            [1,"ea","fennel bulb, sliced thin"],
            [1,"ea","apple, sliced thin"],
            [250,"ml","cloudy apple juice"],
            [2,"ea","tbsp apple cider vinegar"],
            [2,"ea","tbsp Dijon mustard"],
            [4,"ea","sprigs thyme"],
            [2,"ea","bay leaves"]]],
         ["To serve",[
            [600,"g","potatoes, peeled and chunked"]]]],
      s:[["Rub","Salt, smoked paprika, brown sugar and pepper mixed together, then rubbed all over the cheeks.",0],
         ["Layer","Fennel and apple scattered over the base of the pot. Cheeks laid on top of them.",0],
         ["Pour","Apple juice, vinegar and Dijon whisked, then poured <b>around</b> the cheeks rather than over them. Thyme and bay tucked in.",0],
         ["Braise","Lid on. <b>Slow cooker on low, or the oven at 165 \u00b0C.</b> Done when a fork turns in the meat with no resistance.",210],
         ["Mash","Potatoes boiled in well-salted water until tender.",18],
         ["Reduce","Cheeks lifted out. The liquid simmered hard on the stove until it reduces by about a third.",10],
         ["Finish","<b>A ladle of the reduced juices through the mash instead of butter.</b> Cheeks back in with the fennel and apple.",0],
         ["Serve","Cheeks over the mash, the braised fennel and apple alongside.",0]],
      n:[["Why beef cheeks and not Tim\u2019s pulled chicken","His version is pulled chicken. <b>Four pulled chickens have already shipped</b> \u2014 harissa pulled chicken, harissa pulled thigh, pulled chicken bowl, pulled chicken slaw bowl. <b>Beef cheek has never been used here</b>, and it is what a cider braise actually wants: it is almost all collagen, so it goes silky instead of stringy."],
         ["Cloudy apple juice, not cider","<b>Tim\u2019s \u201cunfiltered apple cider\u201d is American for cloudy apple juice.</b> The alcoholic cider at Coles is a different drink and would leave this sharp and thin."],
         ["Fat flag \u2014 715 kcal, 20 g fat a serve","Reasonable for a braise, and the mash is most of the carbs. <b>No butter in the mash</b> \u2014 the reduced braising liquid does the job better and keeps about 110 kcal and 12 g of fat a serve off the plate."],
         ["It cannot be hurried","Three and a half hours, and under-braised cheek is rubbery rather than tough. Nearly all of it is unattended: about 20 minutes of actual work."],
         ["Better tomorrow","If you can, braise it a day ahead \u2014 it is better reheated. Freezes flat in its juices for three months."]]}'''

# ------------------------------------------------------------- the shopping
# (name, qty, unit, hint, price, what it is for, recipe-ingredient key or None)
# Price is a read-out, never a constraint — see CLAUDE.md.
CATS = [
 ("Protein", [
  ("Chicken wings",2500,"g","\u00b7 one 2 kg and one 500 g tray",20.00,"Lemon pepper \u2014 four dinners, cooked on the night","chicken wings"),
  ("Chicken breast",1500,"g","",19.00,"The harvest bowls \u2014 three lunches","chicken breast"),
  ("Beef cheeks",500,"g","\u00b7 one pack, about two",14.00,"<b>Tonight</b> \u2014 the cider braise","beef cheeks"),
  ("Salmon fillets",1200,"g","",42.00,"Three dinners \u2014 freeze a third on Sunday","salmon fillets"),
  ("Shaved ham",600,"g","",12.00,"The grinders \u2014 cured, so it is fine","shaved ham"),
  ("Salami",200,"g","",6.00,"The grinders \u2014 200 g, not 300; it is the fattiest thing in them","salami"),
 ]),
 ("Dairy", [
  ("Provolone",200,"g","",7.00,"The grinders \u2014 Swiss if there is no provolone","provolone"),
  ("Greek yoghurt, 0% fat",2000,"g","",12.00,"The parfaits \u2014 0%, not the 10% stuff","Greek yoghurt"),
 ]),
 ("Produce", [
  ("Potatoes",2600,"g","\u00b7 a 3 kg bag",8.00,"Wedges with the wings, and tonight\u2019s mash","potatoes"),
  ("Sweet potatoes",900,"g","",3.50,"Roasted, into the harvest bowls","sweet potatoes"),
  ("Fennel",1,"ea","",4.00,"<b>Tonight</b> \u2014 it goes under the cheeks","fennel bulb"),
  ("Apples",10,"ea","",8.00,"Three to the bowls, six to the parfaits, one to the braise","apples"),
  ("Cos lettuce",4,"ea","",8.00,"Two for the grinder salad, two for the bowls","cos lettuce"),
  ("Corn cobs",6,"ea","",7.50,"Two a night, charred for the salsa","corn cobs"),
  ("Lemons",8,"ea","",6.00,"The salmon, the wings and the edamame","lemons"),
  ("Tomatoes",600,"g","",4.00,"Grinder salad and the corn salsa","tomatoes"),
  ("Red onions",4,"ea","",2.50,"Two grinders, two salsas","red onions"),
  ("Cabbage",1,"ea","",2.50,"The wing slaw",None),
  ("Carrots",500,"g","",1.50,"The slaw","carrots"),
  ("Chives",2,"ea","",6.00,"The bowls and the salsa","bunch chives"),
  ("Thyme",1,"ea","",3.50,"<b>Tonight</b> \u2014 four sprigs into the braise",None),
 ]),
 ("Frozen", [
  ("Shelled edamame",2000,"g","\u00b7 four 500 g bags",24.00,"The whole savoury snack","shelled edamame"),
 ]),
 ("Pantry \u2014 one-off, lasts months", [
  ("Bread rolls",12,"ea","",6.00,"Two each, three lunches","bread rolls"),
  ("Cloudy apple juice",1000,"ml","",4.00,"<b>The braise.</b> Cloudy juice, <b>not</b> alcoholic cider","cloudy apple juice"),
  ("Apple cider vinegar",500,"ml","",4.00,"Two tablespoons into the braise",None),
  ("Smoked paprika",50,"g","",3.50,"The rub on the cheeks",None),
  ("Bay leaves",10,"g","",3.00,"Two into the braise",None),
  ("Brown sugar",500,"g","",2.50,"A tablespoon into the rub",None),
  ("Cajun seasoning",50,"g","",4.00,"The blackened salmon, three nights",None),
  ("Lemon pepper seasoning",50,"g","",3.50,"The wings, four nights",None),
  ("Rolled oats",500,"g","",2.50,"The parfait mix","rolled oats"),
  ("Pecans",150,"g","",6.00,"Toasted \u2014 bowls and parfaits","pecans"),
  ("Honey",500,"g","",6.00,"Parfaits and the bowl dressing","honey"),
  ("Dijon mustard",200,"g","",3.00,"The braise, the slaw and the dressing",None),
  ("Mayonnaise",250,"g","",4.00,"The slaw and the grinder salad",None),
  ("Chilli flakes",50,"g","",3.00,"The edamame",None),
 ]),
]

CUPBOARD = (u"Olive oil, salt and pepper, baking powder, cinnamon, dried oregano, caster sugar, "
            u"and <b>red wine vinegar</b> \u2014 three dishes use it this week, so check you have most "
            u"of a bottle. <b>No protein powder, no almond meal, no filo, no couscous.</b>")

DATES = u"15\u201321 November"

# =========================================================== read + swap
s = io.open(PAGE, encoding="utf-8").read()
orig = s

a = s.index("  var M = {")
b = s.index("\n  };", a)
meals = s[a:b]

if ('"%s":{' % SWAP_OUT) in meals:
    ms = meals.index('"%s":{' % SWAP_OUT)
    me = meals.index('\n\n    "', ms)
    meals = meals[:ms] + SWAP_IN + "," + meals[me:]
    print("swapped %s -> cheeks" % SWAP_OUT)
else:
    assert '"cheeks":{' in meals, "neither the old dish nor the new one is present"
    print("cheeks already in place")

for key in T:
    assert ('"%s":{' % key) in meals, "recipe missing from the page: %s" % key
assert ('"%s":{' % SWAP_OUT) not in meals, "the swapped-out dish is still there"

# =========================================================== audit
tally, perday, energy = {}, [], []
for day, mode, L, D in DAYS:
    tally[L] = tally.get(L, 0) + 1
    tally[D] = tally.get(D, 0) + 1
    perday.append(T[L][1] + T[D][1] + SNACK_P)
    energy.append(T[L][2] + T[D][2] + SNACK_K)

for k, (_, _, _, port) in T.items():
    if port is None:
        continue
    assert tally.get(k, 0) * 2 == port, "PORTIONS %s: %d meals x2 != %d" % (k, tally.get(k, 0), port)
assert sum(v[3] for v in T.values() if v[3]) == 28, "portions != 28"
assert sum(tally.values()) == 14, "meals != 14"
assert len(DAYS) == 7
print("portions 28 ok, meals 14 ok (7 lunch / 7 dinner)")
print("protein/day:", perday, "avg %.1f" % (sum(perday) / 7.0))
assert all(BAND[0] <= p <= BAND[1] for p in perday), "OUT OF BAND: %s" % perday
PRO = int(round(sum(perday) / 7.0))
KCAL = int(round(sum(energy) / 7.0 / 10.0) * 10)
print("energy/day:", energy, "avg -> %d" % KCAL)


def base(nm):
    """'cabbage, shredded' and 'beef - chuck or topside' both reduce to the
    thing you actually buy, so a prep word cannot break a shop match."""
    return nm.split(",")[0].split(" \u2014 ")[0].strip()


need = {}
for key, body in re.findall(r'"(\w+)":\{(.*?)\n      s:\[', meals, re.S):
    ings = body[body.index("i:["):]
    for q, u, nm in re.findall(r'\[([\d.]+),"(\w+)","([^"]+)"\]', ings):
        k = base(nm)
        need.setdefault(k, [0.0, u])
        need[k][0] += float(q)

problems = []
for cat, items in CATS:
    for nm, q, u, hint, price, why, rk in items:
        if rk is None:
            continue
        k = base(rk)
        if k not in need:
            problems.append("no recipe line %r (shop: %s)" % (k, nm)); continue
        want, wu = need[k]
        if wu != u:
            problems.append("unit %s: shop %s vs recipe %s" % (nm, u, wu))
        elif q < want:
            problems.append("SHORT %s: buying %g%s, need %g%s" % (nm, q, u, want, u))
for p in problems:
    print("  !!", p)
assert not problems, "cross-check failed"
print("quantity cross-check: clean")

# =========================================================== generate
def esc(x):
    return x.replace("&", "&amp;")


def row(role, key):
    t, p = T[key][0], T[key][1]
    return ('          <div class="row" data-pro="%d"><span class="role">%s</span>'
            '<button class="open" data-meal="%s"><span class="rname">%s</span>'
            '<span class="leader"></span></button><span class="rpro">%d g</span></div>'
            % (p, role, key, esc(t), p))


out = ['<div class="rail" id="rail">']
for day, mode, L, D in DAYS:
    out += ["",
      '      <article class="docket">',
      '        <div class="d-head"><h3 class="d-day">%s</h3><span class="d-date"></span><span class="d-mode">%s</span></div>' % (day, mode),
      '        <div class="rows">',
      row("Lunch", L), row("Dinner", D),
      row("Savoury", "edamame"), row("Sweet", "parfait"),
      '        </div>', '      </article>']
rail = "\n".join(out)

n, total, lines = 0, 0.0, []
for cat, items in CATS:
    lines += ['        <div class="r-cat">', '          <h4>%s</h4>' % cat]
    for nm, q, u, hint, price, why, rk in items:
        n += 1
        total += price
        h = ' data-s="%s"' % hint if hint else ''
        lines.append('          <label class="r-item"><input type="checkbox" id="n%d">'
          '<span class="r-name">%s<span class="r-qty" data-q="%g" data-u="%s"%s></span></span>'
          '<span class="r-price" data-p="%.2f">$%.2f</span>'
          '<span class="r-for">%s</span></label>' % (n, esc(nm), q, u, h, price, price, why))
    lines += ['          <div class="r-sub"><span>Subtotal</span><span data-sub="0">$0.00</span></div>',
              '        </div>', '']
shop = "\n".join(lines[:-1])
print("lines %d | total $%.2f  (a read-out, not a target)" % (n, total))

SHOP_INTRO = (u'    <p class="para"><b>Last week\u2019s velveted beef is gone</b> \u2014 you ate it, and nothing '
 u'in this plan repeats. In its place is <b>Tim Laielli\u2019s cider braise from 13 November, moved onto beef '
 u'cheeks</b>: his own version is pulled chicken, and four pulled chickens have already been through here. '
 u'Beef cheek never has. <b>Four proteins and no fresh pork</b> \u2014 chicken wings, chicken breast, salmon, '
 u'beef cheeks, and cured ham and salami. No lentils, as always. The shop comes to <b>$%.2f</b> across %d '
 u'lines. <b>Check the Dijon, mayonnaise, honey and the apple cider vinegar before you leave</b>: they are '
 u'on the list because I cannot see your cupboard. <b>Cloudy apple juice, not alcoholic cider</b> \u2014 that '
 u'one would change the dish.</p>') % (total, n)

RTOP = u'          <p>%s \u00b7 %d lines \u00b7 no fresh pork, no lentils</p>' % (DATES, n)

RSTOCK = (u'        <div class="r-stock">\n'
 u'          <h4>Assumed in the cupboard</h4>\n'
 u'          <p class="r-stock-n">%s</p>\n'
 u'        </div>') % CUPBOARD

RFOOT = (u'        <p class="r-foot">Protein averages <b>%d g each a day</b> \u2014 %d at the bottom, %d at '
 u'the top. <b>Every single day lands inside the %d\u2013%d target</b>, which is the third week running. '
 u'Energy about %d kcal a day.</p>') % (PRO, min(perday), max(perday), BAND[0], BAND[1], KCAL)

PREP = (u'''    <div class="sh"><h2>Sunday cook-up</h2><p class="sh-note">55 minutes \u00b7 the braise does the waiting, not you</p></div>
    <p class="para"><b>55 minutes hands-on</b>, and the shape of the day is set by one thing: <b>the cheeks go in early and then look after themselves for three and a half hours</b>. Everything else fits inside that window. The oven is only needed once, at 200 \u00b0C for the chicken tray \u2014 so if you braise in the slow cooker the two never collide. Braise from <b>@barefoodtim</b>, 13 November, moved onto beef cheeks.</p>
    <div class="prep">
      <ol class="prep-ol">
        <li><div><b>1:00 \u2014 rub the cheeks and get them in</b><p>Salt, smoked paprika, brown sugar and pepper rubbed all over. Fennel and apple down first, cheeks on top, then the juice, vinegar and Dijon <b>poured around rather than over</b>. Thyme and bay tucked in, lid on, low. <b>Walk away until 4:30.</b></p></div></li>
        <li><div><b>1:20 \u2014 the chicken tray</b><p>Breast butterflied flat, sweet potato cubed and oiled on the same tray, 200 \u00b0C. Out at 70 \u00b0C internal and rested.</p></div></li>
        <li><div><b>2:00 \u2014 the parfait jar</b><p>Pecans toasted dry and chopped, oats and cinnamon stirred through. One jar, lasts the fortnight.</p></div></li>
        <li><div><b>2:15 \u2014 the bagging</b><p>Wings rubbed and bagged raw. Grinder meat and cheese in one tub. Salmon split three ways and <b>Friday\u2019s portion into the freezer</b>.</p></div></li>
        <li><div><b>2:30 \u2014 done until dinner</b><p>Nothing else needs you for two hours.</p></div></li>
        <li><div><b>4:30 \u2014 potatoes on, cheeks out</b><p>Potatoes boiled and mashed. Cheeks lifted out, the liquid reduced hard by a third, then <b>a ladle of it through the mash instead of butter</b>.</p></div></li>
      </ol>
      <p class="aside"><b>The bare minimum, if Sunday gets away from you.</b> Get the cheeks in and put the chicken tray on. The wing rub, the grinder bags and the parfait jar are fifteen minutes of bagging that can happen any evening. <b>The braise is the only thing with a clock on it</b>, and it is the one that needs you least.</p>
    </div>''')

PAIR = (u'      <table class="pair"><tbody>'
 u'<tr><td>Beef cheek</td><td>almost all collagen \u2014 it goes <b>silky</b> rather than stringy, which is why a braise suits it and a pan does not</td></tr>'
 u'<tr><td>Cloudy apple juice</td><td>Tim\u2019s \u201cunfiltered apple cider\u201d is American for this. <b>Alcoholic cider is a different drink</b></td></tr>'
 u'<tr><td>Poured around, not over</td><td>the top of the meat stays above the liquid, so it roasts while the bottom braises</td></tr>'
 u'<tr><td>Reduce before serving</td><td>braising liquid is thin until you take a third out of it; that is the sauce</td></tr>'
 u'<tr><td>Mash, no butter</td><td>a ladle of the reduced juices beats butter here, and keeps 12 g of fat a serve off the plate</td></tr>'
 u'<tr><td>Chicken wings \u2014 baking powder</td><td>lifts the skin\u2019s pH so it blisters instead of tightening</td></tr>'
 u'<tr><td>Wings \u2014 frozen raw</td><td>never frozen cooked; four dinners of wings only works if they are fried fresh</td></tr>'
 u'<tr><td>Chicken breast \u2014 butterflied</td><td>even thickness beats any cooking time you could pick</td></tr>'
 u'<tr><td>Salmon \u2014 blackened</td><td>spice on the flesh side only, into a dry screaming pan, turned once</td></tr>'
 u'<tr><td>Corn \u2014 charred dry</td><td>no oil and no stirring; let it sit still and catch</td></tr>'
 u'<tr><td>The grinder salad</td><td>salted, rested ten minutes, <b>drained</b> \u2014 that liquid is what ruins the bread</td></tr>'
 u'<tr><td>Greek yoghurt \u2014 0%</td><td>same protein as the 10%, a third of the fat, and here it is most of the dish</td></tr>'
 u'<tr><td>Edamame</td><td>salted while still steaming, or the salt never sticks at all</td></tr>'
 u'</tbody></table>')

# =========================================================== splice
def cut(a_anchor, b_anchor, new, label):
    global s
    i = s.index(a_anchor)
    j = s.index(b_anchor, i)
    s = s[:i] + new + s[j:]
    print("  ok  %-14s %6d -> %6d" % (label, j - i, len(new)))


def sub1(old, new, label):
    global s
    assert s.count(old) == 1, "%s found %d times" % (label, s.count(old))
    s = s.replace(old, new)
    print("  ok  " + label)


s = s[:a] + meals + s[b:]
print("  ok  meals")
cut('<div class="rail" id="rail">', '\n    </div>\n  </section>', rail, "rail")
# the shop intro is whatever paragraph sits immediately above the shop tools;
# anchoring on its text would break the moment the text changes, and anchoring
# on <p class="para"> alone matches an earlier panel and eats the page
_j = s.index('\n    <div class="shoptools">')
_i = s.rindex('    <p class="para">', 0, _j)
assert _j - _i < 2000, 'shop intro span looks wrong: %d bytes' % (_j - _i)
s = s[:_i] + SHOP_INTRO + s[_j:]
print('  ok  %-14s %6d -> %6d' % ('shop intro', _j - _i, len(SHOP_INTRO)))
sub1(re.search(r'          <p>[^<]*November[^<]*</p>', s).group(0), RTOP, "receipt date")
cut('        <div class="r-cat">', '\n\n        <div class="r-tot">', shop, "shop rows")
cut('        <div class="r-stock">', '\n\n        <p class="r-foot">', RSTOCK, "cupboard")
cut('        <p class="r-foot">', '\n      </div>', RFOOT, "receipt foot")
cut('    <div class="sh"><h2>Sunday cook-up</h2>', '</section>', PREP, "cook-up")
cut('      <table class="pair">', '\n    </div>', PAIR, "pair table")
sub1(re.search(r'<textarea id="note-text" placeholder="[^"]*">', s).group(0),
     '<textarea id="note-text" placeholder="e.g. too much chicken, the snacks got boring, '
     'want something baked again, more fish, less bread, Sunday took too long...">',
     "notes placeholder")

assert s != orig

# 1. the page script must parse. A missing comma between two recipes kills
#    the whole IIFE: the shop never paints and no cook sheet opens, with
#    nothing on the page to say why.
import subprocess, tempfile
_js = re.search(r"<script>(.*)</script>", s, re.S).group(1)
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
    fh.write(_js); _tmp = fh.name
_r = subprocess.run(["node", "--check", _tmp], capture_output=True, text=True)
if _r.returncode:
    sys.stderr.write(_r.stderr)
    raise SystemExit("page script does not parse - nothing written")
os.unlink(_tmp)
print("page script parses")

io.open(PAGE, "w", encoding="utf-8").write(s)
print("\nwritten: %d -> %d bytes" % (len(orig), len(s)))

# check the page content only: the script block holds regex tables with words
# like "bicarb" in them, and they are code rather than a stale dish reference
content = s[:s.index("<script>")]
stale = ["mongolian", "Mongolian", "goosetheory", "Shaoxing", "Velveted",
         "velveting", "potroast", "8\u201314 November", "your 460 g"]
left = [(t, content.count(t)) for t in stale if content.count(t)]
print("stale references:", left or "none")
assert not left, left
