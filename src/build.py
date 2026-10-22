#!/usr/bin/env python3
"""Bygger lillakliniken.com som statiska HTML-filer.

Användning:
  python3 src/build.py                 -> bygger till public/ (för Cloudflare Pages)
  python3 src/build.py --preview DIR   -> bygger en förhandsvisning med relativa länkar

Allt innehåll finns i den här filen. Ändra texter, priser eller Kaddio-länkar här
och kör skriptet igen.
"""
import os
import shutil
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(ROOT, "src", "static")
SITE_URL = "https://lillakliniken.com"

# ---------------------------------------------------------------------------
# Kaddio – direktlänkar. Uppdatera här när behandlingsformerna byter namn.
# ---------------------------------------------------------------------------
K = "https://lillakliniken.kaddio.com"
BOOK_NEW_60 = K + "/booking/cal/psykiater-nybesok-60-min-online"
BOOK_NEW_90 = K + "/booking/cal/psykiater-nybesok-90-min-online"
BOOK_ADHD = K + "/booking/cal/psykiater-nybesok-90-min-online"   # byt till ADHD-frågeställning när den finns
BOOK_RX = K + "/booking/cal/psykiater-forskrivningsfornyelse"
LOGIN = K + "/login"
KDK = "https://lillaklinikendk.kaddio.com"   # dansk enhed (DKK)
DK_FIRST_60 = KDK + "/booking/cal/psykiater-frste-konsultation-60-min-online"
DK_FIRST_90 = KDK + "/booking/cal/psykiater-frste-konsultation-90-min-online"
DK_LOGIN = KDK + "/login"

PHONE_DISPLAY = "070-448 02 40"
PHONE_TEL = "+46704480240"
EMAIL = "info@lillakliniken.com"
EMAIL_DK = "info@lillakliniken.dk"
ADDRESS = "Vändgatan 9, 416 44 Göteborg"
ORG = "GG KONSULT AB, org.nr 559338-1915"
UPDATED = date.today().isoformat()

CHECK = '<svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5L20 7"/></svg>'


