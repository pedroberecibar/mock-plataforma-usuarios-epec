import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { AppShell } from "./AppShell";

const NAV_LABELS = ["Inicio", "Consumo", "Objetivos", "Mi factura", "Configuración"];

describe("AppShell", () => {
  it("renderiza el logo con alt=EPEC", () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()}>
        <div>contenido</div>
      </AppShell>,
    );
    expect(screen.getByAltText("EPEC")).toBeTruthy();
  });

  it("renderiza los 5 items de navegación por su label", () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()}>
        <div>contenido</div>
      </AppShell>,
    );
    for (const label of NAV_LABELS) {
      expect(screen.getAllByText(label).length).toBeGreaterThan(0);
    }
  });

  it('"Inicio" tiene aria-current="page" por defecto', () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()}>
        <div />
      </AppShell>,
    );
    const activeItems = screen.getAllByRole("link", { current: "page" });
    expect(activeItems.some((el) => el.textContent?.includes("Inicio"))).toBe(true);
  });

  it('click en "Consumo" llama onNavegar con "consumo"', async () => {
    const onNavegar = vi.fn();
    render(
      <AppShell vistaActiva="home" onNavegar={onNavegar}>
        <div />
      </AppShell>,
    );
    const consumoLinks = screen.getAllByRole("link", { name: /consumo/i });
    const enabled = consumoLinks.find((el) => !el.getAttribute("aria-disabled"));
    await userEvent.click(enabled!);
    expect(onNavegar).toHaveBeenCalledWith("consumo");
  });

  it('items "Objetivos", "Mi factura" y "Configuración" tienen aria-disabled y no llaman onNavegar', () => {
    const onNavegar = vi.fn();
    render(
      <AppShell vistaActiva="home" onNavegar={onNavegar}>
        <div />
      </AppShell>,
    );
    for (const label of ["Objetivos", "Mi factura", "Configuración"]) {
      const items = screen.getAllByText(label);
      for (const item of items) {
        // Verify disabled attribute is set
        const link = item.closest("a");
        expect(link?.getAttribute("aria-disabled")).toBe("true");
        // fireEvent bypasses pointer-events:none — should still not trigger navigation
        fireEvent.click(item);
      }
    }
    expect(onNavegar).not.toHaveBeenCalled();
  });

  it("muestra el nombre del usuario cuando se pasa usuarioNombre", () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()} usuarioNombre="Pedro Berecibar">
        <div />
      </AppShell>,
    );
    expect(screen.getByText("Pedro Berecibar")).toBeTruthy();
  });

  it('muestra fallback "Mi cuenta" cuando no se pasa usuarioNombre', () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()}>
        <div />
      </AppShell>,
    );
    expect(screen.getAllByText("Mi cuenta").length).toBeGreaterThan(0);
  });

  it("renderiza los children en el área de contenido", () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()}>
        <div data-testid="contenido-hijo">hijo</div>
      </AppShell>,
    );
    expect(screen.getByTestId("contenido-hijo")).toBeTruthy();
  });
});
