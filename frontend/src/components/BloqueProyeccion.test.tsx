import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { BloqueProyeccion } from "./BloqueProyeccion";
import type { ProyeccionResponse } from "../api/types";

const insuficiente: ProyeccionResponse = {
  mes: "2026-06-01",
  metodo_aplicado: "insuficiente",
  bandera_confianza: "sin_datos",
  rango_inferior_kwh: null,
  rango_superior_kwh: null,
};

const reciente: ProyeccionResponse = {
  mes: "2026-06-01",
  metodo_aplicado: "reciente",
  bandera_confianza: "baja",
  rango_inferior_kwh: 80.0,
  rango_superior_kwh: 120.0,
};

const interanual: ProyeccionResponse = {
  mes: "2026-06-01",
  metodo_aplicado: "interanual",
  bandera_confianza: "alta",
  rango_inferior_kwh: 270.0,
  rango_superior_kwh: 330.0,
};

describe("BloqueProyeccion", () => {
  it("muestra mensaje de datos insuficientes cuando metodo es insuficiente", () => {
    render(<BloqueProyeccion proyeccion={insuficiente} />);
    expect(screen.getByText(/Datos insuficientes para proyectar/)).not.toBeNull();
  });

  it("no muestra rango cuando metodo es insuficiente", () => {
    render(<BloqueProyeccion proyeccion={insuficiente} />);
    expect(screen.queryByText(/kWh/)).toBeNull();
  });

  it("muestra el rango inferior y superior para metodo reciente", () => {
    render(<BloqueProyeccion proyeccion={reciente} />);
    expect(screen.getByText(/80/)).not.toBeNull();
    expect(screen.getByText(/120/)).not.toBeNull();
  });

  it("muestra la etiqueta de confianza alta para interanual", () => {
    render(<BloqueProyeccion proyeccion={interanual} />);
    expect(screen.getByText("Alta confianza")).not.toBeNull();
  });

  it("muestra la etiqueta de confianza baja para reciente", () => {
    render(<BloqueProyeccion proyeccion={reciente} />);
    expect(screen.getByText("Baja confianza")).not.toBeNull();
  });

  it("muestra el texto de ajuste progresivo", () => {
    render(<BloqueProyeccion proyeccion={interanual} />);
    expect(screen.getByText(/Se ajusta a medida que avanza el mes/)).not.toBeNull();
  });

  it("tiene aria-label de sección", () => {
    render(<BloqueProyeccion proyeccion={insuficiente} />);
    expect(screen.getByRole("region", { name: "proyección mensual" })).not.toBeNull();
  });
});
