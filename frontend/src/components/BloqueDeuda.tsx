import type { CSSProperties } from "react";
import type { FacturaDatosResponse } from "../api/types";
import type { Vista } from "./AppShell";
import {
  diasHastaVencimiento,
  formatImporte,
  proximoVencimiento,
  textoDiasRestantes,
} from "../utils/factura";
import {
  cardStyle,
  color,
  fg,
  font,
  fontSize,
  fontWeight,
  labelStyle,
  lineHeight,
  radius,
  space,
} from "../design-tokens";

interface Props {
  datos: FacturaDatosResponse | null;
  onNavegar?: (vista: Vista) => void;
}

function chipColors(dias: number): { bg: string; text: string } {
  if (dias < 0) return { bg: color.errorLight, text: color.errorDark };
  if (dias <= 5) return { bg: color.warningLight, text: color.warningDark };
  return { bg: color.green100, text: color.successDark };
}

export function BloqueDeuda({ datos, onNavegar }: Props) {
  // Datos aún no cargados: estado neutro, sin afirmar "al día" prematuramente.
  if (datos == null) {
    return (
      <section aria-label="deuda" style={cardStyle}>
        <p style={labelStyle}>Deuda total</p>
        <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.md, color: fg.muted }}>—</p>
      </section>
    );
  }

  const documentos = datos.documentos;
  const hayDeuda = documentos.length > 0;

  if (!hayDeuda) {
    return (
      <section aria-label="deuda" style={cardStyle}>
        <p style={labelStyle}>Deuda total</p>
        <p style={{
          margin:     `${space[2]}px 0 ${space[1]}px`,
          fontFamily: font.technical,
          fontSize:   fontSize["2xl"],
          fontWeight: fontWeight.light,
          color:      color.successDark,
          lineHeight: lineHeight.snug,
        }}>
          Estás al día
        </p>
        <p style={{ margin: 0, fontSize: fontSize.sm, color: fg.secondary }}>
          No tenés facturas pendientes de pago.
        </p>
        <div style={{ marginTop: space[4] }}>
          <button onClick={() => onNavegar?.("factura")} style={linkStyle}>
            Ver mis facturas →
          </button>
        </div>
      </section>
    );
  }

  const proximo = proximoVencimiento(documentos);
  const dias = proximo?.fecha_vencimiento ? diasHastaVencimiento(proximo.fecha_vencimiento) : null;
  const chip = dias != null ? chipColors(dias) : null;

  return (
    <section aria-label="deuda" style={cardStyle}>
      <p style={labelStyle}>Deuda total</p>
      <p style={{
        margin:        `${space[2]}px 0 ${space[1]}px`,
        fontFamily:    font.technical,
        fontSize:      fontSize["2xl"],
        fontWeight:    fontWeight.light,
        color:         fg.primary,
        lineHeight:    lineHeight.snug,
        letterSpacing: "-0.02em",
      }}>
        {formatImporte(datos.total_deuda)}
      </p>
      <p style={{ margin: 0, fontSize: fontSize.sm, color: fg.secondary }}>
        {documentos.length === 1 ? "1 factura pendiente" : `${documentos.length} facturas pendientes`}
      </p>

      {dias != null && chip && (
        <span style={{
          display:      "inline-block",
          marginTop:    space[3],
          padding:      `${space[1]}px ${space[3]}px`,
          borderRadius: radius.full,
          background:   chip.bg,
          color:        chip.text,
          fontSize:     fontSize.xs,
          fontWeight:   fontWeight.semibold,
        }}>
          {textoDiasRestantes(dias)}
        </span>
      )}

      <div style={{ marginTop: space[4] }}>
        <button onClick={() => onNavegar?.("factura")} style={linkStyle}>
          Ver factura →
        </button>
      </div>
    </section>
  );
}

const linkStyle: CSSProperties = {
  background:  "none",
  border:      "none",
  padding:     0,
  color:       fg.link,
  fontFamily:  font.sans,
  fontSize:    fontSize.sm,
  fontWeight:  fontWeight.semibold,
  cursor:      "pointer",
};
