import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { EmptyState } from "./EmptyState";

describe("EmptyState", () => {
  it("muestra el título", () => {
    render(<EmptyState title="Sin datos disponibles" />);
    expect(screen.getByText("Sin datos disponibles")).toBeDefined();
  });

  it("muestra la descripción cuando se provee", () => {
    render(
      <EmptyState title="Sin datos" description="No hay consumo registrado para este período." />
    );
    expect(screen.getByText("No hay consumo registrado para este período.")).toBeDefined();
  });

  it("no muestra botón CTA cuando no se provee", () => {
    const { container } = render(<EmptyState title="Sin datos" />);
    expect(container.querySelectorAll("button").length).toBe(0);
  });

  it("muestra y llama al CTA cuando se provee", async () => {
    const handleClick = vi.fn();
    render(
      <EmptyState title="Sin datos" ctaLabel="Reintentar" onCta={handleClick} />
    );
    await userEvent.click(screen.getByRole("button", { name: "Reintentar" }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("tiene role=status para lectores de pantalla", () => {
    render(<EmptyState title="Sin datos" />);
    expect(screen.getByRole("status")).toBeDefined();
  });
});
