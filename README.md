# Novoterm

Monorepo strony Novoterm z odpornym na uśpienie backendu przepływem publikacji.

## Architektura

- `apps/web` — Astro 7, statyczny frontend publikowany na Vercel.
- `apps/cms` — FastAPI, panel redakcyjny i chroniony eksport treści dla builda.
- `supabase` — deklaratywny schemat PostgreSQL, RLS, seed i konfiguracja Storage.
- `novoterm-site` — niezmienione źródło pierwszego prototypu HTML (backup migracji).
- `scripts/migrate_legacy_to_astro.py` — jednorazowy mechaniczny importer prototypu.

Publiczna strona nie odpytuje Rendera podczas wizyty. Astro pobiera snapshot treści tylko
podczas builda. Jeśli CMS nie odpowiada, build korzysta z
`apps/web/src/data/content-fallback.json`, a ostatni udany deploy pozostaje dostępny na CDN.

## Frontend

Wymagany Node.js 22.12 lub nowszy:

```bash
cd apps/web
npm install
npm run dev
npm run build
```

Zmienne builda opisuje `apps/web/.env.example`.

## CMS

Wymagany Python 3.12 lub nowszy.

### Windows (PowerShell)

```powershell
cd apps/cms
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
# uvloop nie działa na Windows — użyj pliku bez tej zależności:
Get-Content requirements.lock | Where-Object { $_ -notmatch 'uvloop' } | Set-Content requirements.win.lock
pip install -r requirements.win.lock
copy .env.example .env
# uzupełnij .env (Supabase), potem:
uvicorn app.main:app --reload --port 8000
```

### Linux / macOS

```bash
cd apps/cms
python -m venv .venv
.venv/bin/pip install -r requirements.lock
cp .env.example .env
.venv/bin/uvicorn app.main:app --reload
```

Uzupełnij `.env`:
- `DATABASE_URL` — pooler Supabase (port 6543, tryb transakcyjny)
- `SUPABASE_PUBLISHABLE_KEY` — anon / publishable key z Project Settings → API
- `SUPABASE_SERVICE_ROLE_KEY` — wyłącznie w backendzie (upload mediów)

Logowanie do panelu odbywa się przez **Supabase Authentication**. Utwórz użytkownika w
Dashboard → Authentication → Users (Auto Confirm User) i zaloguj się tym emailem oraz hasłem
na `http://127.0.0.1:8000/admin/login`.

Panel pozwala graficznie edytować strony i realizacje (bloki treści, okładka, galeria),
przesyłać media oraz zmieniać kolejność realizacji metodą przeciągnij-i-upuść.

Po wdrożeniu kolumny kolejności uruchom migrację w Supabase SQL Editor:

`supabase/migrations/20260721_add_project_sort_order.sql`

## Panel pod /admin na głównej domenie

Panel CMS (Render) nie jest osobnym adresem dla redaktora — `apps/web/vercel.json`
przekierowuje (rewrite, nie redirect) `/admin/*`, `/api/admin/*` i `/static/*` z domeny
Vercel do usługi `novoterm-cms` na Renderze. Dzięki temu wpisanie `<domena-strony>/admin`
prowadzi od razu do logowania, bez osobnego hosta do zapamiętania.

Jeśli publiczny adres usługi Render różni się od `https://novoterm-cms.onrender.com`
(np. przez zmianę nazwy serwisu albo własną domenę), popraw `destination` we wszystkich
regułach w `apps/web/vercel.json` na aktualny adres.

## Publikacja treści

1. Redaktor zapisuje i publikuje treść w CMS.
2. CMS zapisuje ją w Supabase.
3. Przycisk „Opublikuj na Vercel” wywołuje `VERCEL_DEPLOY_HOOK`.
4. Build Astro pobiera `/api/export/site` z nagłówkiem `X-Export-Token`.
5. Vercel udostępnia gotowy HTML z CDN; Render może ponownie zasnąć.

## Weryfikacja

```bash
cd apps/cms
.venv/bin/ruff check app tests
PYTHONPATH=. .venv/bin/pytest -q

cd ../web
npm run build
```
