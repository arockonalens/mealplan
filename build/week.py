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
 "cider":   ("Cider-braised chicken thighs, fennel and apple", 54, 790, 2),
 "satay":   ("Satay chicken, rice and greens",              54, 670,  4),
 "steak":   ("Rump steak, chimichurri, crisp potatoes",     57, 600,  2),
 "chimchx": ("Chimichurri chicken thighs, green rice and beans", 45, 660, 2),
 "harvest": ("Harvest chicken bowl, apple and pecan",       55, 588,  6),
 "grinder": ("Italian grinder sliders",                     42, 562,  6),
 "salmon":  ("Paprika-crusted salmon, charred corn salsa",  43, 525,  4),
 "gnocchi": ("Sweet potato gnocchi, rump steak and sage",  64, 720,  2),
 "tofu":    ("Crispy sesame-soy tofu",                      14, 170, None),
 "parfait": ("Apple cinnamon yoghurt parfait",              17, 235, None),
}
DAYS = [
 ("Sun", "Satay night",         "grinder", "satay"),
 ("Mon", "Satay, then fish",    "satay",   "salmon"),
 ("Tue", "Braise night",        "harvest", "cider"),
 ("Wed", "Second salmon",       "harvest", "salmon"),
 ("Thu", "Gnocchi night",       "grinder", "gnocchi"),
 ("Fri", "Steak night",         "harvest", "steak"),
 ("Sat", "Chimichurri chicken", "grinder", "chimchx"),
]
SNACK_P = T["tofu"][1] + T["parfait"][1]
SNACK_K = T["tofu"][2] + T["parfait"][2]
BAND = (112, 154)

# ------------------------------------------------- recipes this file owns
# Every recipe here is written into the page, replacing the page's copy if it
# has one. Anything on the page whose key is not in T is dropped, and printed.
#  - cider:  Tim Laielli's 13 Nov cider braise, in place of last week's beef.
#    Briefly on beef cheeks; Greg asked for chicken (15 Nov), so thighs, whole
#  - chilli: Tim's October turkey chilli, in place of the wings (15 Nov: "chicken
#    wings is a no")
#  - tofu:   in place of the edamame (15 Nov: "get rid of edamame")
CIDER = u'''"cider":{r:"Dinner · 2 portions",t:"Cider-braised chicken thighs, fennel and apple",p:54,c:70,sv:"2 portions · Tuesday · thighs rubbed Sunday · 1¼ hours in the oven, 20 minutes of work",m:["Oven","1¼ hr","Flag · 790 kcal"],
      src:"Tim Laielli, the bare minimum, 13 Nov — his cider-braised chicken, with the thighs left whole",
      kp:"Rubbed thighs bagged in the fridge Sunday · cooked Tuesday",al:"mustard",
      i:[["The rub",[
            [500,"g","chicken thigh fillets, trimmed"],
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
      s:[["Rub","Sunday: salt, smoked paprika, brown sugar and pepper rubbed all over the thighs. Bagged, into the fridge.",0],
         ["Oven","Tuesday: oven to 165 °C.",0],
         ["Layer","Fennel and apple scattered over the base of an ovenproof pot with a lid. Thighs laid on top, <b>whole</b>.",0],
         ["Pour","Apple juice, vinegar and Dijon whisked, then poured <b>around</b> the thighs rather than over them. Thyme and bay tucked in.",0],
         ["Braise","Lid on, into the oven.",75],
         ["Mash","Potatoes boiled in well-salted water until tender.",18],
         ["Reduce","Thighs lifted out and kept warm. The liquid simmered hard on the stove until it reduces by about a third.",10],
         ["Finish","<b>A ladle of the reduced juices through the mash instead of butter.</b>",0],
         ["Serve","Thighs whole over the mash, the braised fennel and apple alongside, the rest of the juices spooned over.",0]],
      n:[["Whole thighs, not pulled","Tim shreds his. <b>Four pulled chickens have already been through here</b> — harissa pulled chicken, harissa pulled thigh, pulled chicken bowl, pulled chicken slaw bowl — so these stay whole. Thigh rather than breast because breast goes dry and stringy sitting in liquid for over an hour."],
         ["Cloudy apple juice, not cider","<b>Tim’s “unfiltered apple cider” is American for cloudy apple juice.</b> The alcoholic cider at Coles is a different drink and would leave this sharp and thin."],
         ["No sear","Tim’s own shortcut: the thighs go straight into the pot. In a braise this wet, nobody can tell."],
         ["Cooked is not the same as tender","Thigh is safe well before the hour is up, but it is the full 75 minutes that turns it soft."],
         ["Fat flag — 790 kcal, 21 g fat a serve","<b>The heaviest plate of the week.</b> Most of the fat is the thigh itself; trimming what you can see before the rub takes a few grams off. <b>No butter in the mash</b> — the reduced juices do the job and keep about 110 kcal and 12 g of fat a serve off the plate."]]}'''

