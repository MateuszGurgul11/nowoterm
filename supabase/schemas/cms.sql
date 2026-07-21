create schema if not exists private;
revoke all on schema private from public, anon, authenticated;

create type public.content_status as enum ('draft', 'published', 'archived');

create table public.media (
  id uuid primary key default gen_random_uuid(),
  storage_path text not null unique,
  public_url text not null,
  file_name text not null,
  mime_type text not null,
  alt_text text not null default '',
  width integer check (width is null or width > 0),
  height integer check (height is null or height > 0),
  size_bytes bigint check (size_bytes is null or size_bytes >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.site_settings (
  id text primary key default 'default' check (id = 'default'),
  company_name text not null default 'Novoterm Budownictwo',
  phone text not null default '+48 726 324 514',
  email text not null default 'biuro@novoterm-budownictwo.pl',
  street text not null default 'ul. Ciemierów 10',
  postal_code text not null default '62-310',
  city text not null default 'Pyzdry',
  region text not null default 'Wielkopolskie',
  social_links jsonb not null default '{}'::jsonb check (jsonb_typeof(social_links) = 'object'),
  default_seo_title text not null default 'Novoterm Budownictwo',
  default_seo_description text not null default '',
  default_og_image_id uuid references public.media(id) on delete set null,
  organization_schema jsonb not null default '{}'::jsonb check (jsonb_typeof(organization_schema) = 'object'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.pages (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  title text not null,
  seo_title text not null check (char_length(seo_title) between 1 and 70),
  seo_description text not null check (char_length(seo_description) between 1 and 180),
  og_image_id uuid references public.media(id) on delete set null,
  content jsonb not null default '{}'::jsonb check (jsonb_typeof(content) = 'object'),
  status public.content_status not null default 'draft',
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (status <> 'published' or published_at is not null)
);

create table public.projects (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  title text not null,
  excerpt text not null default '',
  category text not null,
  location text,
  area_m2 numeric(12, 2) check (area_m2 is null or area_m2 > 0),
  duration text,
  completion_date date,
  featured boolean not null default false,
  sort_order integer not null default 0,
  cover_image_id uuid references public.media(id) on delete set null,
  gallery jsonb not null default '[]'::jsonb check (jsonb_typeof(gallery) = 'array'),
  content jsonb not null default '{}'::jsonb check (jsonb_typeof(content) = 'object'),
  seo_title text not null check (char_length(seo_title) between 1 and 70),
  seo_description text not null check (char_length(seo_description) between 1 and 180),
  status public.content_status not null default 'draft',
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (status <> 'published' or published_at is not null)
);

create table public.posts (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  title text not null,
  excerpt text not null default '',
  content jsonb not null default '{}'::jsonb check (jsonb_typeof(content) = 'object'),
  tags text[] not null default '{}',
  author_name text not null default 'Novoterm Budownictwo',
  cover_image_id uuid references public.media(id) on delete set null,
  seo_title text not null check (char_length(seo_title) between 1 and 70),
  seo_description text not null check (char_length(seo_description) between 1 and 180),
  status public.content_status not null default 'draft',
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (status <> 'published' or published_at is not null)
);

create table public.case_studies (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references public.projects(id) on delete set null,
  slug text not null unique check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  title text not null,
  challenge text not null default '',
  solution jsonb not null default '{}'::jsonb check (jsonb_typeof(solution) = 'object'),
  results jsonb not null default '[]'::jsonb check (jsonb_typeof(results) = 'array'),
  cover_image_id uuid references public.media(id) on delete set null,
  seo_title text not null check (char_length(seo_title) between 1 and 70),
  seo_description text not null check (char_length(seo_description) between 1 and 180),
  status public.content_status not null default 'draft',
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (status <> 'published' or published_at is not null)
);

create index pages_published_idx
  on public.pages (published_at desc)
  where status = 'published';
create index projects_published_idx
  on public.projects (published_at desc)
  where status = 'published';
create index projects_sort_order_idx
  on public.projects (sort_order asc, published_at desc);
create index projects_category_published_idx
  on public.projects (category, published_at desc)
  where status = 'published';
create index posts_published_idx
  on public.posts (published_at desc)
  where status = 'published';
create index posts_tags_idx on public.posts using gin (tags);
create index case_studies_published_idx
  on public.case_studies (published_at desc)
  where status = 'published';
create index site_settings_default_og_image_id_idx on public.site_settings (default_og_image_id);
create index pages_og_image_id_idx on public.pages (og_image_id);
create index projects_cover_image_id_idx on public.projects (cover_image_id);
create index posts_cover_image_id_idx on public.posts (cover_image_id);
create index case_studies_project_id_idx on public.case_studies (project_id);
create index case_studies_cover_image_id_idx on public.case_studies (cover_image_id);

create function private.set_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

revoke all on function private.set_updated_at() from public, anon, authenticated;

create trigger media_set_updated_at
before update on public.media
for each row execute function private.set_updated_at();
create trigger site_settings_set_updated_at
before update on public.site_settings
for each row execute function private.set_updated_at();
create trigger pages_set_updated_at
before update on public.pages
for each row execute function private.set_updated_at();
create trigger projects_set_updated_at
before update on public.projects
for each row execute function private.set_updated_at();
create trigger posts_set_updated_at
before update on public.posts
for each row execute function private.set_updated_at();
create trigger case_studies_set_updated_at
before update on public.case_studies
for each row execute function private.set_updated_at();

alter table public.media enable row level security;
alter table public.site_settings enable row level security;
alter table public.pages enable row level security;
alter table public.projects enable row level security;
alter table public.posts enable row level security;
alter table public.case_studies enable row level security;

create policy "deny_api_access" on public.media
  for all to anon, authenticated using (false) with check (false);
create policy "deny_api_access" on public.site_settings
  for all to anon, authenticated using (false) with check (false);
create policy "deny_api_access" on public.pages
  for all to anon, authenticated using (false) with check (false);
create policy "deny_api_access" on public.projects
  for all to anon, authenticated using (false) with check (false);
create policy "deny_api_access" on public.posts
  for all to anon, authenticated using (false) with check (false);
create policy "deny_api_access" on public.case_studies
  for all to anon, authenticated using (false) with check (false);

revoke all on table public.media from anon, authenticated;
revoke all on table public.site_settings from anon, authenticated;
revoke all on table public.pages from anon, authenticated;
revoke all on table public.projects from anon, authenticated;
revoke all on table public.posts from anon, authenticated;
revoke all on table public.case_studies from anon, authenticated;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'media',
  'media',
  true,
  10485760,
  array['image/jpeg', 'image/png', 'image/webp', 'image/avif', 'image/svg+xml']
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;
