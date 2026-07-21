import fallbackSnapshot from "../data/content-fallback.json";

export type ContentBlock = {
  type: "heading" | "paragraph" | "list" | "quote" | "image";
  level?: 2 | 3;
  text?: string;
  items?: string[];
  src?: string;
  alt?: string;
};

export type CmsEntry = {
  id: string;
  slug: string;
  title: string;
  seo_title: string;
  seo_description: string;
  content: { blocks?: ContentBlock[]; [key: string]: unknown };
  published_at: string | null;
};

export type CmsProject = CmsEntry & {
  excerpt: string;
  category: string;
  location: string | null;
  area_m2: number | null;
  duration: string | null;
  completion_date: string | null;
  featured?: boolean;
  sort_order?: number;
  cover_image?: string | null;
  gallery: Array<{ src: string; alt: string }>;
};

/** Mapuje etykietę kategorii CMS na klucz filtra na /realizacje */
export function categoryFilterKey(category: string): string {
  const map: Record<string, string> = {
    "Hale biurowe": "hale",
    "Obiekty przemysłowe": "przemyslowe",
    "Budynki usługowe": "uslugowe",
    "Izolacje PUR": "izolacje",
  };
  return map[category] ?? category.toLowerCase().replace(/\s+/g, "-");
}

export function sortProjects(projects: CmsProject[]): CmsProject[] {
  return [...projects].sort((a, b) => {
    const orderA = a.sort_order ?? Number.MAX_SAFE_INTEGER;
    const orderB = b.sort_order ?? Number.MAX_SAFE_INTEGER;
    if (orderA !== orderB) return orderA - orderB;
    const dateA = a.published_at ? Date.parse(a.published_at) : 0;
    const dateB = b.published_at ? Date.parse(b.published_at) : 0;
    return dateB - dateA;
  });
}

export type CmsPost = CmsEntry & {
  excerpt: string;
  tags: string[];
  author_name: string;
};

export type CmsCaseStudy = Omit<CmsEntry, "content"> & {
  challenge: string;
  solution: { blocks?: ContentBlock[] };
  results: Array<{ label: string; value: string }>;
};

export type ContentSnapshot = {
  schema_version: number;
  generated_at: string | null;
  settings: Record<string, unknown> | null;
  media: Array<Record<string, unknown>>;
  pages: CmsEntry[];
  projects: CmsProject[];
  posts: CmsPost[];
  case_studies: CmsCaseStudy[];
};

let snapshotPromise: Promise<ContentSnapshot> | undefined;

async function fetchSnapshot(): Promise<ContentSnapshot> {
  const url = import.meta.env.CMS_EXPORT_URL;
  const token = import.meta.env.CMS_EXPORT_TOKEN;
  const normalize = (snapshot: ContentSnapshot): ContentSnapshot => ({
    ...snapshot,
    projects: sortProjects(snapshot.projects ?? []),
  });

  if (!url || !token) {
    return normalize(fallbackSnapshot as ContentSnapshot);
  }

  try {
    const response = await fetch(url, {
      headers: { "X-Export-Token": token },
      signal: AbortSignal.timeout(90_000),
    });
    if (!response.ok) {
      throw new Error(`CMS zwrócił ${response.status}`);
    }
    return normalize((await response.json()) as ContentSnapshot);
  } catch (error) {
    console.warn("CMS jest niedostępny podczas builda; używam lokalnego snapshotu.", error);
    return normalize(fallbackSnapshot as ContentSnapshot);
  }
}

export function getContentSnapshot(): Promise<ContentSnapshot> {
  snapshotPromise ??= fetchSnapshot();
  return snapshotPromise;
}