SATAY = u'''"satay":{r:"Dinner and lunch · 8 portions",t:"Satay chicken, rice and greens",p:54,c:52,sv:"8 portions cooked · Sunday dinner and Monday lunch · the other four frozen for another week",m:["Pan","50 min","Flag · 670 kcal"],
      src:"RecipeTin Eats (Nagi Maehashi) — Thai chicken satay with peanut sauce. Her sauce as written; marinade scaled to 1.5 kg; breast, no skewers, no curry paste",
      kp:"Four portions left · into the freezer by Wednesday · 3 months frozen",al:"peanut, soy",
      i:[["Marinade",[
            [1500,"g","chicken breast, in 2 cm pieces"],
            [2.5,"ea","tbsp mild curry powder"],
            [2.5,"ea","tsp white sugar"],
            [2.5,"ea","tsp salt"],
            [150,"ml","light coconut milk — from the second tin"]]],
         ["Thai peanut sauce",[
            [340,"ml","light coconut milk — most of the first tin"],
            [0.75,"ea","cup natural peanut butter, smooth — about 190 g"],
            [0.25,"ea","cup white sugar — about 50 g"],
            [2,"ea","tsp dark soy sauce"],
            [1,"ea","tsp salt"],
            [2,"ea","tbsp apple cider vinegar"],
            [0.75,"ea","cup water"]]],
         ["Cooking",[
            [3,"ea","tbsp olive oil"]]],
         ["Veggies",[
            [2,"ea","heads broccoli, in small florets"],
            [2,"ea","red capsicums, sliced"],
            [2,"ea","carrots, sliced thin"]]],
         ["To serve",[
            [1.75,"ea","cups jasmine rice — about 320 g"],
            [2,"ea","tbsp roasted peanuts, chopped fine"],
            [2,"ea","limes, in wedges"]]]],
      s:[["Marinate","Chicken mixed with the curry powder, sugar, salt and 150 ml of coconut milk.",20],
         ["Sauce","The rest of the tin, peanut butter, sugar, dark soy, salt, vinegar and water into a saucepan over medium-low. Simmered, stirred now and then. Pourable but thick; water if it tightens. Lid on.",5],
         ["Fry","Big non-stick pan, medium-high, a tablespoon of oil. Chicken in <b>three batches</b>, about 3 minutes a side until golden. Out.",18],
         ["Veggies","Carrot in first, then broccoli and capsicum, with a splash of water. Still crunchy.",4],
         ["Toss","Chicken back in, sauce over, tossed.",1],
         ["Serve","Over rice, peanuts and a lime wedge on top.",0],
         ["Portion","Cooled. Monday’s two into the fridge, <b>the other four into the freezer</b>.",0],
         ["Reheat","Covered, until steaming right through, a splash of water if the sauce has set. Over rice cooked fresh.",4]],
      n:[["No curry paste","Nagi’s recipe has red curry paste in the marinade and the sauce. <b>Both left out</b> — it carries heat, and your partner does not want any. The mild curry powder keeps the curry note."],
         ["Breast, not thigh, and no skewers","She uses thigh on skewers. Breast keeps about 8 g of fat a serve off, and pieces in a pan suit eight portions."],
         ["Light coconut milk","She uses full-fat. Light keeps about 6 g of fat a serve off. Scaling her marinade to 1.5 kg takes a second tin; about 300 ml is left over, and it freezes."],
         ["Natural peanut butter","No added sugar or oil. A sweetened spread makes it thick and flat, and needs more water."],
         ["Fat flag — 670 kcal, 27 g fat a serve","With the rice. Peanut butter and the frying oil are most of it. About 6 g of sugar a serve from the sauce."],
         ["Not a repeat of the peanut bowls","The crunchy peanut chicken bowls ran earlier. This is her satay, hot, with greens and rice."]]}'''