class Site:
    def __init__(self, out, preview=False):
        self.out = out
        self.preview = preview
        self.pages = []

    # Link helper: in live mode keep pretty absolute URLs, in preview make them relative.
    def href(self, cur, target):
        if target.startswith(("http", "mailto:", "tel:")):
            return target
        if not self.preview:
            return target
        path, _, frag = target.partition("#")
        cur_dir = cur.strip("/")
        depth = len(cur_dir.split("/")) if cur_dir else 0
        prefix = "../" * depth
        p = path.strip("/")
        rel = prefix + (p + "/" if p else "") + "index.html"
        return rel + ("#" + frag if frag else "")

    def asset(self, cur, a):
        if not self.preview:
            return "/" + a
        cur_dir = cur.strip("/")
        depth = len(cur_dir.split("/")) if cur_dir else 0
        return "../" * depth + a

    def write(self, path, html):
        dest = os.path.join(self.out, path.strip("/"), "index.html") if path != "/404" else os.path.join(self.out, "404.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(html)
        if path != "/404":
            self.pages.append(path)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout(s, path, title, desc, body, lang="sv", alt=None, jsonld=""):
    h = lambda t: s.href(path, t)
    css = s.asset(path, "css/site.css")
    ico = s.asset(path, "favicon.svg")
    canonical = SITE_URL + path
    alt_links = ""
    if alt:
        alt_links = (f'<link rel="alternate" hreflang="sv" href="{SITE_URL}{alt["sv"]}">'
                     f'<link rel="alternate" hreflang="da" href="{SITE_URL}{alt["da"]}">')
    if lang == "sv":
        top = ('<span>Vid akuta besvär: ring 1177 eller 112. Vi bedriver inte akut vård.</span>'
               f'<span class="lang"><a href="{h("/")}" aria-current="true" lang="sv">Svenska</a>'
               f'<a href="{h("/dk/")}" lang="da">Dansk</a></span>')
        nav_items = [("/sa-fungerar-det/", "Så fungerar det"), ("/#vi-hjalper", "Vi hjälper med"),
                     ("/priser/", "Priser"), ("/lakare/", "Läkare"), ("/kontakt/", "Kontakt")]
        actions = (f'<a class="btn btn-ghost" href="{LOGIN}">Logga in</a>'
                   f'<a class="btn btn-primary" href="{BOOK_NEW_60}">Boka läkarbedömning</a>')
        home = "/"
        skip = "Hoppa till innehållet"
        nav_label = "Huvudmeny"
        footer = footer_sv(s, path)
    else:
        top = ('<span>Ved akut behov: kontakt egen læge, lægevagten eller ring 112.</span>'
               f'<span class="lang"><a href="{h("/")}" lang="sv">Svenska</a>'
               f'<a href="{h("/dk/")}" aria-current="true" lang="da">Dansk</a></span>')
        nav_items = [("/dk/#sadan", "Sådan foregår det"), ("/dk/#priser", "Priser"),
                     ("/dk/#laege", "Lægen"), ("/dk/kontakt/", "Kontakt")]
        actions = (f'<a class="btn btn-ghost" href="{DK_LOGIN}">Log ind</a>'
                   f'<a class="btn btn-primary" href="{DK_FIRST_60}">Book konsultation</a>')
        home = "/dk/"
        skip = "Gå til indhold"
        nav_label = "Hovedmenu"
        footer = footer_dk(s, path)
    nav = "".join(
        f'<a href="{h(t)}"{" aria-current=\"page\"" if t == path else ""}>{label}</a>' for t, label in nav_items)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
{alt_links}
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta name="theme-color" content="#16232B">
<link rel="icon" href="{ico}" type="image/svg+xml">
<link rel="stylesheet" href="{css}">
{jsonld}
</head>
<body>
<a class="skip" href="#main">{skip}</a>
<div class="topbar"><div class="wrap">{top}</div></div>
<header class="site-header"><div class="wrap">
<a class="brand" href="{h(home)}"><b>Lillakliniken</b><span>Psykiatri Cura</span></a>
<nav class="nav" aria-label="{nav_label}">{nav}</nav>
<div class="actions">{actions}</div>
</div></header>
<main id="main">
{body}
</main>
{footer}
</body>
</html>
"""


def footer_sv(s, path):
    h = lambda t: s.href(path, t)
    return f"""<footer class="site-footer"><div class="wrap">
<div class="col"><b>Lillakliniken Psykiatri Cura</b>
<span>Specialistpsykiatri för vuxna – online i hela Sverige och på mottagning i Göteborg.</span>
<span>Vårdgivare: {ORG}</span>
<span>Vid akuta besvär: ring 1177 eller 112.</span></div>
<nav class="col" aria-label="Tjänster">
<a href="{h('/psykiater-online/')}">Psykiater online</a>
<a href="{h('/psykiater-goteborg/')}">Psykiater Göteborg</a>
<a href="{h('/adhd/')}">ADHD hos vuxna</a>
<a href="{h('/depression/')}">Depression</a>
<a href="{h('/angest/')}">Ångest</a>
<a href="{h('/second-opinion/')}">Second opinion</a>
<a href="{h('/recept-intyg-remiss/')}">Recept, intyg och remiss</a></nav>
<nav class="col" aria-label="Information">
<a href="{h('/priser/')}">Priser</a>
<a href="{h('/lakare/')}">Våra läkare</a>
<a href="{h('/forskning/')}">Forskning</a>
<a href="{h('/kontakt/')}">Kontakt</a>
<a href="{h('/dk/')}" lang="da">Dansk side</a></nav>
<div class="legal">
<a href="{h('/integritetspolicy/')}">Integritetspolicy</a> ·
<a href="{h('/cookies/')}">Cookies</a> ·
<a href="{h('/patientsakerhet/')}">Patientsäkerhet</a> ·
<a href="{h('/klagomal/')}">Klagomål och synpunkter</a>
<br>© {date.today().year} Lillakliniken Psykiatri Cura</div>
</div></footer>"""


def footer_dk(s, path):
    h = lambda t: s.href(path, t)
    return f"""<footer class="site-footer"><div class="wrap">
<div class="col"><b>Lillakliniken Psykiatri Cura</b>
<span>Speciallæge i psykiatri – videokonsultationer i hele Danmark.</span>
<span>{ORG}</span>
<span>Ved akut behov: kontakt egen læge, lægevagten eller ring 112.</span></div>
<nav class="col" aria-label="Information">
<a href="{h('/dk/kontakt/')}">Kontakt</a>
<a href="{h('/dk/kontakt/')}#klage">Klagevejledning</a>
<a href="{h('/dk/kontakt/')}#privatliv">Privatliv</a>
<a href="{h('/')}" lang="sv">Svensk side</a></nav>
<div class="legal">© {date.today().year} Lillakliniken Psykiatri Cura</div>
</div></footer>"""


def page_hero(s, path, eyebrow, title, lead, crumbs=None, cta=True):
    h = lambda t: s.href(path, t)
    c = ""
    if crumbs:
        c = f'<div class="crumbs"><a href="{h("/")}">Hem</a> / {crumbs}</div>'
    btn = ""
    if cta:
        btn = (f'<div class="actions"><a class="btn btn-primary btn-lg" href="{BOOK_NEW_60}">Boka läkarbedömning</a>'
               f'<a class="btn btn-ghost btn-lg" href="{h("/priser/")}">Se priser</a></div>')
    return f"""<div class="page-hero"><div class="wrap">{c}
<span class="eyebrow">{eyebrow}</span>
<h1>{title}</h1>
<p class="lead">{lead}</p>{btn}
</div></div>"""


def cta_band(s, path, text="Alla börjar med en bedömning hos specialistläkare i psykiatri."):
    return f"""<section class="cta-band"><div class="wrap">
<div style="display:flex;flex-direction:column;gap:6px;max-width:620px"><h2>Redo att boka?</h2><p class="muted">{text}</p></div>
<div class="actions"><a class="btn btn-primary btn-lg" href="{BOOK_NEW_60}">Boka läkarbedömning</a>
<a class="btn btn-ghost btn-lg" href="{LOGIN}">Redan patient? Logga in</a></div>
</div></section>"""


def faq(items):
    return '<div class="faq">' + "".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items) + "</div>"


NOT_FOR_US = """<div class="note">
<h2 style="font-size:1.3rem">Vi är inte rätt mottagning om du</h2>
<ul>
<li>behöver akut hjälp eller har tankar på att ta ditt liv – ring 112 eller sök akut psykiatrisk mottagning</li>
<li>har ett pågående missbruk som behöver behandlas först</li>
<li>söker enbart förskrivning av ett visst läkemedel</li>
</ul>
<p>Råd om vård dygnet runt: ring 1177.</p>
</div>"""


# ---------------------------------------------------------------------------
# Svenska sidor
# ---------------------------------------------------------------------------

def home(s):
    p = "/"
    h = lambda t: s.href(p, t)
    jsonld = f"""<script type="application/ld+json">{{"@context":"https://schema.org","@type":"MedicalClinic","name":"Lillakliniken Psykiatri Cura","url":"{SITE_URL}/","telephone":"{PHONE_TEL}","email":"{EMAIL}","medicalSpecialty":"Psychiatric","address":{{"@type":"PostalAddress","streetAddress":"Vändgatan 9","postalCode":"416 44","addressLocality":"Göteborg","addressCountry":"SE"}},"areaServed":["SE","DK"]}}</script>"""
    body = f"""
<div class="hero"><div class="wrap">
<div class="hero-main">
<span class="eyebrow">Specialistpsykiatri för vuxna</span>
<h1>Psykiater online – i hela Sverige</h1>
<p class="lead">Hos oss träffar du en specialistläkare i psykiatri som bedömer, beslutar och följer upp din behandling. Via video, och på vår mottagning i Göteborg när det behövs.</p>
<div class="actions"><a class="btn btn-primary btn-lg" href="{BOOK_NEW_60}">Boka läkarbedömning</a>
<a class="btn btn-ghost btn-lg" href="{h('/sa-fungerar-det/')}">Så fungerar det</a></div>
</div>
<aside class="hero-side"><div class="price-card">
<h2>Nybesök hos psykiater</h2>
<div class="price-row"><span>60 minuter</span><strong>2 500 kr</strong></div>
<div class="price-row"><span>90 minuter</span><strong>3 500 kr</strong></div>
<ul class="checks">
<li>{CHECK}Specialistläkare i psykiatri</li>
<li>{CHECK}Bokning och inloggning med BankID</li>
<li>{CHECK}Betalas vid bokning</li>
</ul>
</div></aside>
</div></div>

<section aria-labelledby="hjalp"><div class="wrap">
<div class="section-head"><h2 id="hjalp">Hur kan vi hjälpa dig?</h2></div>
<div class="grid grid-3">
<div class="card"><span class="eyebrow">Ny patient</span><h3>Boka en läkarbedömning</h3>
<p class="grow">Alla börjar med en bedömning hos specialistläkare i psykiatri. Läkaren föreslår sedan en plan tillsammans med dig.</p>
<a class="btn btn-primary" href="{BOOK_NEW_60}">Boka nybesök</a></div>
<div class="card"><span class="eyebrow">Redan patient</span><h3>Återbesök och frågor</h3>
<p class="grow">Boka återbesök hos din läkare eller skriv till oss. Logga in med BankID.</p>
<a class="btn btn-ghost" href="{LOGIN}">Logga in</a></div>
<div class="card"><span class="eyebrow">Recept, intyg, remiss</span><h3>Beställ digitalt</h3>
<p class="grow">Receptförnyelse, intyg och remisser för dig som är patient hos oss. Hanteras inom 48 timmar på vardagar.</p>
<a class="btn btn-ghost" href="{h('/recept-intyg-remiss/')}">Så går det till</a></div>
</div>
</div></section>

<section class="band-white" aria-labelledby="steg"><div class="wrap">
<div class="section-head"><h2 id="steg">Så går det till</h2><p class="muted">Samma läkare tar ansvar för din bedömning och din fortsatta behandling.</p></div>
<ol class="steps">
<li><b>Boka och fyll i</b><span>Du bokar med BankID, betalar och fyller i en hälsodeklaration.</span></li>
<li><b>Träffa en specialist</b><span>Du träffar en specialistläkare i psykiatri, oftast via video.</span></li>
<li><b>Bedömning och plan</b><span>Läkaren gör en medicinsk bedömning och föreslår nästa steg.</span></li>
<li><b>Behandling och uppföljning</b><span>Vid behov fortsätter du hos oss – online, eller på mottagningen i Göteborg.</span></li>
</ol>
</div></section>

<section id="vi-hjalper" aria-labelledby="omraden"><div class="wrap">
<div class="section-head"><h2 id="omraden">Vi hjälper vuxna med</h2></div>
<div class="grid">
<a class="card" href="{h('/adhd/')}"><h3>ADHD</h3><p class="grow">Läkarbedömning, utredning och medicinsk behandling för vuxna.</p><span class="more">Läs mer →</span></a>
<a class="card" href="{h('/depression/')}"><h3>Depression</h3><p class="grow">Även långvarig eller svårbehandlad depression, när tidigare behandling inte hjälpt.</p><span class="more">Läs mer →</span></a>
<a class="card" href="{h('/angest/')}"><h3>Ångest</h3><p class="grow">Ångestsyndrom och panikångest, med fokus på stabilisering och funktion.</p><span class="more">Läs mer →</span></a>
<a class="card" href="{h('/second-opinion/')}"><h3>Second opinion</h3><p class="grow">När symtomen är oklara eller du vill ha en ny medicinsk helhetsbedömning.</p><span class="more">Läs mer →</span></a>
</div>
</div></section>

<section style="padding-top:0"><div class="wrap">
<div class="feature">
<div><span class="eyebrow">ADHD hos vuxna</span><h2>Börja med en läkarbedömning</h2>
<p>Läkaren bedömer om en utredning är rätt nästa steg. En fullständig ADHD-utredning görs av psykolog och specialistläkare tillsammans och kostar 26 900 kr.</p>
<p>Läkemedelsbehandling kan aldrig utlovas före en medicinsk bedömning.</p></div>
<div><a class="btn btn-light btn-lg" href="{BOOK_ADHD}">Boka nybesök – ADHD</a>
<a href="{h('/adhd/')}" style="text-align:center;font-weight:600">Läs mer om utredningen</a></div>
</div>
</div></section>

<section class="band-white" aria-labelledby="team"><div class="wrap">
<div class="section-head"><h2 id="team">Våra läkare</h2><p class="muted">Alla våra läkare är specialister i psykiatri och tar personligt medicinskt ansvar för sina patienter.</p></div>
{doctors_grid(s, p, short=True)}
<p style="margin-top:22px"><a href="{h('/lakare/')}">Läs mer om våra läkare →</a></p>
</div></section>

<section><div class="wrap">{NOT_FOR_US}</div></section>
{cta_band(s, p)}
"""
    s.write(p, layout(s, p, "Psykiater online och i Göteborg | Lillakliniken",
                      "Specialistläkare i psykiatri online i hela Sverige och på mottagning i Göteborg. Nybesök 2 500 kr. Boka med BankID.",
                      body, alt={"sv": "/", "da": "/dk/"}, jsonld=jsonld))


DOCTORS = [
    ("giuseppe-guerriero.jpg", "Giuseppe Guerriero", "Specialistläkare i psykiatri · grundare och medicinskt ansvarig",
     "Ser varje människa som en helhet, där symtom är ett uttryck för samspelet mellan kropp, psyke och livssituation. Lång klinisk erfarenhet i Sverige och internationellt, och doktorand vid Sahlgrenska akademin, Göteborgs universitet.",
     "Svenska, italienska, engelska, danska"),
    ("nikolai-magerkurth.jpg", "Nikolai Magerkurth", "Specialistläkare i psykiatri",
     "Humanistisk och fenomenologisk inriktning med en helhetssyn på människan. Ser behandling som en relationell process där samtalet är lika viktigt som läkemedlet.",
     "Svenska, engelska, spanska"),
    ("cecilia-mircica.jpg", "Cecilia Mircica", "Specialistläkare i psykiatri och allmänmedicin",
     "Helhetsinriktad och systemisk, med blick för relationer, familj och livssituation. Kombinerar medicinska och psykologiska perspektiv och har även utbildning i psykologi och psykoterapi.",
     "Svenska, rumänska, engelska"),
]


def doctors_grid(s, path, short=False):
    out = []
    for img, name, role, bio, langs in DOCTORS:
        b = "" if short else f"<p>{bio}</p>"
        src = s.asset(path, "img/" + img)
        out.append(f'<div class="doctor"><img class="photo" src="{src}" alt="{name}" width="120" height="120" loading="lazy"><h3>{name}</h3>'
                   f'<span class="role">{role}</span>{b}<span class="langs">Språk: {langs}</span></div>')
    return '<div class="doctors">' + "".join(out) + "</div>"


def how(s):
    p = "/sa-fungerar-det/"
    h = lambda t: s.href(p, t)
    body = page_hero(s, p, "Så fungerar det", "Från bokning till behandling",
                     "Hos oss börjar alla med en läkarbedömning. Det är specialistläkaren som bedömer, beslutar och följer upp – och som vid behov tar in andra yrkesgrupper.",
                     crumbs="Så fungerar det") + f"""
<section><div class="wrap">
<ol class="steps">
<li><b>Boka och fyll i</b><span>Du väljer tid i vår bokning, loggar in med BankID och betalar. Inför besöket fyller du i en hälsodeklaration.</span></li>
<li><b>Träffa en specialist</b><span>Besöket sker oftast via video. Du behöver en dator eller mobil och en lugn plats där du kan prata ostört.</span></li>
<li><b>Bedömning och plan</b><span>Läkaren gör en medicinsk bedömning och föreslår en plan: behandling, utredning, uppföljning – eller hänvisning om en annan vårdform passar bättre.</span></li>
<li><b>Behandling och uppföljning</b><span>Du fortsätter hos din läkare med återbesök, läkemedelsbehandling och uppföljning efter behov.</span></li>
</ol>
</div></section>
<section class="band-white"><div class="wrap prose">
<h2>Online eller på mottagningen</h2>
<p>De flesta besök sker via video, oavsett var i Sverige du bor. Vår mottagning ligger på {ADDRESS}. Besök på mottagningen bokas efter överenskommelse med din läkare, till exempel när en fysisk undersökning behövs.</p>
<h2>Vad du kan förvänta dig vid första besöket</h2>
<ul>
<li>En genomgång av dina besvär, din bakgrund och tidigare behandling</li>
<li>En medicinsk helhetsbedömning av en specialistläkare i psykiatri</li>
<li>Ett förslag på fortsatt plan som ni går igenom tillsammans</li>
</ul>
<p>Välj 90 minuter om din situation är mer komplex, till exempel om du har flera diagnoser eller lång behandlingshistorik.</p>
<h2>Andra yrkesgrupper</h2>
<p>Läkaren leder vården. Vid behov arbetar vi tillsammans med legitimerad psykolog, till exempel vid utredning av ADHD, och med provtagning via externt laboratorium.</p>
<h2>Betalning och avbokning</h2>
<p>Vi är en privat mottagning utan avtal med regionen. Nybesök betalas vid bokningen. Villkor för avbokning och ombokning framgår när du bokar. Se alla <a href="{h('/priser/')}">priser</a>.</p>
</div></section>
<section><div class="wrap">{NOT_FOR_US}</div></section>
{cta_band(s, p)}"""
    s.write(p, layout(s, p, "Så fungerar det | Lillakliniken",
                      "Så går ett besök hos Lillakliniken till: bokning med BankID, läkarbedömning via video och fortsatt behandling hos samma specialistläkare.", body))


def online(s):
    p = "/psykiater-online/"
    h = lambda t: s.href(p, t)
    body = page_hero(s, p, "Psykiater online", "Psykiater online i hela Sverige",
                     "Träffa en specialistläkare i psykiatri via video – var du än bor i Sverige. Bedömning, läkemedelsbehandling och uppföljning hos samma läkare.",
                     crumbs="Psykiater online") + f"""
<section><div class="wrap prose">
<h2>När passar det att träffa en psykiater online?</h2>
<p>Många söker psykiater vid till exempel ångest eller panik, nedstämdhet, koncentrationssvårigheter, när tidigare behandling inte hjälpt eller när man vill ha en medicinsk helhetsbedömning. Ett videobesök fungerar för de flesta bedömningar och uppföljningar.</p>
<h2>Det här ingår</h2>
<ul>
<li>Bedömning av specialistläkare i psykiatri</li>
<li>Läkemedelsbehandling och uppföljning när det är medicinskt motiverat</li>
<li>Receptförnyelse, intyg och remisser för dig som är patient hos oss</li>
<li>Säker inloggning och journal via BankID</li>
</ul>
<h2>Det här behöver du</h2>
<ul>
<li>BankID</li>
<li>Dator, surfplatta eller mobil med kamera</li>
<li>En lugn plats där du kan prata ostört</li>
</ul>
<p>Föredrar du att träffas på plats? Vi har även <a href="{h('/psykiater-goteborg/')}">mottagning i Göteborg</a>.</p>
</div></section>
<section class="band-white"><div class="wrap">
<div class="section-head"><h2>Vanliga frågor</h2></div>
{faq([
    ("Kan en psykiater skriva ut läkemedel efter ett videobesök?", "Ja, när det är medicinskt motiverat efter en individuell bedömning. Vissa läkemedel kräver tätare uppföljning eller ett besök på plats. Läkemedel kan aldrig utlovas i förväg."),
    ("Behöver jag remiss?", "Nej, du kan boka direkt. Har du journaler eller tidigare utredningar är det bra att ta med information om dem."),
    ("Gäller högkostnadsskyddet?", "Nej. Vi är en privat mottagning utan avtal med regionen, och besöken betalas av dig själv."),
])}
</div></section>
{cta_band(s, p)}"""
    s.write(p, layout(s, p, "Psykiater online – specialistläkare via video | Lillakliniken",
                      "Psykiater online i hela Sverige. Specialistläkare i psykiatri via video, med bokning och journal via BankID. Nybesök från 2 500 kr.", body))


def goteborg(s):
    p = "/psykiater-goteborg/"
    h = lambda t: s.href(p, t)
    body = page_hero(s, p, "Psykiater Göteborg", "Privat psykiater i Göteborg",
                     f"Specialistläkare i psykiatri med mottagning på {ADDRESS}. De flesta besök sker via video, och du träffar läkaren på plats när det behövs.",
                     crumbs="Psykiater Göteborg") + f"""
<section><div class="wrap prose">
<h2>Mottagningen</h2>
<p>Vår mottagning ligger på {ADDRESS}. Besök på plats bokas efter överenskommelse med din läkare, till exempel när en fysisk undersökning behövs eller när det passar behandlingen bättre.</p>
<h2>Så börjar du</h2>
<p>Alla nya patienter börjar med ett nybesök hos en specialistläkare i psykiatri. Det första besöket sker oftast via video, så att du snabbt kommer igång.</p>
<h2>Vi hjälper vuxna med</h2>
<ul>
<li><a href="{h('/adhd/')}">ADHD</a> – läkarbedömning, utredning och behandling</li>
<li><a href="{h('/depression/')}">Depression</a>, även svårbehandlad</li>
<li><a href="{h('/angest/')}">Ångest och panikångest</a></li>
<li><a href="{h('/second-opinion/')}">Second opinion och oklar diagnos</a></li>
</ul>
</div></section>
<section><div class="wrap">{NOT_FOR_US}</div></section>
{cta_band(s, p)}"""
    s.write(p, layout(s, p, "Psykiater Göteborg – privat specialistpsykiatri | Lillakliniken",
                      "Privat psykiater i Göteborg. Specialistläkare i psykiatri med mottagning på Vändgatan 9 och besök via video.", body))


def adhd(s):
    p = "/adhd/"
    h = lambda t: s.href(p, t)
    body = page_hero(s, p, "ADHD hos vuxna", "ADHD hos vuxna – börja med en läkarbedömning",
                     "Vi bedömer, utreder och behandlar ADHD hos vuxna. Alla börjar med ett besök hos en specialistläkare i psykiatri, som bedömer om en utredning är rätt nästa steg.",
                     crumbs="ADHD", cta=False) + f"""
<section><div class="wrap">
<ol class="steps">
<li><b>Läkarbedömning</b><span>Ett nybesök på 90 minuter hos specialistläkare i psykiatri: dina besvär, din bakgrund och om en utredning är motiverad.</span></li>
<li><b>Utredning vid behov</b><span>Om utredning är indicerad görs den av legitimerad psykolog och specialistläkare tillsammans.</span></li>
<li><b>Återkoppling</b><span>Du får ett skriftligt utlåtande med eventuell diagnos, styrkor, svårigheter och rekommendationer.</span></li>
<li><b>Behandling och uppföljning</b><span>Vid behov fortsätter du med medicinsk behandling och uppföljning hos din läkare.</span></li>
</ol>
<div class="actions" style="margin-top:30px"><a class="btn btn-primary btn-lg" href="{BOOK_ADHD}">Boka nybesök – ADHD (90 min)</a></div>
</div></section>
<section class="band-white"><div class="wrap prose">
<h2>Vad ingår i utredningen?</h2>
<ul>
<li>Psykiatrisk anamnes och utvecklingshistoria</li>
<li>Strukturerade intervjuer, till exempel DIVA-5, och om möjligt intervju med en närstående</li>
<li>Neuropsykologisk testning, till exempel WAIS-IV</li>
<li>Skattningsskalor för symtom, funktion och samsjuklighet</li>
<li>Medicinsk bedömning av specialistläkare för att utesluta andra orsaker och bedöma samsjuklighet</li>
<li>Skriftligt utlåtande med rekommendationer</li>
</ul>
<h2>Pris</h2>
<p>Läkarbedömning (nybesök 90 min): 3 500 kr. Fullständig ADHD-utredning med psykolog och specialistläkare: 26 900 kr. Se alla <a href="{h('/priser/')}">priser</a>.</p>
<h2>Om läkemedel</h2>
<p>Läkemedelsbehandling kan aldrig utlovas före en medicinsk bedömning. Centralstimulerande läkemedel förskrivs bara när diagnos och indikation är fastställda, och kräver regelbunden uppföljning.</p>
</div></section>
<section><div class="wrap">
<div class="section-head"><h2>Vanliga frågor</h2></div>
{faq([
    ("Kan jag boka en utredning direkt?", "Nej. Utredningen bokas först efter en läkarbedömning, så att du inte genomgår en utredning som inte behövs."),
    ("Jag har redan en ADHD-diagnos. Kan jag få behandling hos er?", "Ja. Boka ett nybesök och ta med ditt utredningsutlåtande. Läkaren bedömer om och hur behandlingen ska fortsätta."),
    ("Kan ni skriva ut mitt tidigare läkemedel direkt?", "Vi förnyar inte recept på centralstimulerande läkemedel utan en egen bedömning. Det är en fråga om patientsäkerhet."),
])}
</div></section>
{cta_band(s, p)}"""
    s.write(p, layout(s, p, "ADHD hos vuxna – bedömning och utredning | Lillakliniken",
                      "ADHD-bedömning, utredning och behandling för vuxna hos specialistläkare i psykiatri. Utredning med psykolog och läkare: 26 900 kr.", body))


def condition(s, p, eyebrow, title, lead, sections, meta_title, meta_desc, faqs=None):
    body = page_hero(s, p, eyebrow, title, lead, crumbs=eyebrow)
    body += '<section><div class="wrap prose">' + "".join(f"<h2>{h2}</h2>{html}" for h2, html in sections) + "</div></section>"
    if faqs:
        body += f'<section class="band-white"><div class="wrap"><div class="section-head"><h2>Vanliga frågor</h2></div>{faq(faqs)}</div></section>'
    body += f'<section><div class="wrap">{NOT_FOR_US}</div></section>' + cta_band(s, p)
    s.write(p, layout(s, p, meta_title, meta_desc, body))


def conditions(s):
    condition(s, "/depression/", "Depression", "Depression – även när tidigare behandling inte hjälpt",
              "Specialistpsykiatrisk bedömning och behandling av depression, från lindrig till långvarig eller svårbehandlad.",
              [("När kan du behöva träffa en psykiater?", "<p>Om nedstämdheten håller i sig, påverkar arbete och relationer eller inte blivit bättre trots behandling, kan en specialistpsykiatrisk bedömning hjälpa. Särskilt när det finns samsjuklighet eller när diagnosen är oklar.</p>"),
               ("Vad vi gör", "<ul><li>En grundlig medicinsk och psykiatrisk helhetsbedömning</li><li>Genomgång av tidigare behandling, doser och effekter</li><li>Plan för läkemedelsbehandling och uppföljning</li><li>Hänvisning till psykologisk behandling när det behövs</li></ul>"),
               ("Svårbehandlad depression", "<p>När flera behandlingar inte gett tillräcklig effekt behövs ofta en ny bedömning av diagnos, samsjuklighet och behandlingsval. Det är ett område där vi har särskild klinisk och forskningsmässig erfarenhet.</p>")],
              "Depression – psykiater online och i Göteborg | Lillakliniken",
              "Bedömning och behandling av depression, även svårbehandlad, hos specialistläkare i psykiatri. Online i hela Sverige.",
              [("Hur snabbt får jag tid?", "Du ser lediga tider direkt i bokningen."), ("Kan jag fortsätta hos min nuvarande psykolog?", "Ja. Läkaren kan samarbeta med din psykolog eller annan vårdgivare om du vill.")])
    condition(s, "/angest/", "Ångest", "Ångest och panikångest",
              "Specialistpsykiatrisk behandling av ångestsyndrom och panikångest, med fokus på stabilisering, funktion och långsiktig förbättring.",
              [("När kan du behöva träffa en psykiater?", "<p>När ångest eller panikattacker begränsar ditt liv, när tidigare behandling inte hjälpt eller när det finns andra psykiatriska eller kroppsliga besvär samtidigt.</p>"),
               ("Vad vi gör", "<ul><li>Bedömning av typ av ångest och eventuell samsjuklighet</li><li>Läkemedelsbehandling när det är motiverat, med uppföljning</li><li>Råd om och hänvisning till psykologisk behandling</li></ul>")],
              "Ångest och panikångest – psykiater | Lillakliniken",
              "Bedömning och behandling av ångest och panikångest hos specialistläkare i psykiatri, online i hela Sverige och i Göteborg.")
    condition(s, "/second-opinion/", "Second opinion", "Second opinion och oklar diagnos",
              "När symtomen är blandade eller oklara, när du fått olika besked eller när du vill ha en ny medicinsk helhetsbedömning av en specialistläkare i psykiatri.",
              [("Vem passar det för?", "<ul><li>Dig som har flera diagnoser och vill förstå helheten</li><li>Dig som har provat behandling utan tillräcklig effekt</li><li>Dig som vill ha en oberoende bedömning innan du fattar ett beslut om behandling</li></ul>"),
               ("Så går det till", "<p>Boka ett nybesök på 90 minuter. Ta gärna med sammanfattningar av tidigare journaler och utredningar. Du får en bedömning och, om du vill, en skriftlig sammanfattning som du kan ta med till din vårdgivare.</p>")],
              "Second opinion psykiatri – ny bedömning | Lillakliniken",
              "Second opinion och bedömning vid oklar diagnos hos specialistläkare i psykiatri. Online i hela Sverige.")


def rx(s):
    p = "/recept-intyg-remiss/"
    h = lambda t: s.href(p, t)
    body = page_hero(s, p, "För patienter", "Recept, intyg och remiss",
                     "För dig som redan är patient hos oss. Allt beställs digitalt och hanteras inom 48 timmar på vardagar.",
                     crumbs="Recept, intyg och remiss", cta=False) + f"""
<section><div class="wrap prose">
<h2>Receptförnyelse</h2>
<p>Receptförnyelse innebär alltid en medicinsk bedömning av läkare, som går igenom journal, tidigare ordinationer och behandlingsplan. Avgiften (450 kr) gäller bedömningen, även om receptet inte förnyas.</p>
<p><a class="btn btn-primary" href="{BOOK_RX}">Begär receptförnyelse (BankID)</a></p>
<p><b>Boka i stället en tid om</b></p>
<ul>
<li>läkaren tidigare har sagt att återbesök krävs innan nästa recept</li>
<li>du önskar dosändring eller nytt läkemedel</li>
<li>du har nya eller försämrade symtom</li>
<li>du behöver en akut bedömning – ring då 1177 eller 112</li>
</ul>
<p>För narkotikaklassade läkemedel skickas begäran normalt tidigast en vecka innan läkemedlet tar slut, om inte annat har överenskommits med läkaren.</p>
<h2>Intyg och utlåtanden</h2>
<p>Intyg är inte patientbesök och bokas separat. Läkaren skriver intyg utifrån en medicinsk bedömning och journalen. Intyg som i första hand ska användas av någon annan än vården, till exempel Transportstyrelsen, färdtjänst, försäkringsbolag, arbetsgivare eller förskola, är momspliktiga (25 %). Underlag som behövs för din fortsatta vård är momsfria.</p>
<ul>
<li>Sjukintyg till Försäkringskassan (FK7804)</li>
<li>Läkarutlåtande för aktivitets- eller sjukersättning</li>
<li>Läkarintyg till Transportstyrelsen</li>
<li>Färdtjänstintyg</li>
<li>Rättsligt intyg och medicinskt underlag</li>
<li>Specialistunderlag för din fortsatta vård</li>
<li>Läkarintyg till försäkringsbolag, arbetsgivare eller lärosäte</li>
<li>Läkarintyg för förskola</li>
<li>Reseintyg för läkemedel</li>
<li>Medicinsk sammanfattning på begäran</li>
</ul>
<h2>Remiss och provtagning</h2>
<p>Läkaren kan skriva remiss till annan vårdgivare eller till provtagning. Prover tas hos SYNLAB eller samarbetspartner. Laboratoriets kostnad tillkommer, och för hantering av remiss och svar tar vi en administrativ avgift på normalt 150–300 kr per provtagningstillfälle.</p>
<p>Priser för intyg och remiss finns på <a href="{h('/priser/')}">prissidan</a>.</p>
<p><a class="btn btn-ghost" href="{LOGIN}">Logga in och beställ</a></p>
</div></section>"""
    s.write(p, layout(s, p, "Recept, intyg och remiss | Lillakliniken",
                      "Receptförnyelse, intyg och remisser för patienter hos Lillakliniken. Beställ digitalt med BankID – hanteras inom 48 timmar på vardagar.", body))


def prices(s):
    p = "/priser/"
    h = lambda t: s.href(p, t)

    def table(caption, rows):
        r = "".join(f'<tr><td>{a}</td><td>{b}</td><td class="num">{c}</td></tr>' for a, b, c in rows)
        return (f'<div class="table-box"><table><caption>{caption}</caption><thead><tr><th scope="col">Tjänst</th>'
                f'<th scope="col">Tid</th><th scope="col" class="num">Pris</th></tr></thead><tbody>{r}</tbody></table></div>')
    body = page_hero(s, p, "Priser", "Priser",
                     "Vi är en privat mottagning utan avtal med regionen. Högkostnadsskyddet gäller inte. Alla priser i svenska kronor.",
                     crumbs="Priser", cta=False) + f"""
<section><div class="wrap" style="display:flex;flex-direction:column;gap:24px">
{table("Läkarbesök", [("Nybesök hos specialistläkare i psykiatri", "60 min", "2 500 kr"), ("Nybesök vid mer komplex frågeställning", "90 min", "3 500 kr"), ("Återbesök", "30 min", "1 500 kr"), ("Återbesök", "45 min", "2 000 kr"), ("Återbesök", "60 min", "2 500 kr"), ("Telefonrådgivning", "20 min", "750 kr"), ("Anhörigkonsultation", "30 min", "1 500 kr"), ("Anhörigkonsultation", "60 min", "2 500 kr")])}
{table("Utredning", [("ADHD-utredning (psykolog och specialistläkare, inkl. läkarbesök 90 min)", "Flera besök", "26 900 kr")])}
{table("Recept, intyg och administration", [("Receptförnyelse", "–", "450 kr"), ("Kontakt med andra vårdgivare", "20 min", "750 kr"), ("Remissutfärdande", "15 min", "750 kr"), ("Specialistunderlag för vård", "20 min", "1 000 kr"), ("Läkarintyg till försäkringsbolag / arbetsgivare (inkl. moms)", "20 min", "1 250 kr"), ("Reseintyg för läkemedel (inkl. moms)", "20 min", "1 250 kr"), ("Läkarintyg för förskola (inkl. moms)", "20 min", "1 250 kr"), ("Sjukintyg FK7804", "30 min", "1 500 kr"), ("Medicinsk sammanfattning på begäran", "30 min", "1 500 kr"), ("Läkarutlåtande för aktivitets- eller sjukersättning", "60 min", "2 500 kr"), ("Färdtjänstintyg (inkl. moms)", "20 min", "1 875 kr"), ("Läkarintyg Transportstyrelsen (inkl. moms)", "30 min", "1 875 kr"), ("Rättsligt intyg / medicinskt underlag (inkl. moms)", "30 min", "1 875 kr"), ("Administrativ avgift provtagning (labbkostnad tillkommer)", "–", "150–300 kr")])}
</div></section>
<section class="band-white"><div class="wrap prose">
<h2>Villkor</h2>
<ul>
<li>Nybesök betalas vid bokningen.</li>
<li>Villkor för avbokning och ombokning framgår när du bokar.</li>
<li>Tiderna är ungefärliga. Journalföring, bedömning och förskrivning kan ingå i den bokade tiden.</li>
<li>Intyg och administrativa tjänster är inte patientbesök och bokas separat.</li>
</ul>
</div></section>
{cta_band(s, p)}"""
    s.write(p, layout(s, p, "Priser | Lillakliniken Psykiatri Cura",
                      "Priser hos Lillakliniken: nybesök hos psykiater 2 500 kr (60 min), återbesök från 1 500 kr, ADHD-utredning 26 900 kr.", body))


def doctors(s):
    p = "/lakare/"
    body = page_hero(s, p, "Våra läkare", "Specialistläkare i psykiatri",
                     "Hos oss är det läkaren som bedömer, beslutar och följer upp. Alla våra läkare är specialister i psykiatri och tar personligt medicinskt ansvar för sina patienter.",
                     crumbs="Våra läkare") + f"""
<section><div class="wrap">{doctors_grid(s, p)}</div></section>
<section class="band-white"><div class="wrap prose">
<h2>Läkare som vill arbeta med oss</h2>
<p>Vi välkomnar fler specialister i psykiatri i Sverige och Danmark. Du arbetar online i den omfattning som passar dig, och vi sköter bokning, betalning och administration. Skriv till <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div></section>
{cta_band(s, p)}"""
    s.write(p, layout(s, p, "Våra läkare | Lillakliniken Psykiatri Cura",
                      "Möt Lillaklinikens specialistläkare i psykiatri: Giuseppe Guerriero, Nikolai Magerkurth och Cecilia Mircica.", body))


def contact(s):
    p = "/kontakt/"
    body = page_hero(s, p, "Kontakt", "Kontakt",
                     "Skriv helst till oss via vårt kontaktformulär med BankID. Då hamnar ditt meddelande säkert i rätt journal.",
                     crumbs="Kontakt", cta=False) + f"""
<section><div class="wrap">
<div class="grid grid-3">
<div class="card"><h3>Skriv till oss</h3><p class="grow">Logga in med BankID och skicka ett meddelande. Vi svarar inom två arbetsdagar.</p><a class="btn btn-primary" href="{LOGIN}">Öppna kontaktformuläret</a></div>
<div class="card"><h3>Telefon</h3><p class="grow">Vi har begränsad telefontid. Om vi inte kan svara, skriv hellre till oss via kontaktformuläret.</p><p><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p></div>
<div class="card"><h3>Mottagning</h3><p class="grow">{ADDRESS}. Besök på mottagningen sker efter överenskommelse med din läkare.</p><p class="small">E-post för allmänna frågor (inte för personuppgifter eller hälsofrågor): {EMAIL}</p></div>
</div>
</div></section>
<section><div class="wrap">{NOT_FOR_US}</div></section>
<section class="band-white"><div class="wrap prose">
<h2>Vårdgivare</h2>
<p>Lillakliniken Psykiatri Cura drivs av {ORG}, {ADDRESS}.</p>
</div></section>"""
    s.write(p, layout(s, p, "Kontakt | Lillakliniken Psykiatri Cura",
                      "Kontakta Lillakliniken via kontaktformulär med BankID. Mottagning på Vändgatan 9 i Göteborg.", body))


def research(s):
    p = "/forskning/"
    body = page_hero(s, p, "Forskning", "Klinisk forskning och utveckling",
                     "Vår kliniska verksamhet är nära kopplad till forskning inom translationell psykiatri vid Göteborgs universitet.",
                     crumbs="Forskning", cta=False) + f"""
<section><div class="wrap prose">
<h2>Forskningsområden</h2>
<p>Forskningen handlar om sårbarhetsmekanismer vid stress- och traumarelaterade tillstånd, där klinisk psykiatri kombineras med neurovetenskapliga och psykofysiologiska modeller.</p>
<ul>
<li>Stressreglering, autonom reglering och interoception</li>
<li>Icke-invasiv neuromodulering, inom ramen för ett doktorandprojekt</li>
<li>Affektreglering och långsiktig sårbarhet vid PTSD och komplext trauma</li>
<li>ADHD hos vuxna, särskilt vid samsjuklighet och komplex problematik</li>
</ul>
<h2>Forskning och klinik</h2>
<p>Strukturerade kliniska observationer kan ge upphov till nya forskningsfrågor, men klinisk vård ersätter aldrig formella forskningsprotokoll. Forskningen följer etiska och vetenskapliga riktlinjer.</p>
<h2>Kontakt</h2>
<p>Frågor om forskning och samarbeten: research@lillakliniken.com</p>
</div></section>"""
    s.write(p, layout(s, p, "Forskning | Lillakliniken Psykiatri Cura",
                      "Lillakliniken bedriver klinisk forskning inom translationell psykiatri, stressreglering och vuxen-ADHD.", body))


def legal(s, p, title, lead, sections, meta_desc):
    body = page_hero(s, p, "Information", title, lead, crumbs=title, cta=False)
    body += '<section><div class="wrap prose">' + "".join(f"<h2>{h2}</h2>{html}" for h2, html in sections)
    body += f'<p class="small">Senast uppdaterad {UPDATED}.</p></div></section>'
    s.write(p, layout(s, p, f"{title} | Lillakliniken", meta_desc, body))


def legals(s):
    legal(s, "/integritetspolicy/", "Integritetspolicy",
          "Så behandlar vi dina personuppgifter.",
          [("Personuppgiftsansvarig", f"<p>{ORG}, {ADDRESS}, är personuppgiftsansvarig för behandlingen av dina personuppgifter.</p>"),
           ("Vilka uppgifter vi behandlar", "<p>När du är patient behandlar vi uppgifter som behövs för din vård: namn, personnummer, kontaktuppgifter, hälsouppgifter i journalen och uppgifter om bokningar och betalningar.</p>"),
           ("Varför och med vilket stöd", "<p>Vi behandlar uppgifterna för att ge dig vård, föra journal enligt patientdatalagen, administrera bokningar och fakturering samt uppfylla lagkrav. Behandlingen sker med stöd av rättslig förpliktelse och, för hälsouppgifter, för att tillhandahålla hälso- och sjukvård.</p>"),
           ("Var uppgifterna lagras", "<p>Journal, bokning och meddelanden hanteras i vårt journalsystem Kaddio, med inloggning via BankID. Vi skickar inte hälsouppgifter via vanlig e-post eller via webbplatsen.</p>"),
           ("Hur länge vi sparar uppgifterna", "<p>Journaluppgifter sparas så länge patientdatalagen kräver, normalt minst tio år efter den sista anteckningen. Övriga uppgifter sparas så länge de behövs för ändamålet.</p>"),
           ("Dina rättigheter", "<p>Du har rätt att få information om och tillgång till dina uppgifter, begära rättelse och i vissa fall begära begränsning. Journaluppgifter kan inte raderas på begäran utom i de fall lagen medger. Du kan klaga till Integritetsskyddsmyndigheten (IMY).</p>"),
           ("Kontakt", "<p>Frågor om personuppgifter skickar du via kontaktformuläret när du är inloggad, eller till vår postadress.</p>")],
          "Integritetspolicy för Lillakliniken Psykiatri Cura.")
    legal(s, "/cookies/", "Cookies",
          "Den här webbplatsen använder inga cookies för spårning eller marknadsföring.",
          [("Den här webbplatsen", "<p>Webbplatsen sätter inga egna cookies och använder inga analys- eller annonsverktyg. Typsnitten laddas från vår egen server, inte från externa tjänster.</p>"),
           ("Bokning och inloggning", "<p>När du bokar eller loggar in kommer du till vårt journalsystem Kaddio. Där används nödvändiga cookies för inloggning och säkerhet.</p>")],
          "Information om cookies på lillakliniken.com.")
    legal(s, "/patientsakerhet/", "Patientsäkerhet",
          "Så arbetar vi för att vården ska vara säker.",
          [("Vårt arbete", "<p>Vi arbetar systematiskt med kvalitet och patientsäkerhet enligt vårt ledningssystem. Händelser som har medfört eller hade kunnat medföra vårdskada utreds, och allvarliga händelser anmäls till IVO enligt lex Maria.</p>"),
           ("Patientsäkerhetsberättelse", "<p>Varje år sammanfattar vi vårt patientsäkerhetsarbete i en patientsäkerhetsberättelse. Den kan beställas via kontaktformuläret.</p>"),
           ("Förskrivning", "<p>Läkemedel förskrivs alltid efter individuell medicinsk bedömning. För narkotikaklassade läkemedel gäller särskilda rutiner för uppföljning.</p>")],
          "Patientsäkerhet hos Lillakliniken Psykiatri Cura.")
    legal(s, "/klagomal/", "Klagomål och synpunkter",
          "Vi vill veta om något inte blev som du förväntade dig.",
          [("Kontakta oss först", "<p>Skriv till oss via kontaktformuläret när du är inloggad. Vi svarar och utreder ditt klagomål så snart vi kan.</p>"),
           ("Om du inte är nöjd", "<p>Du kan också vända dig till Patientnämnden i din region, som ger stöd och kan hjälpa dig att föra fram dina synpunkter. Inspektionen för vård och omsorg (IVO) tar emot klagomål på vården i vissa fall.</p>")],
          "Så lämnar du klagomål och synpunkter till Lillakliniken.")


# ---------------------------------------------------------------------------
# Danske sider
# ---------------------------------------------------------------------------

def dk_home(s):
    p = "/dk/"
    h = lambda t: s.href(p, t)
    body = f"""
<div class="hero"><div class="wrap">
<div class="hero-main">
<span class="eyebrow">Speciallæge i psykiatri</span>
<h1>Psykiater online – i hele Danmark</h1>
<p class="lead">Psykiatrisk vurdering, medicinsk behandling og opfølgning hos speciallæge i psykiatri. Alle konsultationer foregår som videokonsultation.</p>
<div class="actions"><a class="btn btn-primary btn-lg" href="{DK_FIRST_60}">Book første konsultation</a>
<a class="btn btn-ghost btn-lg" href="#sadan">Sådan foregår det</a></div>
</div>
<aside class="hero-side"><div class="price-card" id="priser">
<h2>Første konsultation</h2>
<div class="price-row"><span>60 minutter</span><strong>2 500 kr.</strong></div>
<div class="price-row"><span>90 minutter</span><strong>3 500 kr.</strong></div>
<ul class="checks">
<li>{CHECK}Kun videokonsultation</li>
<li>{CHECK}Log ind med MitID</li>
<li>{CHECK}Betales ved booking</li>
</ul>
</div></aside>
</div></div>
<section id="sadan" class="band-white"><div class="wrap">
<div class="section-head"><h2>Sådan foregår det</h2></div>
<ol class="steps">
<li><b>Book og udfyld</b><span>Du booker online, logger ind med MitID og udfylder en helbredserklæring.</span></li>
<li><b>Videokonsultation</b><span>Du taler med en speciallæge i psykiatri via video.</span></li>
<li><b>Vurdering og plan</b><span>Lægen foretager en psykiatrisk vurdering og foreslår næste skridt.</span></li>
<li><b>Opfølgning</b><span>Ved behov fortsætter du med opfølgende konsultationer hos samme læge.</span></li>
</ol>
</div></section>
<section><div class="wrap">
<div class="section-head"><h2>Priser</h2><p class="muted">Alle priser i danske kroner.</p></div>
<div class="table-box"><table><thead><tr><th scope="col">Ydelse</th><th scope="col">Tid</th><th scope="col" class="num">Pris</th></tr></thead><tbody>
<tr><td>Første konsultation</td><td>60 min</td><td class="num">2 500 kr.</td></tr>
<tr><td>Første konsultation ved mere kompleks problemstilling</td><td>90 min</td><td class="num">3 500 kr.</td></tr>
<tr><td>Opfølgende konsultation</td><td>30 min</td><td class="num">1 500 kr.</td></tr>
<tr><td>Opfølgende konsultation</td><td>60 min</td><td class="num">2 500 kr.</td></tr>
<tr><td>Epikrise</td><td>–</td><td class="num">Pris oplyses</td></tr>
</tbody></table></div>
</div></section>
<section id="laege" class="band-white"><div class="wrap">
<div class="section-head"><h2>Lægen</h2></div>
<div class="doctors"><div class="doctor"><img class="photo" src="{s.asset(p, 'img/giuseppe-guerriero.jpg')}" alt="Giuseppe Guerriero" width="120" height="120" loading="lazy"><h3>Giuseppe Guerriero</h3>
<span class="role">Speciallæge i psykiatri</span>
<p>Ser hele mennesket, hvor symptomer er udtryk for samspillet mellem krop, psyke og livssituation. Mange års klinisk erfaring i Sverige og internationalt, og ph.d.-studerende ved Göteborgs Universitet.</p>
<span class="langs">Sprog: dansk, svensk, engelsk, italiensk</span></div></div>
</div></section>
<section><div class="wrap"><div class="note">
<h2 style="font-size:1.3rem">Vi er ikke det rette sted, hvis du</h2>
<ul><li>har brug for akut hjælp eller har tanker om at tage dit liv – ring 112</li>
<li>har et aktivt misbrug, der skal behandles først</li>
<li>kun ønsker ordination af et bestemt lægemiddel</li></ul>
<p>Ved akut behov: kontakt egen læge eller lægevagten.</p>
</div></div></section>"""
    s.write(p, layout(s, p, "Psykiater online i Danmark | Lillakliniken",
                      "Speciallæge i psykiatri via video i hele Danmark. Første konsultation fra 2 500 kr. Log ind med MitID.",
                      body, lang="da", alt={"sv": "/", "da": "/dk/"}))


def dk_contact(s):
    p = "/dk/kontakt/"
    body = f"""<div class="page-hero"><div class="wrap"><span class="eyebrow">Kontakt</span><h1>Kontakt</h1>
<p class="lead">Skriv helst til os via kontaktformularen, når du er logget ind. Så havner din besked sikkert i din journal.</p>
<div class="actions"><a class="btn btn-primary" href="{DK_LOGIN}">Log ind og skriv til os</a></div></div></div>
<section><div class="wrap prose">
<p>Generelle spørgsmål (ikke helbredsoplysninger): {EMAIL_DK}</p>
<p>Alle konsultationer i Danmark foregår som videokonsultation. Vi har ingen klinik i Danmark, hvor du kan møde op.</p>
<h2 id="klage">Klagevejledning</h2>
<p>Er du utilfreds, så kontakt os først. Du kan også klage til Styrelsen for Patientklager.</p>
<h2 id="privatliv">Privatliv</h2>
<p>{ORG} er dataansvarlig. Journal, booking og beskeder håndteres i vores journalsystem Kaddio med sikker log ind. Vi sender ikke helbredsoplysninger via almindelig e-mail eller via hjemmesiden. Hjemmesiden bruger ingen cookies til sporing.</p>
</div></section>"""
    s.write(p, layout(s, p, "Kontakt | Lillakliniken Danmark",
                      "Kontakt Lillakliniken i Danmark via sikker kontaktformular. Klagevejledning og privatliv.", body, lang="da"))


def not_found(s):
    p = "/404"
    body = page_hero(s, "/", "404", "Sidan finns inte", "Sidan kan ha flyttats när vi gjorde om webbplatsen.", cta=False)
    body += f'<section><div class="wrap"><div class="actions"><a class="btn btn-primary" href="{s.href("/", "/")}">Till startsidan</a><a class="btn btn-ghost" href="{s.href("/", "/priser/")}">Priser</a></div></div></section>'
    s.write(p, layout(s, "/", "Sidan finns inte | Lillakliniken", "Sidan finns inte.", body))


# ---------------------------------------------------------------------------

def build(out, preview=False):
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    s = Site(out, preview)
    home(s); how(s); online(s); goteborg(s); adhd(s); conditions(s); rx(s); prices(s)
    doctors(s); contact(s); research(s); legals(s); dk_home(s); dk_contact(s); not_found(s)
    for item in os.listdir(STATIC):
        src = os.path.join(STATIC, item)
        dst = os.path.join(out, item)
        (shutil.copytree if os.path.isdir(src) else shutil.copy2)(src, dst)
    if not preview:
        urls = "".join(f"<url><loc>{SITE_URL}{p}</loc></url>" for p in s.pages)
        with open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    else:
        for name in ("_headers", "_redirects", "robots.txt"):
            fp = os.path.join(out, name)
            if os.path.exists(fp):
                os.remove(fp)
    return s.pages


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        pages = build(sys.argv[2], preview=True)
    else:
        pages = build(os.path.join(ROOT, "public"))
    print(f"Byggde {len(pages)} sidor")
