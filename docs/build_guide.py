import markdown, re, pathlib
src = pathlib.Path("docs/EDUCATOR_GUIDE.md").read_text(encoding="utf-8")
GH = "https://github.com/Educatian/cipherfell/blob/master/"
# rewrite repo-relative links to GitHub so they resolve on the live site
src = src.replace("](../research/", f"]({GH}research/").replace("](../README.md", f"]({GH}README.md")
src = src.replace("](../README.md#", f"]({GH}README.md#")
html_body = markdown.markdown(src, extensions=["tables","fenced_code","toc","sane_lists"])
tpl = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cipherfell — Educator Guide</title>
<style>
:root{--ink:#2c2114;--rust:#b5663b;--green:#6b7f4e;--gold:#d8a43e}
body{font-family:Georgia,'Times New Roman',serif;color:var(--ink);
 background:#f4ead0;margin:0;line-height:1.6}
.wrap{max-width:860px;margin:0 auto;padding:38px 22px 80px}
.bar{position:sticky;top:0;background:#2c2114;color:#f7eed5;padding:10px 22px;
 font-size:15px;display:flex;gap:18px;align-items:center;z-index:10;flex-wrap:wrap}
.bar a{color:#f0d79a;text-decoration:none;font-family:system-ui,sans-serif}
.bar a:hover{text-decoration:underline}
.bar b{font-family:Georgia,serif}
h1{font-size:38px;line-height:1.15;margin:.4em 0 .3em}
h2{font-size:28px;color:var(--rust);margin-top:1.4em;border-bottom:2px solid #e0cda0;padding-bottom:4px}
h3{font-size:22px;color:#5a4a2c;margin-top:1.3em}
img{max-width:100%;height:auto;border-radius:10px;border:2px solid var(--ink);display:block;margin:14px auto;box-shadow:0 6px 18px rgba(0,0,0,.15)}
table{border-collapse:collapse;width:100%;margin:14px 0;background:#fbf5e3}
th,td{border:1px solid #d8c69a;padding:8px 10px;text-align:left;vertical-align:top;font-size:16px}
th{background:#ece0bf}
code{background:#ece0bf;padding:1px 5px;border-radius:4px;font-size:.92em}
blockquote{border-left:4px solid var(--gold);margin:12px 0;padding:6px 16px;background:#fbf5e3;color:#5a4a2c}
a{color:#9a5a2b}
hr{border:none;border-top:2px solid #e0cda0;margin:28px 0}
.tag,.k,.h{font-family:system-ui,sans-serif}
@media(max-width:600px){h1{font-size:30px}th,td{font-size:14px}}
</style></head><body>
<div class="bar"><b>Cipherfell — The Warden's Eye</b>
 <a href="https://cipherfell.pages.dev/">▶ Play the game</a>
 <a href="facilitator_deck.html">▣ Facilitator deck</a>
 <a href="https://github.com/Educatian/cipherfell">GitHub</a></div>
<div class="wrap">__BODY__</div></body></html>"""
out = tpl.replace("__BODY__", html_body)
pathlib.Path("dist/docs").mkdir(parents=True, exist_ok=True)
pathlib.Path("dist/docs/guide.html").write_text(out, encoding="utf-8")
print("wrote dist/docs/guide.html", len(out), "bytes; images:", out.count("<img"))
