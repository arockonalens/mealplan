# -*- coding: utf-8 -*-
"""Cut the Claude-artifact copy out of index.html.

    python3 -I build/artifact.py <out.html>

The artifact is a <body> fragment: the title, the Google Fonts links, the
style block and the inner body. No doctype, no head, no favicon or manifest,
and no plain "github.io" anywhere. The service-worker registration stays in,
because it only runs when the host matches /github\\.io$/ - which is why the
backslash form must be present and the plain form must not.

Lives in the repo for the same reason week.py does: the session scratchpad it
used to live in gets wiped.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "index.html")
if len(sys.argv) != 2:
    raise SystemExit(__doc__)
OUT = sys.argv[1]

s = io.open(SRC, encoding="utf-8").read()
head = s[s.index("<title>"):s.index("</head>")]
body = s[s.index("<body>") + 6:s.rindex("</body>")]
keep = [re.search(r"<title>.*?</title>", head, re.S).group(0)]
keep += [l for l in re.findall(r'<link rel="(?:preconnect|stylesheet)"[^>]*>', head) if "fonts." in l]
keep.append(re.search(r"<style>.*?</style>", head, re.S).group(0))
out = "\n".join(keep) + "\n" + body

bad = {t: out.lower().count(t.lower()) for t in
       ["favicon", "manifest", "<!doctype", "<html", "</html>", "<head>", "<body", "github.io"]
       if out.lower().count(t.lower())}
print("stray document/asset refs:", bad or "none")
assert not bad, bad
assert r"github\.io" in out, "service-worker host guard missing"
assert "navigator.serviceWorker.register" in out
for must in ["tabbar", "cu-scroll-v1", "s-notes", 'class="rail"', 'id="r-total"']:
    assert must in out, "missing: %r" % must
for never in ["Per meal, each", "t-permeal", "splurge", "recurring basket"]:
    assert never not in out, "price argument still present: %r" % never

io.open(OUT, "w", encoding="utf-8").write(out)
print("fragment: %d bytes (page %d) -> %s" % (len(out), len(s), OUT))
