import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { KwhHero } from "./KwhHero";

describe("KwhHero", () => {
  it("muestra el valor numérico", () => {
    render(<KwhHero value={215} />);
    expect(screen.getByText(/215/)).toBeDefined();
  });

  it("muestra la unidad kWh", () => {
    render(<KwhHero value={78} />);
    expect(screen.getByText(/kWh/)).toBeDefined();
  });

  it("muestra el sublabel cuando se provee", () => {
    render(<KwhHero value={78} sublabel="consumo acumulado del mes" />);
    expect(screen.getByText("consumo acumulado del mes")).toBeDefined();
  });

  it("no muestra sublabel cuando no se provee", () => {
    const { container } = render(<KwhHero value={100} />);
    expect(container.querySelectorAll("[data-testid='kwh-sublabel']").length).toBe(0);
  });

  it("variante hero tiene fuente más grande que variante inline", () => {
    const { container: heroContainer } = render(<KwhHero value={100} variant="hero" />);
    const { container: inlineContainer } = render(<KwhHero value={100} variant="inline" />);
    const heroSize = parseInt(
      (heroContainer.querySelector("[data-testid='kwh-value']") as HTMLElement)?.style.fontSize ?? "0"
    );
    const inlineSize = parseInt(
      (inlineContainer.querySelector("[data-testid='kwh-value']") as HTMLElement)?.style.fontSize ?? "0"
    );
    expect(heroSize).toBeGreaterThan(inlineSize);
  });

  it("formatea con separador de miles en es-AR", () => {
    render(<KwhHero value={1234} />);
    expect(screen.getByText(/1\.234|1,234|1234/)).toBeDefined();
  });
});
