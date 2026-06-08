TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Cursor Watch — daily investment & adoption tracker</title>
<style>
  :root{
    --bg:#0b0d12; --panel:#13161d; --panel2:#181c25; --line:#262b36;
    --ink:#e8ebf2; --muted:#9aa3b2; --accent:#6ea8fe; --accent2:#7ee0c0;
    --warn:#ffcf72; --pill:#1f2530;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  a{color:var(--accent);text-decoration:none}
  a:hover{text-decoration:underline}
  .wrap{max-width:1100px;margin:0 auto;padding:0 20px 80px}
  header{position:sticky;top:0;z-index:20;background:rgba(11,13,18,.86);
    backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
  .head-in{max-width:1100px;margin:0 auto;padding:14px 20px;display:flex;
    align-items:center;gap:14px;flex-wrap:wrap}
  .logo{font-weight:700;font-size:18px;letter-spacing:.2px}
  .logo span{color:var(--accent)}
  .asof{color:var(--muted);font-size:13px}
  .spacer{flex:1}
  .btn{background:var(--accent);color:#06223f;border:0;border-radius:8px;
    padding:9px 14px;font-weight:650;font-size:13px;cursor:pointer}
  .btn:hover{filter:brightness(1.07)}
  .btn.ghost{background:transparent;color:var(--ink);border:1px solid var(--line)}
  h1.lede{font-size:15px;font-weight:500;color:var(--muted);
    margin:22px 0 4px;max-width:760px}
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:18px 0 6px}
  .kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
  .kpi .k{font-size:12px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted)}
  .kpi .v{font-size:17px;font-weight:680;margin-top:6px;line-height:1.35}
  .deal{background:linear-gradient(180deg,#1a2230,#141a24);border:1px solid #2b3a52;
    border-radius:12px;padding:16px 18px;margin:16px 0;font-size:14.5px}
  .deal b{color:var(--accent2)}
  section{margin:30px 0}
  .s-h{display:flex;align-items:baseline;gap:10px;margin:0 0 14px;
    border-bottom:1px solid var(--line);padding-bottom:8px}
  .s-h h2{font-size:18px;margin:0}
  .s-h .sub{color:var(--muted);font-size:13px}
  .grid{display:grid;gap:13px}
  .g3{grid-template-columns:repeat(3,1fr)}
  .g2{grid-template-columns:repeat(2,1fr)}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:14px 15px}
  .card h3{margin:0 0 6px;font-size:15px}
  .card .meta{color:var(--muted);font-size:12.5px}
  .stat{font-size:13.5px;color:var(--ink);margin-top:7px}
  .person{color:var(--accent2);font-size:12.5px;margin-top:8px}
  .tl{list-style:none;margin:0;padding:0}
  .tl li{position:relative;padding:0 0 16px 22px;border-left:2px solid var(--line);margin-left:6px}
  .tl li:last-child{border-left-color:transparent}
  .tl .dot{position:absolute;left:-7px;top:3px;width:12px;height:12px;border-radius:50%;
    background:var(--accent);border:2px solid var(--bg)}
  .tl .d{font-weight:680;font-size:13px;color:var(--accent)}
  .tl .e{font-size:14px}
  .cl{display:flex;gap:12px;align-items:flex-start;padding:11px 0;border-bottom:1px solid var(--line)}
  .cl .ver{flex:0 0 52px;font-weight:700;color:var(--accent2)}
  .cl .dt{color:var(--muted);font-size:12.5px}
  .vids{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
  .vid{background:var(--panel);border:1px solid var(--line);border-radius:11px;overflow:hidden}
  .vid .frame{position:relative;width:100%;aspect-ratio:16/9;background:#000}
  .vid iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
  .vid .cap{padding:10px 12px;font-size:13.5px}
  .feed{list-style:none;margin:0;padding:0}
  .feed li{padding:10px 0;border-bottom:1px solid var(--line)}
  .feed .src{display:inline-block;background:var(--pill);color:var(--muted);
    font-size:11px;padding:2px 8px;border-radius:20px;margin-right:8px}
  .note{color:var(--muted);font-size:12.5px;background:var(--panel2);
    border:1px dashed var(--line);border-radius:10px;padding:12px 14px;margin-top:10px}
  footer{margin-top:40px;border-top:1px solid var(--line);padding-top:16px;
    color:var(--muted);font-size:12.5px}
  @media (max-width:840px){.kpis,.g3,.g2,.vids{grid-template-columns:1fr}}
  @media print{
    header{position:static;background:#fff}
    body{background:#fff;color:#111}
    .no-print{display:none!important}
    .card,.kpi,.deal,.panel,.vid{break-inside:avoid;border-color:#ccc;background:#fff}
    .vid .frame{display:none}
    a{color:#1a4d8f}
    section{break-inside:avoid}
  }
</style>
</head>
<body>
<header>
  <div class="head-in">
    <div class="logo">🖱️ Cursor<span>Watch</span></div>
    <div class="asof" id="asof"></div>
    <div class="spacer"></div>
    <button class="btn ghost no-print" onclick="location.reload()">↻ Refresh</button>
    <button class="btn no-print" onclick="window.print()">⬇ Export to PDF</button>
  </div>
</header>

<div class="wrap">
  <h1 class="lede" id="lede"></h1>

  <div class="kpis" id="kpis"></div>
  <div class="deal" id="deal"></div>

  <section>
    <div class="s-h"><h2>Funding &amp; market trajectory</h2><span class="sub">valuation · ARR · strategic moves</span></div>
    <ul class="tl" id="timeline"></ul>
  </section>

  <section>
    <div class="s-h"><h2>Company adoption</h2><span class="sub">who runs on Cursor — named logos + live signals</span></div>
    <div class="grid g3" id="adopters"></div>
    <div class="note" id="adoption-note"></div>
    <ul class="feed" id="adoption-feed" style="margin-top:12px"></ul>
  </section>

  <section>
    <div class="s-h"><h2>Product velocity</h2><span class="sub">what they shipped — live changelog</span></div>
    <div id="changelog"></div>
  </section>

  <section class="no-print">
    <div class="s-h"><h2>Watch it built</h2><span class="sub">short, real build tutorials &amp; workflow demos</span></div>
    <div class="vids" id="videos"></div>
  </section>

  <section>
    <div class="s-h"><h2>In the news</h2><span class="sub">fresh coverage, refreshed daily</span></div>
    <ul class="feed" id="news"></ul>
  </section>

  <footer id="footer"></footer>
</div>

<script>
const DATA = /*DATA*/null/*DATA*/;
const $ = (id)=>document.getElementById(id);
const e = (s)=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function render(){
  const d = DATA, c = d.company;
  $('asof').textContent = '· as of ' + d.as_of;
  $('lede').textContent = c.one_liner + ' This board tracks Cursor as an investment & market story: funding, real company adoption, product velocity, and the workflows people are actually building.';

  $('kpis').innerHTML = [
    ['Valuation', c.latest_valuation],
    ['Revenue (ARR)', c.latest_arr],
    ['Fortune 500', c.fortune500],
    ['Product', d.changelog[0] ? ('v'+d.changelog[0].version+' · '+d.changelog[0].date) : 'Cursor']
  ].map(([k,v])=>`<div class="kpi"><div class="k">${e(k)}</div><div class="v">${e(v)}</div></div>`).join('');

  $('deal').innerHTML = '<b>⚡ Headline deal —</b> ' + e(c.headline_deal);

  $('timeline').innerHTML = d.funding_timeline.slice().reverse().map(t=>
    `<li><span class="dot"></span><div class="d">${e(t.date)}</div>
     <div class="e">${e(t.event)} ${t.source?`· <a href="${e(t.source)}" target="_blank">source</a>`:''}</div></li>`).join('');

  $('adopters').innerHTML = d.adopters.map(a=>
    `<div class="card"><h3>${e(a.company)}</h3>
     <div class="stat">${e(a.stat)}</div>
     ${a.person?`<div class="person">${e(a.person)}</div>`:''}
     <div class="meta" style="margin-top:8px"><a href="${e(a.source)}" target="_blank">${e((a.source||'').replace(/^https?:\/\/(www\.)?/,'').split('/')[0])}</a></div></div>`).join('');

  $('adoption-note').textContent = 'Note: no reliable "who has Cursor installed" database exists (it is a local desktop app, invisible to web-tech scanners like BuiltWith). The signals below are the next best thing — fresh adoption coverage and hiring mentions, refreshed daily.';

  $('adoption-feed').innerHTML = (d.adoption_signals||[]).map(s=>
    `<li><span class="src">${e(s.source)}</span><a href="${e(s.url)}" target="_blank">${e(s.title)}</a></li>`).join('') || '<li class="meta">No new adoption signals today.</li>';

  $('changelog').innerHTML = (d.changelog||[]).map(cl=>
    `<div class="cl"><div class="ver">${e(cl.version)}</div>
     <div><div class="dt">${e(cl.date)}</div><div>${e(cl.summary)}</div>
     <a class="meta" href="${e(cl.url)}" target="_blank">read →</a></div></div>`).join('') || '<div class="meta">Changelog unavailable.</div>';

  $('videos').innerHTML = (d.videos||[]).map(v=>
    `<div class="vid"><div class="frame"><iframe loading="lazy" src="https://www.youtube-nocookie.com/embed/${e(v.id)}" title="${e(v.title)}" allowfullscreen></iframe></div>
     <div class="cap">${e(v.title)}${v.note?` · <span class="meta">${e(v.note)}</span>`:''}</div></div>`).join('') || '<div class="meta">No videos found.</div>';

  $('news').innerHTML = (d.news||[]).map(s=>
    `<li><span class="src">${e(s.source)}</span><a href="${e(s.url)}" target="_blank">${e(s.title)}</a></li>`).join('') || '<li class="meta">No news today.</li>';

  $('footer').innerHTML = `Generated ${e(d.generated_at)} · scraped &amp; searched via Firecrawl · base facts verified against CNBC, TechCrunch, InfoQ, Engadget, cursor.com.<br>
    <b>Disclaimer:</b> Figures (valuation, ARR, deal terms) come from press reports and may be unconfirmed or change. This is a market-tracking tool, not investment advice — verify before relying on any number.`;
}
render();
</script>
</body>
</html>
"""
