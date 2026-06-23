import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { SectionTitle } from "./SectionTitle";

describe("SectionTitle", () => {
  it("renderiza el texto como h3", () => {
    render(<SectionTitle>Consumo diario</SectionTitle>);
    expect(screen.getByRole("heading", { level: 3 })).toBeDefined();
    expect(screen.getByText("Consumo diario")).toBeDefined();
  });

  it("acepta children como ReactNode", () => {
    render(
      <SectionTitle>
        Comparación <strong>histórica</strong>
      </SectionTitle>
    );
    expect(screen.getByText("histórica")).toBeDefined();
  });
});
