-- Kolejność realizacji w panelu CMS i na froncie
alter table public.projects
  add column if not exists sort_order integer not null default 0;

create index if not exists projects_sort_order_idx
  on public.projects (sort_order asc, published_at desc);

-- Uzupełnij kolejność istniejących rekordów według daty publikacji
with ordered as (
  select
    id,
    row_number() over (
      order by published_at desc nulls last, updated_at desc
    ) - 1 as rn
  from public.projects
)
update public.projects p
set sort_order = ordered.rn
from ordered
where p.id = ordered.id;
