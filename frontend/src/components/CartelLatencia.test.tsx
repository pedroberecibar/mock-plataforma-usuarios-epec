import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { CartelLatencia } from "./CartelLatencia";

describe("CartelLatencia", () => {
  it("no renderiza nada cuando datosHasta es null", () => {
    const { container } = render(<CartelLatencia datosHasta={null} />);
    expect(container.firstChild).toBeNull();
  });

  it("muestra el banner con la fecha formateada cuando datosHasta tiene valor", () => {
    render(<CartelLatencia datosHasta="2026-06-15" />);
    const banner = screen.getByRole("status");
    expect(banner).not.toBeNull();
    expect(banner.textContent).toContain("15");
    expect(banner.textContent).toContain("junio");
    expect(banner.textContent).toContain("2026");
  });

  it("tiene aria-label de latencia de datos", () => {
    render(<CartelLatencia datosHasta="2026-06-01" />);
    expect(screen.getByLabelText("latencia de datos")).not.toBeNull();
  });
});
