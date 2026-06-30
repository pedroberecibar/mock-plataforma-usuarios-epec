export async function triggerPoblar(_token: string): Promise<void> {
  // no-op en modo demo — la ingesta real no aplica
}

// Reflejo de RefrescoResult de ../api/ingest. Se re-declara porque el alias de
// gh-pages redirige ../api/ingest → ../mock/ingest (no se puede importar el tipo original).
export interface RefrescoResult {
  ok: boolean;
  datos_hasta: string | null;
}

// En la demo no hay Oracle: el "Actualizar" es un no-op exitoso.
export async function refrescarConsumo(_token: string): Promise<RefrescoResult> {
  return { ok: true, datos_hasta: null };
}
