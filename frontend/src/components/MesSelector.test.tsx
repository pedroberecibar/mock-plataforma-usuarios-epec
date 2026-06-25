import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MesSelector } from "./MesSelector";

const MESES = [
  { value: "2026-06", label: "Junio de 2026" },
  { value: "2026-05", label: "Mayo de 2026" },
  { value: "2026-04", label: "Abril de 2026" },
];

describe("MesSelector", () => {
  it("renderiza una opción por cada mes", () => {
    render(<MesSelector value="2026-06" meses={MESES} onChange={() => {}} />);
    const opciones = screen.getAllByRole("option");
    expect(opciones).toHaveLength(3);
    expect(screen.getByRole("option", { name: "Mayo de 2026" })).not.toBeNull();
  });

  it("refleja el mes seleccionado", () => {
    render(<MesSelector value="2026-05" meses={MESES} onChange={() => {}} />);
    const select = screen.getByRole("combobox") as HTMLSelectElement;
    expect(select.value).toBe("2026-05");
  });

  it("dispara onChange con el value del mes elegido", () => {
    const onChange = vi.fn();
    render(<MesSelector value="2026-06" meses={MESES} onChange={onChange} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "2026-04" } });
    expect(onChange).toHaveBeenCalledWith("2026-04");
  });
});
