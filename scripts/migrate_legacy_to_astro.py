"""Mechaniczna migracja treści istniejącej strony HTML do stron Astro."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "novoterm-site"
WEB = ROOT / "apps" / "web"

PAGES = {
    "index.html": "index.astro",
    "o-firmie.html": "o-firmie.astro",
    "generalne-wykonawstwo.html": "generalne-wykonawstwo.astro",
    "specjalizacje-hale-biurowe.html": "specjalizacje-hale-biurowe.astro",
    "specjalizacje-obiekty-przemyslowe.html": "specjalizacje-obiekty-przemyslowe.astro",
    "specjalizacje-izolacje-pur.html": "specjalizacje-izolacje-pur.astro",
    "specjalizacje-sucha-zabudowa.html": "specjalizacje-sucha-zabudowa.astro",
    "realizacje.html": "realizacje.astro",
    "proces.html": "proces.astro",
    "kontakt.html": "kontakt.astro",
}


def extract(pattern: str, source: str, file_name: str) -> str:
    match = re.search(pattern, source, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError(f"Nie znaleziono wymaganej sekcji w {file_name}")
    return match.group(1).strip()


def clean_links(content: str) -> str:
    content = content.replace('src="assets/', 'src="/assets/')
    for legacy_name, astro_name in PAGES.items():
        route = "/" if astro_name == "index.astro" else f"/{astro_name.removesuffix('.astro')}"
        content = content.replace(f'href="{legacy_name}', f'href="{route}')
    return content


def migrate_pages() -> None:
    pages_dir = WEB / "src" / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    for legacy_name, astro_name in PAGES.items():
        source = (LEGACY / legacy_name).read_text(encoding="utf-8")
        title = extract(r"<title>(.*?)</title>", source, legacy_name)
        description = extract(
            r'<meta\s+name="description"\s+content="(.*?)"\s*/?>',
            source,
            legacy_name,
        )
        main = clean_links(extract(r"(<main\b.*?</main>)", source, legacy_name))
        solid_header = "header--solid" in source
        page = (
            "---\n"
            'import Layout from "../layouts/Layout.astro";\n'
            f"const title = {json.dumps(title, ensure_ascii=False)};\n"
            f"const description = {json.dumps(description, ensure_ascii=False)};\n"
            "---\n\n"
            f"<Layout {{title}} {{description}} solidHeader={{{str(solid_header).lower()}}}>\n"
            f"{main}\n"
            "</Layout>\n"
        )
        (pages_dir / astro_name).write_text(page, encoding="utf-8")


def copy_static_files() -> None:
    styles_dir = WEB / "src" / "styles"
    scripts_dir = WEB / "public" / "scripts"
    assets_dir = WEB / "public" / "assets"
    styles_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(LEGACY / "css" / "main.css", styles_dir / "global.css")
    shutil.copyfile(LEGACY / "js" / "main.js", scripts_dir / "main.js")
    for asset in (LEGACY / "assets").iterdir():
        if asset.is_file():
            shutil.copyfile(asset, assets_dir / asset.name)
    shutil.copyfile(LEGACY / "assets" / "favicon.svg", WEB / "public" / "favicon.svg")
    shutil.copyfile(LEGACY / "assets" / "logo.svg", WEB / "public" / "logo.svg")


if __name__ == "__main__":
    copy_static_files()
    migrate_pages()
    print(f"Zmigrowano {len(PAGES)} stron do {WEB}")