STEAK = u'''"steak":{r:"Dinner · 2 portions",t:"Rump steak, chimichurri, crisp potatoes",p:57,c:34,sv:"2 portions · Friday · cooked fresh",m:["Pan + air fryer","30 min","Lean beef"],
      kp:"Chimichurri made Friday, half kept for Saturday · steak cooked fresh",al:"none of the big ones",
      i:[["Chimichurri — Friday, for two nights",[
            [1,"ea","bunch flat-leaf parsley, chopped fine"],
            [2,"ea","cloves garlic, crushed"],
            [2,"ea","tsp dried oregano"],
            [3,"ea","tbsp red wine vinegar"],
            [60,"ml","olive oil"],
            [0.5,"ea","tsp salt"]]],
         ["Steak night",[
            [500,"g","rump steak — the second pack"],
            [400,"g","baby potatoes, halved"],
            [200,"g","green beans, trimmed"],
            [1,"ea","tsp olive oil"]]]],
      s:[["Chimichurri","Parsley, garlic, oregano, vinegar, oil and salt stirred in a jar. <b>Half kept for Saturday.</b>",0],
         ["Potatoes","Tossed in the teaspoon of oil and salt. Air fryer 200 °C, shaken halfway.",20],
         ["Steak out","Steak out of the fridge, patted dry, salted both sides.",15],
         ["Sear","Heavy pan smoking hot, no oil. Steak in, 3 minutes a side for medium-rare.",6],
         ["Rest","Onto a board.",5],
         ["Beans","Into the same pan with a splash of water, lid on.",3],
         ["Serve","Steak sliced across the grain, chimichurri over, potatoes and beans alongside.",0]],
      n:[["Nothing hot in it","Just herbs, garlic and vinegar."],
         ["Rump, trimmed","Lean, and the only steak this plan has run is pork. Slice across the grain or it chews."],
         ["57 g protein, 600 kcal, 20 g fat a serve","The chimichurri oil is about a third of the fat."],
         ["The other pack","Thursday’s pack went under the gnocchi."]]}'''

CHIMCHX = u'''"chimchx":{r:"Dinner · 2 portions",t:"Chimichurri chicken thighs, green rice and beans",p:45,c:50,sv:"2 portions · Saturday · thighs frozen Sunday, out Friday night",m:["Pan","25 min","Flag · 660 kcal"],
      kp:"Thighs to the fridge Friday night · Friday’s leftover chimichurri",al:"none of the big ones",
      i:[["Saturday",[
            [400,"g","chicken thigh fillets — Sunday’s bag, with the sage"],
            [0.75,"ea","cup jasmine rice — about 140 g"],
            [200,"g","green beans, trimmed"],
            [2,"ea","tsp olive oil"]]]],
      s:[["Rice","Rice on.",15],
         ["Sear","Oil into a pan over medium-high. Thighs in flat, five minutes a side.",10],
         ["Rest","Out onto a board.",3],
         ["Beans","Into the same pan with a splash of water, lid on.",3],
         ["Green rice","Two spoons of the chimichurri stirred through the hot rice.",0],
         ["Serve","Thighs sliced over the rice, beans alongside, the rest of the chimichurri over the chicken.",0]],
      n:[["Uses what is already here","The thighs bagged with sage on Sunday, and Friday’s second half of chimichurri. Nothing new to buy."],
         ["Fat flag — 660 kcal, 26 g fat a serve","The thigh and the chimichurri oil, about half each."]]}'''

SALMON = u'''"salmon":{r:"Dinner · 4 portions",t:"Paprika-crusted salmon, charred corn salsa",p:43,c:23,sv:"4 portions · two dinners for two · cooked fresh",m:["Pan","20 min","Lowest carb"],
      kp:"Monday and Wednesday · cooked fresh",al:"fish",
      i:[["Salmon",[
            [800,"g","salmon fillets"],
            [2,"ea","tbsp smoked paprika"],
            [1,"ea","tsp garlic powder"],
            [1,"ea","tsp dried oregano"]]],
         ["Charred corn salsa",[
            [4,"ea","corn cobs"],
            [200,"g","tomatoes, chopped"],
            [1,"ea","red onion, diced"],
            [2,"ea","lemons"],
            [1,"ea","bunch chives"]]]],
      s:[["Press","Salmon dried, then pressed hard into the paprika, garlic powder and oregano <b>on the flesh side only</b>.",0],
         ["Sear","Screaming hot dry pan, spice side down first.",4],
         ["Turn","Turned once, three minutes on the skin. Out while the centre is still coral.",3],
         ["Char the corn","Corn cut off the cob and charred in the same pan — <b>no oil, no stirring</b>.",5],
         ["Salsa","Charred corn, tomato, red onion, lemon, salt and chives. Made fresh each night.",0]],
      n:[["Smoky, not hot","Smoked paprika in place of the cajun mix, which carries cayenne."],
         ["The crust goes dark, not the fish","If the pan sweats instead of catching, it is not hot enough."],
         ["Lowest carb plate here","23 g a serve, 525 kcal."]]}'''

