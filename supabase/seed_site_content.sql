-- Import treści ze strony Novoterm (stan HTML/Astro → CMS)
-- Idempotentny: upsert po slug

insert into public.projects (
  slug, title, excerpt, category, location, area_m2, duration,
  featured, gallery, content, seo_title, seo_description,
  status, published_at
)
values
(
  'zaplecze-biurowe-hali-produkcyjnej-wrzesnia',
  'Zaplecze biurowe hali produkcyjnej — Września',
  '860 m² powierzchni biurowo-socjalnej: od stanu surowego do przekazania najemcy w 11 tygodni.',
  'Hale biurowe',
  'Września',
  860,
  '11 tygodni',
  true,
  '[]'::jsonb,
  '{
    "blocks": [
      {"type": "paragraph", "text": "Kompleksowe wykończenie zaplecza biurowego hali produkcyjnej we Wrześni — biura, sale konferencyjne i zaplecze socjalne pod klucz."},
      {"type": "heading", "level": 2, "text": "Zakres prac"},
      {"type": "list", "items": [
        "Zabudowy gipsowo-kartonowe i ścianki działowe",
        "Sufity kasetonowe i podwieszane",
        "Posadzki i wykończenia powierzchni",
        "Elektryka i sanitariaty w zakresie pod klucz"
      ]},
      {"type": "paragraph", "text": "Prace prowadzone równolegle z rozruchem części produkcyjnej. Odbiór bez uwag, w terminie."}
    ]
  }'::jsonb,
  'Zaplecze biurowe hali — Września | Novoterm',
  'Realizacja Novoterm: 860 m² zaplecza biurowego hali produkcyjnej we Wrześni. Pod klucz w 11 tygodni.',
  'published',
  now()
),
(
  'budynek-uslugowo-biurowy-poznan',
  'Budynek usługowo-biurowy — Poznań',
  'Generalne wykonawstwo budynku usługowo-biurowego o powierzchni 1 450 m² w Poznaniu.',
  'Budynki usługowe',
  'Poznań',
  1450,
  'generalne wykonawstwo',
  true,
  '[]'::jsonb,
  '{
    "blocks": [
      {"type": "paragraph", "text": "Generalne wykonawstwo budynku usługowo-biurowego w Poznaniu — jeden wykonawca odpowiedzialny za harmonogram, budżet i odbiór."},
      {"type": "heading", "level": 2, "text": "Zakres"},
      {"type": "list", "items": [
        "Koordynacja robót budowlanych i wykończeniowych",
        "Nadzór podwykonawców i jakości",
        "Dokumentacja powykonawcza i odbiór"
      ]}
    ]
  }'::jsonb,
  'Budynek usługowo-biurowy — Poznań | Novoterm',
  'Realizacja Novoterm w Poznaniu: budynek usługowo-biurowy 1 450 m² w modelu generalnego wykonawstwa.',
  'published',
  now()
),
(
  'izolacja-pur-hali-magazynowej-gniezno',
  'Izolacja PUR hali magazynowej — Gniezno',
  'Natrysk piany poliuretanowej na hali magazynowej o powierzchni 3 200 m² w Gnieźnie.',
  'Obiekty przemysłowe',
  'Gniezno',
  3200,
  'natrysk PUR',
  true,
  '[]'::jsonb,
  '{
    "blocks": [
      {"type": "paragraph", "text": "Izolacja natryskowa PUR hali magazynowej w Gnieźnie — bezspoinowa warstwa o wysokiej skuteczności termicznej."},
      {"type": "list", "items": [
        "Przygotowanie podłoża i zabezpieczenie strefy prac",
        "Natrysk piany zamkniętokomórkowej",
        "Kontrola grubości i ciągłości izolacji"
      ]}
    ]
  }'::jsonb,
  'Izolacja PUR hali magazynowej — Gniezno',
  'Realizacja Novoterm: izolacja natryskowa PUR hali magazynowej 3 200 m² w Gnieźnie.',
  'published',
  now()
),
(
  'open-space-zaplecze-konferencyjne-poznan',
  'Open space z zapleczem konferencyjnym — Poznań',
  'Sucha zabudowa open space z zapleczem konferencyjnym — 620 m² w Poznaniu.',
  'Hale biurowe',
  'Poznań',
  620,
  'sucha zabudowa',
  false,
  '[]'::jsonb,
  '{
    "blocks": [
      {"type": "paragraph", "text": "Aranżacja powierzchni biurowej open space z częścią konferencyjną w Poznaniu w oparciu o systemową suchą zabudowę."}
    ]
  }'::jsonb,
  'Open space konferencyjny — Poznań | Novoterm',
  'Realizacja Novoterm: open space z zapleczem konferencyjnym, 620 m², Poznań.',
  'published',
  now()
),
(
  'pawilon-uslugowy-czescia-biurowa-wrzesnia',
  'Pawilon usługowy z częścią biurową — Września',
  'Wykończenie pawilonu usługowego z częścią biurową — 1 100 m² we Wrześni, pod klucz.',
  'Budynki usługowe',
  'Września',
  1100,
  'pod klucz',
  false,
  '[]'::jsonb,
  '{
    "blocks": [
      {"type": "paragraph", "text": "Kompleksowe wykończenie pawilonu usługowego z częścią biurową we Wrześni w modelu pod klucz."}
    ]
  }'::jsonb,
  'Pawilon usługowy — Września | Novoterm',
  'Realizacja Novoterm: pawilon usługowy z częścią biurową, 1 100 m², Września.',
  'published',
  now()
),
(
  'modernizacja-zaplecza-socjalnego-konin',
  'Modernizacja zaplecza socjalnego — Konin',
  'Modernizacja zaplecza socjalnego 480 m² w Koninie — prace w reżimie działającego zakładu.',
  'Obiekty przemysłowe',
  'Konin',
  480,
  'praca w reżimie zakładu',
  false,
  '[]'::jsonb,
  '{
    "blocks": [
      {"type": "paragraph", "text": "Modernizacja zaplecza socjalnego obiektu przemysłowego w Koninie z zachowaniem ciągłości pracy zakładu."}
    ]
  }'::jsonb,
  'Modernizacja zaplecza — Konin | Novoterm',
  'Realizacja Novoterm: modernizacja zaplecza socjalnego 480 m² w Koninie, w reżimie zakładu.',
  'published',
  now()
),
(
  'termoizolacja-dachu-hali-produkcyjnej-sroda-wlkp',
  'Termoizolacja dachu hali produkcyjnej — Środa Wlkp.',
  'Termoizolacja dachu hali produkcyjnej 2 700 m² w Środzie Wielkopolskiej (λ 0,022).',
  'Izolacje PUR',
  'Środa Wlkp.',
  2700,
  'λ 0,022',
  false,
  '[]'::jsonb,
  '{
    "blocks": [
      {"type": "paragraph", "text": "Natryskowa termoizolacja dachu hali produkcyjnej w Środzie Wielkopolskiej — parametry λ od 0,022 W/mK."}
    ]
  }'::jsonb,
  'Termoizolacja dachu — Środa Wlkp. | Novoterm',
  'Realizacja Novoterm: termoizolacja dachu hali produkcyjnej 2 700 m², Środa Wlkp.',
  'published',
  now()
),
(
  'adaptacja-pietra-biurowego-hali-logistycznej-gniezno',
  'Adaptacja piętra biurowego hali logistycznej — Gniezno',
  'Adaptacja piętra biurowego hali logistycznej — 740 m² w Gnieźnie, realizacja w 9 tygodni.',
  'Hale biurowe',
  'Gniezno',
  740,
  '9 tygodni',
  false,
  '[]'::jsonb,
  '{
    "blocks": [
      {"type": "paragraph", "text": "Adaptacja piętra biurowego w hali logistycznej w Gnieźnie — szybka realizacja bez zakłócania logistyki obiektu."}
    ]
  }'::jsonb,
  'Adaptacja piętra biurowego — Gniezno | Novoterm',
  'Realizacja Novoterm: adaptacja piętra biurowego hali logistycznej, 740 m², Gniezno.',
  'published',
  now()
),
(
  'ocieplenie-poddasza-obiektu-uslugowego-wrzesnia',
  'Ocieplenie poddasza obiektu usługowego — Września',
  'Ocieplenie poddasza obiektu usługowego 390 m² we Wrześni pianą otwartokomórkową.',
  'Izolacje PUR',
  'Września',
  390,
  'piana otwartokomórkowa',
  false,
  '[]'::jsonb,
  '{
    "blocks": [
      {"type": "paragraph", "text": "Ocieplenie poddasza obiektu usługowego we Wrześni pianą poliuretanową otwartokomórkową."}
    ]
  }'::jsonb,
  'Ocieplenie poddasza — Września | Novoterm',
  'Realizacja Novoterm: ocieplenie poddasza obiektu usługowego 390 m², Września.',
  'published',
  now()
)
on conflict (slug) do update set
  title = excluded.title,
  excerpt = excluded.excerpt,
  category = excluded.category,
  location = excluded.location,
  area_m2 = excluded.area_m2,
  duration = excluded.duration,
  featured = excluded.featured,
  content = excluded.content,
  seo_title = excluded.seo_title,
  seo_description = excluded.seo_description,
  status = excluded.status,
  published_at = coalesce(public.projects.published_at, excluded.published_at),
  updated_at = now();

