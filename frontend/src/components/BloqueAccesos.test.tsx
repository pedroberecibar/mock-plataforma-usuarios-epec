import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BloqueAccesos } from "./BloqueAccesos";
import type { Vista } from "./AppShell";

describe("BloqueAccesos", () => {
  it("muestra los 4 accesos rápidos", () => {
    render(<BloqueAccesos suministroId="S001" />);
    expect(screen.getByText(/consumo/i)).toBeDefined();
    expect(screen.getByText(/factura/i)).toBeDefined();
    expect(screen.getByText(/objetivos/i)).toBeDefined();
    expect(screen.getByText(/alertas/i)).toBeDefined();
  });

  it("llama onNavegar con la vista correcta al hacer click en cada acceso", async () => {
    const onNavegar = vi.fn();
    render(<BloqueAccesos suministroId="S001" onNavegar={onNavegar} />);

    await userEvent.click(screen.getByRole("button", { name: /consumo/i }));
    expect(onNavegar).toHaveBeenCalledWith("consumo");

    await userEvent.click(screen.getByRole("button", { name: /factura/i }));
    expect(onNavegar).toHaveBeenCalledWith("factura");

    await userEvent.click(screen.getByRole("button", { name: /objetivos/i }));
    expect(onNavegar).toHaveBeenCalledWith("objetivos");

    await userEvent.click(screen.getByRole("button", { name: /alertas/i }));
    expect(onNavegar).toHaveBeenCalledWith("alertas");
  });

  it("renderiza sin onNavegar sin errores", () => {
    render(<BloqueAccesos suministroId="S001" />);
    expect(screen.getByRole("region", { name: "accesos rápidos" })).toBeDefined();
  });
});

// type check — onNavegar acepta Vista
const _: (v: Vista) => void = vi.fn();
