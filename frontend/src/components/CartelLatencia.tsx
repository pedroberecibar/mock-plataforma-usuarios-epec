import { fg, font, fontSize, radius, space } from "../design-tokens";

interface Props {
  datosHasta: string | null;
}

export function CartelLatencia({ datosHasta }: Props) {
  if (!datosHasta) return null;

  const fecha = new Date(datosHasta + "T00:00:00").toLocaleDateString("es-AR", {
    day:   "numeric",
    month: "long",
    year:  "numeric",
  });

  return (
    <div
      role="status"
      aria-label="latencia de datos"
      style={{
        background:   "rgba(230,145,10,0.06)",
        borderLeft:   "3px solid #e6910a",
        borderRadius: `0 ${radius.sm}px ${radius.sm}px 0`,
        padding:      `${space[2]}px ${space[4]}px`,
        fontFamily:   font.sans,
        fontSize:     fontSize.sm,
        color:        fg.secondary,
        marginBottom: space[4],
      }}
    >
      ⚡ Datos disponibles hasta el <strong>{fecha}</strong>. La ingesta se actualiza
      periódicamente.
    </div>
  );
}
