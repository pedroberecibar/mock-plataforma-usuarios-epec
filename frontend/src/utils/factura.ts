import type { FacturaDocumento } from "../api/types";

// Días calendario hasta el vencimiento (negativo si ya venció). `hoy` es
// inyectable para tests; por defecto, la fecha actual a medianoche.
export function diasHastaVencimiento(fechaStr: string, hoy: Date = new Date()): number {
  const ref = new Date(hoy);
  ref.setHours(0, 0, 0, 0);
  const vcto = new Date(`${fechaStr}T00:00:00`);
  return Math.round((vcto.getTime() - ref.getTime()) / (1000 * 60 * 60 * 24));
}

// Documento con el vencimiento más próximo (el más urgente), o null si ninguno
// tiene fecha de vencimiento.
export function proximoVencimiento(
  documentos: FacturaDocumento[],
  hoy: Date = new Date(),
): FacturaDocumento | null {
  const conVcto = documentos.filter((d) => d.fecha_vencimiento);
  if (conVcto.length === 0) return null;
  return conVcto.reduce((a, b) =>
    diasHastaVencimiento(a.fecha_vencimiento!, hoy) <= diasHastaVencimiento(b.fecha_vencimiento!, hoy)
      ? a
      : b,
  );
}

export function textoDiasRestantes(dias: number): string {
  if (dias < 0) return "Vencida";
  if (dias === 0) return "Vence hoy";
  if (dias === 1) return "Vence mañana";
  return `Faltan ${dias} días`;
}

export function formatImporte(importe: number): string {
  return importe.toLocaleString("es-AR", {
    style: "currency",
    currency: "ARS",
    minimumFractionDigits: 2,
  });
}