GNOCCHI = u'''"gnocchi":{r:"Dinner · 2 portions",t:"Sweet potato gnocchi, rump steak and sage",p:64,c:82,sv:"2 portions · Thursday · gnocchi made tonight",m:["Pan","50 min","Lean beef"],
      kp:"Cooked and eaten tonight",al:"wheat",
      i:[["The gnocchi",[
            [400,"g","sweet potatoes, whole"],
            [0.75,"ea","cup plain flour — about 115 g, plus some for the bench"],
            [1,"ea","tsp salt"]]],
         ["The plate",[
            [500,"g","rump steak — one pack"],
            [2,"ea","tsp olive oil"],
            [1,"ea","bunch sage"],
            [120,"g","baby spinach"],
            [1,"ea","lemon"]]]],
      s:[["Cook","Sweet potatoes pricked all over and microwaved on high, turned halfway, until soft right through.",10],
         ["Dry","Halved, flesh scooped onto a tray and spread thin to steam off.",10],
         ["Dough","Flesh mashed smooth with the salt. Flour worked in with a fork <b>only until it holds</b>; more only if it sticks to your hands.",0],
         ["Roll","Dough split in four, each rolled on a floured bench into a rope as thick as a thumb, cut into 2 cm pieces. Onto a floured tray.",0],
         ["Steak out","Steak patted dry, salted both sides. Big pot of salted water on.",0],
         ["Sear","Big pan smoking hot, no oil. Steak in, 3 minutes a side for medium-rare. Out to rest.",6],
         ["Boil","Gnocchi into the boiling water. Out a minute after they float.",3],
         ["Colour","Oil into the steak pan, medium-high. Gnocchi and sage in, left still until golden underneath, then turned.",5],
         ["Wilt","Spinach in, tossed until it collapses. Lemon squeezed over.",1],
         ["Serve","Steak sliced across the grain over the gnocchi.",0]],
      n:[["Just sweet potato and flour","No egg and no parmesan, the way you make it. About 40% of the carbs are the flour."],
         ["Drying the flesh keeps the flour down","Wet flesh drinks flour and goes dense. Spread it thin and let it steam."],
         ["Boiled, then fried","It is raw dough. Straight into the pan it stays gluey in the middle."],
         ["Steak with it, not the thighs","The thighs are still frozen, and seared beef suits sage and sweet potato. They go to Saturday."],
         ["64 g protein, 720 kcal, 17 g fat a serve","Lean rump, and no butter anywhere."]]}'''

TOFU = u'''"tofu":{r:"Savoury snack · 4 minutes a day",t:"Crispy sesame-soy tofu",p:14,c:4,sv:"14 servings · about 105 g each · one a day",m:["Air fryer","35 min Sunday","First time here"],
      kp:"Half chilled, 4 days · half frozen for Thursday on · dressing kept apart",al:"soy, sesame",
      i:[["Tofu",[
            [1500,"g","firm tofu"],
            [3,"ea","tbsp cornflour"],
            [1,"ea","tbsp olive oil"]]],
         ["Sesame-soy dressing",[
            [3,"ea","tbsp soy sauce"],
            [2,"ea","tsp sesame oil"],
            [2,"ea","tbsp sesame seeds, toasted"]]]],
      s:[["Press","Tofu pressed between paper towel under a heavy board.",20],
         ["Cube","Cut into 2 cm cubes.",0],
         ["Coat","Cubes tossed with the cornflour and the oil until every face is dusted.",0],
         ["Air fry","Air fryer 200 °C, <b>single layer</b>, shaken halfway. In batches.",15],
         ["Split","Cooled on a rack. Half into the fridge, <b>half into the freezer for Thursday on</b>.",0],
         ["Dressing","Soy, sesame oil and sesame seeds shaken in a jar.",0],
         ["Each day","A serve back in the air fryer at 200 °C, then tossed in a spoon of the dressing.",4]],
      n:[["Why tofu","It takes the edamame’s slot because it carries nearly the same protein, and <b>tofu has never been in this plan</b>."],
         ["Pressing is the whole trick","Wet tofu steams in the basket instead of crisping, whatever the temperature."],
         ["Dressed at the last second","Dressed and left in the tub, the crust goes soft within minutes."],
         ["From the freezer","Straight in, no thawing, about 8 minutes instead of 4. Freezing makes tofu chewier and meatier, which suits this."],
         ["Fat flag — 14 g protein, 11 g fat, 170 kcal a serve","<b>Fattier than the edamame was</b> (7 g), and it is the tofu itself rather than the oil: soy is about half fat by energy. A snack-sized amount, but it is not the leanest thing here any more."]]}'''

