import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PageHeader } from "./PageHeader";

describe("PageHeader", () => {
  it("muestra el título", () => {
    render(<PageHeader title="Mi Consumo" />);
    expect(screen.getByRole("heading", { level: 2 })).toBeDefined();
    expect(screen.getByText("Mi Consumo")).toBeDefined();
  });

  it("renderiza el slot de acciones cuando se provee", () => {
    render(
      <PageHeader
        title="Consumo"
        actions={<button>Exportar CSV</button>}
      />
    );
    expect(screen.getByRole("button", { name: "Exportar CSV" })).toBeDefined();
  });

  it("no renderiza slot de acciones cuando no se provee", () => {
    const { container } = render(<PageHeader title="Inicio" />);
    expect(container.querySelectorAll("button").length).toBe(0);
  });

  it("el header tiene el rol banner", () => {
    render(<PageHeader title="Alertas" />);
    expect(screen.getByRole("banner")).toBeDefined();
  });

  it("llama onClick del botón de acción al hacer click", async () => {
    const handleClick = vi.fn();
    render(
      <PageHeader
        title="Consumo"
        actions={<button onClick={handleClick}>Exportar</button>}
      />
    );
    await userEvent.click(screen.getByRole("button", { name: "Exportar" }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
