"""Build a portable photography portfolio using only the Python standard library."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'content.json').read_text())
esc = lambda value: escape(str(value), quote=True)
collections = data['collections']
has_samples = any(p.get('sample', False) for c in collections for p in c['photos'])
name = data.get('name', '').strip()
email = data.get('email', '').strip()
location = data.get('location', '').strip()
role = data.get('role', '').strip()
profile_note = data.get('profileNote', '').strip()
nav = [('index.html', 'Home')] + [(c['slug'] + '.html', c['title']) for c in collections] + [('about.html', 'About'), ('contact.html', 'Contact')]

def image(src, alt, cls='', eager=False):
    # Optional thumbnail variants keep the portable site light on mobile.
    source_path = Path(src)
    thumb = str(source_path.with_name(source_path.stem + '-thumb' + source_path.suffix))
    variants = f' srcset="{esc(thumb)} 720w, {esc(src)} 1600w" sizes="(max-width: 767px) calc(100vw - 40px), 90vw"' if (ROOT / thumb).is_file() else ''
    return f'<img src="{esc(src)}"{variants} alt="{esc(alt)}" width="1600" height="1100" class="{cls}" loading="{"eager" if eager else "lazy"}" decoding="async" {"fetchpriority=high" if eager else ""}>'

def arrow():
    return '<span aria-hidden="true" class="arrow">↗</span>'

def link(href, label, cls='text-link'):
    return f'<a href="{esc(href)}" class="{cls}">{esc(label)}{arrow()}</a>'

def page(filename, title, content):
    links = ''.join(f'<a href="{url}" {"aria-current=page" if filename == url else ""}>{label}</a>' for url, label in nav)
    draft_parts = []
    if has_samples: draft_parts.append('Sample photographs')
    if not name: draft_parts.append('Name to be added')
    if data.get('introIsDraft'): draft_parts.append('Biography is a draft')
    draft = 'Preview · ' + ' · '.join(draft_parts) if draft_parts else ''
    footer = f'''<footer class="site-footer shell"><div class="footer-main"><a class="footer-brand" href="index.html">{esc(data['siteTitle'])}<span>PHOTOGRAPHY PORTFOLIO</span></a><p>Observe. Capture. Share.</p>{link('contact.html', 'Contact')}</div><div class="footer-bottom"><span>{esc(name) + ' · ' if name else ''}Personal photography portfolio</span><span>{esc(draft)}</span></div></footer>'''
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>{esc(title)} | {esc(data['siteTitle'])}</title><meta name="description" content="{esc(data['siteTitle'])}. A personal photography portfolio featuring landscapes, city streets and everyday observations."><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head>
<body><a href="#main" class="skip-link">Skip to main content</a><header class="site-header"><div class="header-inner shell"><a class="brand" href="index.html" aria-label="{esc(data['siteTitle'])} Home"><span class="brand-mark" aria-hidden="true"></span><span>{esc(data['siteTitle'])}</span><span class="brand-divider" aria-hidden="true"></span><span class="brand-subtitle">Photography portfolio</span></a><button class="menu-toggle" aria-label="Open navigation menu" aria-expanded="false" aria-controls="primary-nav"><span></span><span></span></button><nav id="primary-nav" aria-label="Main navigation">{links}</nav></div></header><main id="main">{content}</main>{footer}<div class="toast" role="status" aria-live="polite"></div></body></html>'''
    (ROOT / filename).write_text(html, encoding='utf-8')

hero = collections[0]
tiles = ''.join(f'''<article class="collection"><a class="collection-image" href="{esc(c['slug'])}.html">{image(c['cover'], c['coverAlt'])}<span class="image-link" aria-hidden="true">↗</span></a><div class="collection-meta"><div><h3><a href="{esc(c['slug'])}.html">{esc(c['title'])}</a></h3><p>{esc(c['description'])}</p></div><span class="collection-count">{len(c['photos']):02d} {'sample photos' if any(p.get('sample') for p in c['photos']) else 'photographs'}</span></div></article>''' for c in collections)
page('index.html', 'Home', f'''
<section class="home-hero shell"><div class="hero-heading"><div><p class="eyebrow">PHOTOGRAPHY PORTFOLIO</p><h1>A closer look.</h1><p class="hero-intro">Everyday moments. Places further afield.</p></div>{link('#collections', 'View work', 'outline-link')}</div><a class="hero-image" href="{esc(hero['slug'])}.html" aria-label="Explore landscape photographs">{image(hero['cover'], hero['coverAlt'], eager=True)}</a><div class="hero-caption"><span>{esc(data['siteTitle'])}<span class="caption-divider">/</span>{esc(hero['title'])}</span><span>{'Sample photograph · To be replaced' if has_samples else 'Photographs'}</span></div></section>
<section class="collections-section shell" id="collections"><div class="section-heading"><h2>Selected collections</h2><p>Two perspectives, from open landscapes to city streets.</p></div><div class="collections-grid">{tiles}</div></section>
<section class="home-about shell"><div class="about-label">About</div><div><h2>It starts with noticing.</h2><p>{esc(data['intro'])}</p>{link('about.html', 'Read more')}</div><div class="about-monogram" aria-hidden="true">B<br>L</div></section>''')

dialog = '''<dialog class="lightbox" aria-labelledby="lightbox-title"><div class="lightbox-top"><span id="lightbox-counter"></span><button class="lightbox-close" aria-label="Close image viewer">Close <span aria-hidden="true">×</span></button></div><div class="lightbox-stage"><button class="lightbox-prev" aria-label="Previous photograph">←</button><img id="lightbox-image" alt=""><button class="lightbox-next" aria-label="Next photograph">→</button></div><div class="lightbox-caption"><h2 id="lightbox-title"></h2><p id="lightbox-note"></p></div></dialog>'''
for index, collection in enumerate(collections):
    figures = []
    for i, photo in enumerate(collection['photos']):
        note = 'Sample photograph · To be replaced' if photo.get('sample') else photo.get('caption', '')
        figures.append(f'''<figure class="photo-item"><a href="{esc(photo['src'])}" class="photo-open" data-photo data-title="{esc(photo['title'])}" data-note="{esc(note)}" aria-label="View full size: {esc(photo['title'])}">{image(photo['src'], photo['alt'], eager=i < 2)}<span class="photo-zoom" aria-hidden="true">View full size ↗</span></a><figcaption><span class="photo-title">{esc(photo['title'])}</span><span>{esc(note)}</span></figcaption></figure>''')
    other = collections[(index + 1) % len(collections)]
    page(collection['slug'] + '.html', collection['title'], f'''<section class="collection-page shell"><div class="page-heading"><a class="back-link" href="index.html#collections">← All collections</a><p class="eyebrow">{esc(collection['english'])}</p><h1>{esc(collection['title'])}</h1><p class="page-intro">{esc(collection['description'])}</p><div class="gallery-meta"><span>{len(collection['photos']):02d} {'sample photos' if any(p.get('sample') for p in collection['photos']) else 'photographs'}</span><span>Select a photograph to view it in full</span></div></div><div class="photo-grid">{''.join(figures)}</div><div class="next-collection"><div><p>Explore next</p><h2>{esc(other['title'])}</h2></div>{link(other['slug'] + '.html', 'View collection', 'outline-link')}</div></section>{dialog}''')

profile_fields = [('Name', name or 'To be added')]
if role:
    profile_fields.append(('Role', role))
if location:
    profile_fields.append(('Based in', location))
profile_fields.append(('Subjects', ' / '.join(c['title'] for c in collections)))
profile_rows = ''.join(f'<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>' for label, value in profile_fields)
series_links = ''.join(f'<article><h3>{link(c["slug"] + ".html", c["title"])}</h3><p>{esc(c["description"])}</p></article>' for c in collections)
page('about.html', 'About', f'''<section class="about-page shell"><div class="page-heading"><p class="eyebrow">ABOUT</p><h1>About</h1><p class="page-intro">Photography is a way of looking at the world.</p></div><div class="about-layout"><figure class="about-photo">{image(collections[0]['photos'][1]['src'], collections[0]['photos'][1]['alt'], eager=True)}<figcaption>{'Sample photograph. To be replaced with original work.' if has_samples else 'Original photography'}</figcaption></figure><div class="about-copy"><h2>Hello,<br>welcome to my portfolio.</h2><p>{esc(data['intro'])}</p><p>The photographs are arranged into landscape and city collections. Browse by subject, or open an image to take a closer look at the details.</p>{f'<p class="profile-note">{esc(profile_note)}</p>' if profile_note else ''}{'<p class="draft-note">Draft biography. Personal background will be added.</p>' if data.get('introIsDraft') else ''}<div class="profile-details"><h3>At a glance</h3><dl>{profile_rows}</dl></div>{link('contact.html', 'Contact', 'outline-link')}</div></div><section class="about-series"><h2>About this portfolio</h2><p>Two collections offer different ways to explore the photographs.</p><div class="about-series-grid">{series_links}</div></section></section>''')

if email:
    contact = f'''<span class="contact-label">Email</span><a class="email-address" href="mailto:{quote(email, safe='@.+')}">{esc(email)}</a><div class="contact-actions">{link('mailto:' + email, 'Send email', 'solid-link')}<button class="outline-link" data-copy-email="{esc(email)}">Copy email<span aria-hidden="true">＋</span></button></div><p class="contact-hint">Select “Send email” to open your email app.</p>'''
else:
    contact = '''<span class="contact-label">Email</span><h2 class="pending-email">Email address to be added</h2><p class="contact-hint">A contact email will be added before this portfolio is published.</p>'''
contact_note = data.get('contactNote', '').strip() or 'Get in touch to discuss photographs or learning opportunities.'
page('contact.html', 'Contact', f'''<section class="contact-page shell"><div class="page-heading"><p class="eyebrow">CONTACT</p><h1>Start with a hello.</h1><p class="page-intro">{esc(contact_note)}</p></div><div class="contact-layout"><div class="contact-details">{contact}<section class="contact-profile"><h2>What we can talk about</h2><div class="contact-topic"><h3>Thoughts on the work</h3><p>Have a thought about a photograph? Include its title and collection, and share what caught your attention.</p></div><div class="contact-topic"><h3>Projects and learning</h3><p>For a course project or learning opportunity, share the topic, timing and what you would like to discuss.</p></div></section><div class="contact-secondary"><p>Get to know me through the work and the story behind it.</p><div class="contact-links">{link('index.html#collections', 'View work')}{link('about.html', 'About')}</div></div></div><figure class="contact-image">{image(collections[1]['cover'], collections[1]['coverAlt'], eager=True)}<figcaption>{'Sample photograph · To be replaced' if has_samples else collections[1]['title']}</figcaption></figure></div></section>''')
print('Built: ' + ', '.join(url for url, _ in nav))