-- Case study flagowy (Września)
insert into public.case_studies (
  project_id, slug, title, challenge, solution, results,
  seo_title, seo_description, status, published_at
)
select
  p.id,
  'zaplecze-biurowe-hali-produkcyjnej-wrzesnia',
  'Zaplecze biurowe hali produkcyjnej — Września',
  '860 m² powierzchni biurowo-socjalnej: od stanu surowego do przekazania najemcy w 11 tygodni.',
  '{
    "blocks": [
      {"type": "paragraph", "text": "Zakres obejmował zabudowy g-k, sufity kasetonowe, posadzki, elektrykę i sanitariaty — całość pod klucz."},
      {"type": "paragraph", "text": "Prace prowadzono równolegle z rozruchem części produkcyjnej, bez kolizji z operacjami inwestora."}
    ]
  }'::jsonb,
  '[
    {"label": "Powierzchnia", "value": "860 m²"},
    {"label": "Czas realizacji", "value": "11 tygodni"},
    {"label": "Wynik", "value": "Odbiór bez uwag, w terminie"}
  ]'::jsonb,
  'Case study: hale biurowe Września | Novoterm',
  'Case study Novoterm: zaplecze biurowe hali produkcyjnej we Wrześni — 860 m² w 11 tygodni.',
  'published',
  now()
