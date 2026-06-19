const BASE = import.meta.env.BASE_URL;
const cache = new Map<string, unknown>();

export async function fixture<T>(name: string): Promise<T> {
  if (!cache.has(name)) {
    const res = await fetch(`${BASE}mock-data/${name}.json`);
    if (!res.ok) throw new Error(`fixture ${name}: HTTP ${res.status}`);
    cache.set(name, await res.json());
  }
  return cache.get(name) as T;
}
