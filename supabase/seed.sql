-- Podstawowe ustawienia strony.
-- Pełny import treści (projekty, strony, case study): seed_site_content.sql

insert into public.site_settings (
  id,
  default_seo_title,
  default_seo_description,
  organization_schema
)
values (
  'default',
  'Novoterm Budownictwo',
  'Generalny wykonawca prac wykończeniowych obiektów biurowych i przemysłowych w Wielkopolsce.',
  '{
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
  }'::jsonb
)
on conflict (id) do nothing;
