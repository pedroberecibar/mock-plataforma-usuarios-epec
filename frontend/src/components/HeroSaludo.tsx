import {
  bg,
  border,
  fg,
  font,
  fontSize,
  fontWeight,
  lineHeight,
  space,
} from "../design-tokens";

interface DatoCuenta {
  label: string;
  valor: string;
}

interface Props {
  nombre: string | null;
  nroSuministro: string;
  tarifaCodigo?: string | null;
  mesLabel?: string;
}

function primerNombre(nombreCompleto: string | null): string {
  if (!nombreCompleto) return "";
  return nombreCompleto.split(" ")[0] ?? nombreCompleto;
}

function mesActualLabel(): string {
  return new Date().toLocaleDateString("es-AR", {
    month: "long",
    year: "numeric",
    timeZone: "America/Argentina/Cordoba",
  });
}

export function HeroSaludo({ nombre, nroSuministro, tarifaCodigo, mesLabel }: Props) {
  const saludo = nombre ? `Hola, ${primerNombre(nombre)}.` : "Bienvenido.";
  const periodo = mesLabel ?? mesActualLabel();

  const datos: DatoCuenta[] = [
    { label: "N° Suministro", valor: nroSuministro },
    ...(tarifaCodigo ? [{ label: "Tarifa", valor: tarifaCodigo }] : []),
  ];

  return (
    <header
      style={{
        background:    bg.surfaceFeat,
        borderBottom:  `1px solid ${border.default}`,
        padding:       `${space[8]}px ${space[10]}px`,
        display:       "flex",
        justifyContent: "space-between",
        alignItems:    "flex-start",
        gap:           space[8],
      }}
    >
      {/* Saludo */}
      <div>
        <h1
          style={{
            fontFamily:    font.technical,
            fontSize:      fontSize["3xl"],
            fontWeight:    fontWeight.bold,
            color:         fg.primary,
            letterSpacing: "-0.02em",
            lineHeight:    lineHeight.tight,
            margin:        0,
          }}
        >
          {saludo}
        </h1>
        <p
          style={{
            fontFamily: font.sans,
            fontSize:   fontSize.sm,
            fontWeight: fontWeight.regular,
            color:      fg.muted,
            margin:     0,
            marginTop:  space[2],
            textTransform: "capitalize",
          }}
        >
          {periodo}
        </p>
      </div>

      {/* Datos de cuenta */}
      <div
        style={{
          display:     "flex",
          flexDirection: "column",
          gap:         space[4],
          borderLeft:  `1px solid ${border.default}`,
          paddingLeft: space[8],
          minWidth:    160,
        }}
      >
        {datos.map(({ label, valor }) => (
          <div key={label}>
            <p
              style={{
                fontFamily:    font.sans,
                fontSize:      fontSize.xs,
                fontWeight:    fontWeight.medium,
                color:         fg.secondary,
                letterSpacing: "0.05em",
                margin:        0,
                marginBottom:  2,
                textTransform: "uppercase",
              }}
            >
              {label}
            </p>
            <p
              style={{
                fontFamily: font.mono,
                fontSize:   fontSize.base,
                fontWeight: fontWeight.medium,
                color:      fg.primary,
                margin:     0,
              }}
            >
              {valor}
            </p>
          </div>
        ))}
      </div>
    </header>
  );
}
