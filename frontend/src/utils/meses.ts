export interface MesOpcion {
  value: string; // "YYYY-MM"
  label: string; // "Junio 2026"
}

export function primerDiaDeMes(mes: string): string {
  return `${mes}-01`;
}

export function ultimoDiaDeMes(mes: string): string {
  const [y, m] = mes.split("-").map(Number);
  const dia = new Date(y, m, 0).getDate(); // día 0 del mes siguiente = último del mes
  return `${mes}-${String(dia).padStart(2, "0")}`;
}

/** Última fecha con datos esperable para el mes: hoy si es el mes en curso, fin de mes si es pasado. */
export function ultimoDiaConDatos(mes: string, hoyStr: string): string {
  const mesActual = hoyStr.slice(0, 7);
  return mes === mesActual ? hoyStr : ultimoDiaDeMes(mes);
}

/** Lista de los últimos N meses (incluido el actual), sin meses futuros. */
export function listaMeses(nMeses: number, hoy: Date = new Date()): MesOpcion[] {
  const opciones: MesOpcion[] = [];
  for (let i = 0; i < nMeses; i++) {
    const d = new Date(hoy.getFullYear(), hoy.getMonth() - i, 1);
    const value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    const raw = d.toLocaleDateString("es-AR", { month: "long", year: "numeric" });
    const label = raw.charAt(0).toUpperCase() + raw.slice(1);
    opciones.push({ value, label });
  }
  return opciones;
}
