import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { AppShell } from "./AppShell";

const NAV_LABELS = ["Inicio", "Consumo", "Objetivos", "Mi factura", "Alertas"];
const VISTA_TITLES: Array<{ vista: Parameters<typeof AppShell>[0]["vistaActiva"]; title: string }> = [
  { vista: "home",      title: "Inicio" },
  { vista: "consumo",   title: "Mi Consumo" },
  { vista: "objetivos", title: "Objetivos" },
  { vista: "factura",   title: "Mi Factura" },
  { vista: "alertas",   title: "Alertas" },
];

describe("AppShell", () => {
  it("renderiza el logo con alt=EPEC", () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()} onLogout={vi.fn()}>
        <div>contenido</div>
      </AppShell>,
    );
    expect(screen.getByAltText("EPEC")).toBeTruthy();
  });

  it("renderiza los 5 items de navegación por su label", () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()} onLogout={vi.fn()}>
        <div>contenido</div>
      </AppShell>,
    );
    for (const label of NAV_LABELS) {
      expect(screen.getAllByText(label).length).toBeGreaterThan(0);
    }
  });

  it('"Inicio" tiene aria-current="page" por defecto', () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()} onLogout={vi.fn()}>
        <div />
      </AppShell>,
    );
    const activeItems = screen.getAllByRole("link", { current: "page" });
    expect(activeItems.some((el) => el.textContent?.includes("Inicio"))).toBe(true);
  });

  it('click en "Consumo" llama onNavegar con "consumo"', async () => {
    const onNavegar = vi.fn();
    render(
      <AppShell vistaActiva="home" onNavegar={onNavegar} onLogout={vi.fn()}>
        <div />
      </AppShell>,
    );
    const consumoLinks = screen.getAllByRole("link", { name: /consumo/i });
    const enabled = consumoLinks.find((el) => !el.getAttribute("aria-disabled"));
    await userEvent.click(enabled!);
    expect(onNavegar).toHaveBeenCalledWith("consumo");
  });

  it('click en "Objetivos" llama onNavegar con "objetivos"', async () => {
    const onNavegar = vi.fn();
    render(
      <AppShell vistaActiva="home" onNavegar={onNavegar} onLogout={vi.fn()}>
        <div />
      </AppShell>,
    );
    const links = screen.getAllByRole("link", { name: /objetivos/i });
    const enabled = links.find((el) => !el.getAttribute("aria-disabled"));
    await userEvent.click(enabled!);
    expect(onNavegar).toHaveBeenCalledWith("objetivos");
  });

  it("muestra el nombre del usuario cuando se pasa usuarioNombre", () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()} onLogout={vi.fn()} usuarioNombre="Pedro Berecibar">
        <div />
      </AppShell>,
    );
    expect(screen.getByText("Pedro Berecibar")).toBeTruthy();
  });

  it('muestra fallback "Mi cuenta" cuando no se pasa usuarioNombre', () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()} onLogout={vi.fn()}>
        <div />
      </AppShell>,
    );
    expect(screen.getAllByText("Mi cuenta").length).toBeGreaterThan(0);
  });

  it("renderiza los children en el área de contenido", () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()} onLogout={vi.fn()}>
        <div data-testid="contenido-hijo">hijo</div>
      </AppShell>,
    );
    expect(screen.getByTestId("contenido-hijo")).toBeTruthy();
  });

  it("renderiza el top bar móvil con data-testid", () => {
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()} onLogout={vi.fn()}>
        <div />
      </AppShell>,
    );
    expect(screen.getByTestId("mobile-topbar")).toBeDefined();
  });

  it.each(VISTA_TITLES)(
    "top bar muestra el título '$title' cuando vistaActiva='$vista'",
    ({ vista, title }) => {
      render(
        <AppShell vistaActiva={vista} onNavegar={vi.fn()} onLogout={vi.fn()}>
          <div />
        </AppShell>,
      );
      expect(screen.getByTestId("mobile-topbar").textContent).toContain(title);
    },
  );

  it('click en "Cerrar sesión" llama onLogout', async () => {
    const onLogout = vi.fn();
    render(
      <AppShell vistaActiva="home" onNavegar={vi.fn()} onLogout={onLogout}>
        <div />
      </AppShell>,
    );
    const logoutBtn = screen.getByRole("button", { name: /cerrar sesión/i });
    await userEvent.click(logoutBtn);
    expect(onLogout).toHaveBeenCalledTimes(1);
  });
});
