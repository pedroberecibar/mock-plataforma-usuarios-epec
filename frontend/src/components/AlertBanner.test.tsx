import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { AlertBanner } from "./AlertBanner";

describe("AlertBanner", () => {
  it("muestra el contenido del mensaje", () => {
    render(<AlertBanner variant="warning">Tu factura vence mañana.</AlertBanner>);
    expect(screen.getByText("Tu factura vence mañana.")).toBeDefined();
  });

  it("tiene role=alert", () => {
    render(<AlertBanner variant="error">Error crítico.</AlertBanner>);
    expect(screen.getByRole("alert")).toBeDefined();
  });

  it("renderiza variante warning", () => {
    const { container } = render(
      <AlertBanner variant="warning">Aviso</AlertBanner>
    );
    const el = container.firstChild as HTMLElement;
    expect(el.style.borderLeft).toContain("3px");
  });

  it("renderiza variante error", () => {
    const { container } = render(
      <AlertBanner variant="error">Error</AlertBanner>
    );
    const el = container.firstChild as HTMLElement;
    expect(el.style.borderLeft).toContain("3px");
  });

  it("renderiza variante info", () => {
    const { container } = render(
      <AlertBanner variant="info">Información</AlertBanner>
    );
    const el = container.firstChild as HTMLElement;
    expect(el.style.borderLeft).toContain("3px");
  });

  it("renderiza variante success", () => {
    const { container } = render(
      <AlertBanner variant="success">Objetivo cumplido.</AlertBanner>
    );
    const el = container.firstChild as HTMLElement;
    expect(el.style.borderLeft).toContain("3px");
  });
});
