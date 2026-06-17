interface Props {
  datosHasta: string | null;
}

export function CartelLatencia({ datosHasta }: Props) {
  if (!datosHasta) return null;

  const fecha = new Date(datosHasta + "T00:00:00").toLocaleDateString("es-AR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div
      role="status"
      aria-label="latencia de datos"
      style={{
        background: "#fff8e1",
        border: "1px solid #ffe082",
        borderRadius: 6,
        padding: "8px 14px",
        fontSize: 13,
        color: "#5d4037",
        marginBottom: 16,
      }}
    >
      ⚡ Datos disponibles hasta el <strong>{fecha}</strong>. La ingesta se actualiza
      periódicamente.
    </div>
  );
}