OWN = {"cider": CIDER, "satay": SATAY, "steak": STEAK, "chimchx": CHIMCHX, "salmon": SALMON, "gnocchi": GNOCCHI, "tofu": TOFU}
# dishes Greg has said no to; the build fails if one comes back
BANNED = ["wings", "edamame", "mongolian", "chilli"]


# ------------------------------------------------------------- the shopping
# (name, qty, unit, hint, price, what it is for, recipe-ingredient key or None)
# Price is a read-out, never a constraint — see CLAUDE.md.
CATS = [
 ("Protein", [
  ("Chicken breast",3000,"g","\u00b7 1.5 kg for the satay, 1.5 kg for the bowls",38.00,"<b>Tonight\u2019s</b> satay, and the harvest bowls","chicken breast"),
  ("Chicken thigh fillets",1000,"g","\u00b7 two 500 g trays",16.00,"Tuesday\u2019s braise, and Saturday\u2019s chimichurri chicken \u2014 that tray frozen Sunday","chicken thigh fillets"),
  ("Rump steak",1000,"g","\u00b7 two 500 g packs",28.00,"<b>Top-up for Thursday</b> \u2014 tonight\u2019s gnocchi and Friday\u2019s steak","rump steak"),
  ("Salmon fillets",800,"g","",28.00,"Monday and Wednesday, cooked fresh","salmon fillets"),
  ("Firm tofu",1500,"g","\u00b7 in whatever blocks they have",15.00,"The savoury snack, all fortnight\u2019s worth pressed on Sunday","firm tofu"),
  ("Shaved ham",600,"g","",12.00,"The grinders \u2014 cured, so it is fine","shaved ham"),
  ("Salami",200,"g","",6.00,"The grinders \u2014 200 g, not 300; it is the fattiest thing in them","salami"),
 ]),
 ("Dairy", [
  ("Provolone",200,"g","",7.00,"The grinders \u2014 Swiss if there is no provolone","provolone"),
  ("Greek yoghurt, 0% fat",2000,"g","",12.00,"The parfaits \u2014 0%, not the 10% stuff","Greek yoghurt"),
 ]),
 ("Produce", [
  ("Potatoes",600,"g","\u00b7 loose, about four",2.50,"Tuesday\u2019s mash","potatoes"),
  ("Sweet potatoes",1300,"g","\u00b7 you have some \u2014 buy the difference",5.00,"900 g roasted for the bowls, 400 g for the gnocchi","sweet potatoes"),
  ("Fennel",1,"ea","",4.00,"Tuesday \u2014 it goes under the thighs","fennel bulb"),
  ("Apples",10,"ea","",8.00,"Three to the bowls, six to the parfaits, one to the braise","apples"),
  ("Cos lettuce",4,"ea","",8.00,"Two for the grinder salad, two for the bowls","cos lettuce"),
  ("Corn cobs",4,"ea","",5.00,"Two a night, charred for the salsa","corn cobs"),
  ("Lemons",3,"ea","",2.25,"The salsa two nights, one over the gnocchi","lemons"),
  ("Tomatoes",500,"g","",3.50,"Grinder salad and the corn salsa","tomatoes"),
  ("Red onions",3,"ea","",2.00,"Two for the grinders, one for the salsa","red onions"),
  ("Broccoli",2,"ea","",5.00,"<b>Tonight</b> \u2014 the satay","heads broccoli"),
  ("Red capsicums",2,"ea","",4.00,"<b>Tonight</b> \u2014 the satay","red capsicums"),
  ("Carrots",2,"ea","",1.00,"<b>Tonight</b> \u2014 the satay","carrots"),
  ("Limes",2,"ea","",2.00,"Wedges over the satay","limes"),
  ("Baby potatoes",800,"g","\u00b7 one bag",4.00,"<b>Top-up for Thursday</b> \u2014 Friday\u2019s steak","baby potatoes"),
  ("Green beans",400,"g","",4.00,"<b>Top-up for Thursday</b> \u2014 Friday and Saturday","green beans"),
  ("Flat-leaf parsley",1,"ea","",3.00,"<b>Top-up for Thursday</b> \u2014 Friday\u2019s chimichurri","bunch flat-leaf parsley"),
  ("Garlic",1,"ea","\u00b7 one bulb",1.50,"<b>Top-up for Thursday</b> \u2014 two cloves into the chimichurri",None),
  ("Chives",2,"ea","",6.00,"The bowls and the salsa","bunch chives"),
  ("Sage",1,"ea","",3.00,"The gnocchi",None),
  ("Baby spinach",120,"g","\u00b7 one bag",3.00,"Wilted into the gnocchi","baby spinach"),
  ("Thyme",1,"ea","",3.50,"Tuesday \u2014 four sprigs into the braise",None),
 ]),
 ("Pantry \u2014 one-off, lasts months", [
  ("Plain flour",1000,"g","",2.00,"The gnocchi",None),
  ("Bread rolls",12,"ea","",6.00,"Two each, three lunches","bread rolls"),
  ("Jasmine rice",1000,"g","",3.50,"Under the satay, and Saturday\u2019s green rice",None),
  ("Natural peanut butter",375,"g","\u00b7 one jar",5.00,"\u00be cup into the satay sauce \u2014 natural, no added sugar or oil",None),
  ("Light coconut milk",800,"ml","\u00b7 two 400 ml tins",5.00,"The satay marinade and sauce \u2014 light, not full-fat","light coconut milk"),
  ("Mild curry powder",50,"g","",3.00,"The satay marinade \u2014 <b>mild</b>",None),
  ("Dark soy sauce",150,"ml","",3.50,"Two teaspoons into the satay sauce \u2014 regular soy works, paler",None),
  ("Roasted peanuts",100,"g","\u00b7 smallest bag",3.00,"Chopped over the satay",None),
  ("Cloudy apple juice",1000,"ml","",4.00,"<b>The braise.</b> Cloudy juice, <b>not</b> alcoholic cider","cloudy apple juice"),
  ("Apple cider vinegar",500,"ml","",4.00,"Two tablespoons each into the braise and the satay sauce",None),
  ("Smoked paprika",50,"g","",3.50,"The rub on the thighs, and the salmon crust",None),
  ("Bay leaves",10,"g","",3.00,"Two into the braise",None),
  ("Brown sugar",500,"g","",2.50,"A tablespoon into the rub",None),
  ("Cornflour",300,"g","",2.50,"The tofu coating",None),
  ("Soy sauce",250,"ml","",3.50,"The tofu dressing",None),
  ("Sesame oil",150,"ml","",4.00,"The tofu dressing",None),
  ("Sesame seeds",100,"g","",3.00,"The tofu dressing, toasted",None),
  ("Garlic powder",50,"g","",3.00,"The salmon crust",None),
  ("Rolled oats",500,"g","",2.50,"The parfait mix","rolled oats"),
  ("Pecans",150,"g","",6.00,"Toasted \u2014 bowls and parfaits","pecans"),
  ("Honey",500,"g","",6.00,"Parfaits and the bowl dressing","honey"),
  ("Dijon mustard",200,"g","",3.00,"The braise and the bowl dressing",None),
  ("Mayonnaise",250,"g","",4.00,"The grinder salad",None),
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

starts = [(m.group(1), m.start()) for m in re.finditer(r'\n    "(\w+)":\{', meals)]
entries = {}
for n_, (key, st) in enumerate(starts):
    en = starts[n_ + 1][1] if n_ + 1 < len(starts) else len(meals)
    entries[key] = meals[st + 5:en].rstrip().rstrip(",")
head = meals[:starts[0][1]]
dropped = [k for k in entries if k not in T]
entries.update(OWN)
missing = [k for k in T if k not in entries]
assert not missing, "recipe missing from the page and from OWN: %s" % missing
meals = head + "\n    " + ",\n\n    ".join(entries[k] for k in T)
print("recipes:", ", ".join(T), "| dropped:", ", ".join(dropped) or "none")
for k in BANNED:
    assert ('"%s":{' % k) not in meals, "a banned dish is back: %s" % k
for k in OWN:
    assert meals.count('"%s":{' % k) == 1, "%s appears more than once" % k

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
# 18 Nov: satay was Sunday dinner and came back Thursday and Friday. Greg:
# "Why am I doing satay chicken again Thursday we had it Sunday."
for k in T:
    nd = sum(1 for _, _, _, D in DAYS if D == k)
    assert nd <= 2, "%s fills %d dinners; two at most" % (k, nd)
print("no dish fills more than two dinners")

# The recipe index files each dish by the FIRST word of its r: label, so a dish
# served at dinner must start "Dinner" or it vanishes from the Dinners list.
# 15 Nov: the chilli read "Lunch and dinner" and Greg saw "only two dinners".
roles = dict(re.findall(r'"(\w+)":\{r:"([^"]*)"', meals))
for k, v in T.items():
    if v[3] is None:
        continue
    want = "Dinner" if any(D == k for _, _, _, D in DAYS) else "Lunch"
    assert roles[k].startswith(want), "%s is labelled %r but is served as a %s" % (k, roles[k], want.lower())
print("recipe-index labels match the days")
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
      row("Savoury", "tofu"), row("Sweet", "parfait"),
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

SHOP_INTRO = (u'    <p class="para"><b>Nothing hot this week.</b> <b>Satay chicken Sunday</b>, which covers Monday lunch, in place of the turkey stew; the other four portions go in the freezer. <b>Thursday is sweet potato gnocchi with rump steak, Friday steak with chimichurri, Saturday the frozen thighs with the rest of the chimichurri</b>: the lines marked top-up are what to buy. '
 u'The salmon is crusted in smoked paprika instead of cajun, and the tofu dressing is just soy and sesame. '
 u'Tim\u2019s cider '
 u'braise on whole chicken thighs moves to Tuesday. No beef and no fresh pork \u2014 chicken, salmon and tofu, '
 u'plus cured ham and salami. No lentils, as always. The shop comes to <b>$%.2f</b> across %d lines. '
 u'<b>You have sweet potato</b>: 1.3 kg covers the bowls and the gnocchi, so only buy the difference. '
 u'<b>Check the peanut butter, Dijon, mayonnaise, honey, soy and the apple cider vinegar before you leave.</b> '
 u'<b>Cloudy apple juice, not alcoholic cider.</b></p>') % (total, n)

RTOP = u'          <p>%s \u00b7 %d lines \u00b7 no fresh pork, no lentils</p>' % (DATES, n)

RSTOCK = (u'        <div class="r-stock">\n'
 u'          <h4>Assumed in the cupboard</h4>\n'
 u'          <p class="r-stock-n">%s</p>\n'
 u'        </div>') % CUPBOARD

RFOOT = (u'        <p class="r-foot">Protein averages <b>%d g each a day</b> \u2014 %d at the bottom, %d at '
 u'the top. <b>Every single day lands inside the %d\u2013%d target</b>, which is the third week running. '
 u'Energy about %d kcal a day.</p>') % (PRO, min(perday), max(perday), BAND[0], BAND[1], KCAL)

PREP = (u'''    <div class="sh"><h2>Sunday cook-up</h2><p class="sh-note">about 100 minutes hands-on · the satay is dinner</p></div>
    <p class="para"><b>About 100 minutes hands-on.</b> The satay is tonight’s dinner and four more meals, so it is cooked last and eaten hot. The braise moves to Tuesday: the thighs only get their rub today. Thursday is gnocchi and steak, Friday steak, Saturday the thighs. Lunch today is the grinder, which needs no cooking at all.</p>
    <div class="prep">
      <ol class="prep-ol">
        <li><div><b>1:00 — tofu under a board, chicken tray in, sweet potatoes in the microwave</b><p>Tofu pressed under something heavy. Bowl breast butterflied flat, sweet potato cubed and oiled on the same tray, 200 °C, out at 70 °C internal. The gnocchi’s 400 g of sweet potato microwaved whole, then scooped out and spread on a tray to dry.</p></div></li>
        <li><div><b>1:15 — the gnocchi</b><p>Flesh mashed with the yolk, parmesan and salt, flour worked in only until it holds. Rolled into ropes, cut into 2 cm pieces, onto a floured tray and into the freezer.</p></div></li>
        <li><div><b>1:40 — the tofu</b><p>Cubed, tossed in cornflour and oil, air-fried in batches at 200 °C. Dressing shaken in a jar.</p></div></li>
        <li><div><b>2:20 — the parfait jar and the thighs</b><p>Pecans toasted and chopped into the oats and cinnamon. Grinder meat and cheese in one tub. <b>Tuesday’s thighs rubbed</b> with salt, smoked paprika, brown sugar and pepper, bagged, into the fridge. Saturday’s thighs into a flat bag with salt, pepper and sage, into the freezer. Gnocchi bagged once hard.</p></div></li>
        <li><div><b>4:40 — the satay</b><p>Breast in 2 cm pieces into the curry powder, sugar, salt and coconut milk for 20 minutes. Peanut sauce simmered and kept warm. Chicken fried in three batches, veg in, everything tossed in the sauce.</p></div></li>
        <li><div><b>5:45 — eat, then bag</b><p>Tonight’s two over fresh rice. <b>Into the freezer: four portions of satay and half the tofu.</b> Monday’s satay into the fridge.</p></div></li>
      </ol>
      <p class="aside"><b>The bare minimum, if Sunday gets away from you.</b> The satay and the chicken tray. The gnocchi can be made any evening before Saturday, the tofu any evening, the thighs rubbed Monday night, and the parfait jar is five minutes.</p>
    </div>''')

PAIR = (u'      <table class="pair"><tbody>'
 u'<tr><td>Chicken thigh, not breast</td><td>thigh has the fat and connective tissue to sit in liquid for over an hour; <b>breast goes dry and stringy</b></td></tr>'
 u'<tr><td>Cloudy apple juice</td><td>Tim\u2019s \u201cunfiltered apple cider\u201d is American for this. <b>Alcoholic cider is a different drink</b></td></tr>'
 u'<tr><td>Poured around, not over</td><td>the top of the meat stays above the liquid, so it roasts while the bottom braises</td></tr>'
 u'<tr><td>Reduce before serving</td><td>braising liquid is thin until you take a third out of it; that is the sauce</td></tr>'
 u'<tr><td>Mash, no butter</td><td>a ladle of the reduced juices beats butter here, and keeps 12 g of fat a serve off the plate</td></tr>'
 u'<tr><td>Satay chicken \u2014 batch-seared</td><td>three batches in a smoking wok; crowded, it stews grey in its own water</td></tr>'
 u'<tr><td>Steak \u2014 dry, salted, smoking pan</td><td>a wet steak steams grey; pat it dry and let the pan smoke first</td></tr>'
 u'<tr><td>Steak \u2014 sliced across the grain</td><td>rump has long fibres; cut across them or it chews</td></tr>'
 u'<tr><td>Sweet potato \u2014 microwaved and dried</td><td>boiled flesh drinks water and needs far more flour to hold</td></tr>'
 u'<tr><td>Gnocchi \u2014 frozen raw</td><td>cooked ahead it goes dense; raw from frozen it cooks like fresh</td></tr>'
 u'<tr><td>Chicken breast \u2014 butterflied</td><td>even thickness beats any cooking time you could pick</td></tr>'
 u'<tr><td>Salmon \u2014 paprika crust</td><td>spice on the flesh side only, into a dry screaming pan, turned once</td></tr>'
 u'<tr><td>Corn \u2014 charred dry</td><td>no oil and no stirring; let it sit still and catch</td></tr>'
 u'<tr><td>The grinder salad</td><td>salted, rested ten minutes, <b>drained</b> \u2014 that liquid is what ruins the bread</td></tr>'
 u'<tr><td>Greek yoghurt \u2014 0%</td><td>same protein as the 10%, a third of the fat, and here it is most of the dish</td></tr>'
 u'<tr><td>Tofu \u2014 pressed</td><td>wet tofu steams in the basket instead of crisping; twenty minutes under a board</td></tr>'
 u'<tr><td>Tofu \u2014 dressed last</td><td>dressed and left, the crust goes soft in minutes</td></tr>'
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

UNCHANGED = (s == orig)   # a rerun on a built page is a no-op, not an error

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

# 2. nothing from a dropped dish is left behind. Whole words only: "wing"
#    as a substring matches "swinging" in the gym panels and "thawing" in a
#    method. ALLOWED is the prose that names a dropped dish on purpose, to say
#    it has gone; it is cut out before counting.
content = s[:s.index("<script>")]
STALE = [r"[Mm]ongolian", r"goosetheory", r"Shaoxing", r"[Vv]elvet",
         r"potroast", r"8\u201314 November", r"your 460 g",
         r"\b[Ww]ings?\b", r"\b[Cc]hilli\b", r"[Cc]ajun", r"[Bb]lack bean", r"[Cc]heeks?\b", r"\b[Ee]damame\b", r"\b[Ss]tew\b", r"[Tt]urkey", r"[Cc]annellini", r"[Ll]emon pepper", r"\bslaw\b"]
ALLOWED = [u"in smoked paprika instead of cajun", u"No chilli, no cumin, no paprika", u"in place of the cajun mix", u"No wings and no edamame this week", u"The wings\u2019 four slots",
           u"the wings were rubbed on Sunday", u"the edamame\u2019s slot",
           u"Fattier than the edamame was", u"pulled chicken slaw bowl",
           u"Last week\u2019s velveted beef is gone", u"in place of the turkey stew", u"crowded, it stews grey"]
def _strip(x):
    for a in ALLOWED:
        x = x.replace(a, "")
    return x
_c, _m = _strip(content), _strip(meals)
left = [("page " + t, len(re.findall(t, _c))) for t in STALE if re.search(t, _c)]
left += [("recipes " + t, len(re.findall(t, _m))) for t in STALE if re.search(t, _m)]
if left:
    raise SystemExit("stale references, nothing written: %s" % left)
print("stale references: none")

if UNCHANGED:
    print("\npage already up to date - nothing written")
else:
    io.open(PAGE, "w", encoding="utf-8").write(s)
    print("\nwritten: %d -> %d bytes" % (len(orig), len(s)))