from public.projects p
where p.slug = 'zaplecze-biurowe-hali-produkcyjnej-wrzesnia'
on conflict (slug) do update set
  project_id = excluded.project_id,
  title = excluded.title,
  challenge = excluded.challenge,
  solution = excluded.solution,
  results = excluded.results,
  seo_title = excluded.seo_title,
  seo_description = excluded.seo_description,
  status = excluded.status,
  published_at = coalesce(public.case_studies.published_at, excluded.published_at),
  updated_at = now();

-- Strony marketingowe (SEO + skrót treści do panelu CMS)
insert into public.pages (
  slug, title, seo_title, seo_description, content, status, published_at
)
values
(
  'home',
  'Strona główna',
  'Novoterm Budownictwo — generalny wykonawca',
  'Generalny wykonawca wykończeń obiektów biurowych i przemysłowych. Hale biurowe, budynki usługowe, izolacje PUR. Wielkopolska.',
  '{"blocks":[{"type":"paragraph","text":"Generalny wykonawca prac wykończeniowych obiektów biurowych i przemysłowych w Wielkopolsce."}]}'::jsonb,
  'published', now()
),
(
  'o-firmie',
  'O firmie',
  'O firmie — Novoterm Budownictwo',
  'Novoterm Budownictwo — średniej wielkości generalny wykonawca wykończeń obiektów biurowych i przemysłowych. Własne zespoły, cała Wielkopolska.',
  '{"blocks":[{"type":"paragraph","text":"Novoterm Budownictwo — generalny wykonawca wykończeń obiektów biurowych i przemysłowych z własnymi zespołami i zapleczem technicznym."}]}'::jsonb,
  'published', now()
),
(
  'generalne-wykonawstwo',
  'Generalne wykonawstwo',
  'Generalne wykonawstwo 1000–2000 m² | Novoterm',
  'Generalne wykonawstwo budynków usługowych 1000–2000 m² pod klucz. Jeden wykonawca, pełna odpowiedzialność za harmonogram i budżet.',
  '{"blocks":[{"type":"paragraph","text":"Generalne wykonawstwo budynków usługowych 1000–2000 m² pod klucz — jeden wykonawca, pełna odpowiedzialność."}]}'::jsonb,
  'published', now()
),
(
  'specjalizacje-hale-biurowe',
  'Hale biurowe',
  'Hale biurowe — wykończenia pod klucz | Novoterm',
  'Wykończenia hali biurowych i powierzchni biurowych w obiektach przemysłowych. Zabudowy, sufity, posadzki, instalacje — pod klucz.',
  '{"blocks":[{"type":"paragraph","text":"Kompetencja flagowa Novoterm: wykończenia hal biurowych i powierzchni biurowych w obiektach przemysłowych."}]}'::jsonb,
  'published', now()
),
(
  'specjalizacje-obiekty-przemyslowe',
  'Obiekty przemysłowe',
  'Obiekty przemysłowe — wykończenia hal | Novoterm',
  'Wykończenia obiektów przemysłowych: hale produkcyjne, magazyny, zaplecza socjalne. Izolacje PUR, zabudowy, posadzki.',
  '{"blocks":[{"type":"paragraph","text":"Wykończenia obiektów przemysłowych z możliwością pracy w reżimie działającego zakładu."}]}'::jsonb,
  'published', now()
),
(
  'specjalizacje-izolacje-pur',
  'Izolacje natryskowe PUR',
  'Izolacje natryskowe PUR | Novoterm',
  'Natrysk piany poliuretanowej PUR: dachy i ściany hali, stropy, poddasza. Lambda od 0,022 W/mK. Wielkopolska.',
  '{"blocks":[{"type":"paragraph","text":"Natrysk piany poliuretanowej PUR — izolacja bezspoinowa, szybka aplikacja, wysoka energooszczędność."}]}'::jsonb,
  'published', now()
),
(
  'specjalizacje-sucha-zabudowa',
  'Sucha zabudowa',
  'Sucha zabudowa — ścianki i sufity | Novoterm',
  'Systemowa sucha zabudowa: ścianki działowe, sufity podwieszane g-k i kasetonowe, zabudowa poddaszy, szpachlowanie maszynowe.',
  '{"blocks":[{"type":"paragraph","text":"Systemowa sucha zabudowa wykonywana własnymi zespołami Novoterm."}]}'::jsonb,
  'published', now()
),
(
  'proces',
  'Dla inwestorów — proces',
  'Proces współpracy z inwestorem | Novoterm',
  'Jak pracujemy z inwestorami: wycena, harmonogram, nadzór budowy, raportowanie i odbiór z dokumentacją powykonawczą.',
  '{"blocks":[{"type":"paragraph","text":"Przewidywalny proces: wycena, harmonogram, nadzór, raportowanie i odbiór."}]}'::jsonb,
  'published', now()
),
(
  'kontakt',
  'Kontakt',
  'Kontakt — zapytanie ofertowe | Novoterm',
  'Skontaktuj się z Novoterm Budownictwo: +48 726 324 514, biuro@novoterm-budownictwo.pl. Formularz zapytania ofertowego.',
  '{"blocks":[{"type":"paragraph","text":"Zapytanie ofertowe: podaj rodzaj obiektu i metraż. Tel. +48 726 324 514."}]}'::jsonb,
  'published', now()
),
(
  'realizacje',
  'Realizacje',
  'Realizacje — portfolio B2B | Novoterm',
  'Portfolio realizacji Novoterm Budownictwo: hale biurowe, obiekty przemysłowe, budynki usługowe, izolacje PUR.',
  '{"blocks":[{"type":"paragraph","text":"Wybrane projekty z ostatnich lat. Dane referencyjne udostępniamy na życzenie inwestora."}]}'::jsonb,
  'published', now()
)
on conflict (slug) do update set
  title = excluded.title,
  seo_title = excluded.seo_title,
  seo_description = excluded.seo_description,
  content = excluded.content,
  status = excluded.status,
  published_at = coalesce(public.pages.published_at, excluded.published_at),
  updated_at = now();

update public.site_settings
set
  company_name = 'Novoterm Budownictwo',
  phone = '+48 726 324 514',
  email = 'biuro@novoterm-budownictwo.pl',
  street = 'ul. Ciemierów 10',
  postal_code = '62-310',
  city = 'Pyzdry',
  region = 'Wielkopolskie',
  default_seo_title = 'Novoterm Budownictwo',
  default_seo_description = 'Generalny wykonawca prac wykończeniowych obiektów biurowych i przemysłowych w Wielkopolsce.',
  organization_schema = '{
    "@context": "https://schema.org",
    "@type": ["Organization", "LocalBusiness"],
    "name": "Novoterm Budownictwo",
    "telephone": "+48726324514",
    "email": "biuro@novoterm-budownictwo.pl",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "ul. Ciemierów 10",
      "postalCode": "62-310",
      "addressLocality": "Pyzdry",
      "addressRegion": "Wielkopolskie",
      "addressCountry": "PL"
    }
  }'::jsonb,
  updated_at = now()
where id = 'default';
