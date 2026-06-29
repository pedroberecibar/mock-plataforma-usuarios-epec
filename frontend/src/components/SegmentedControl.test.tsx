import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SegmentedControl } from "./SegmentedControl";

const OPCIONES = [
  { value: "dia", label: "Por día" },
  { value: "mes", label: "Por mes" },
];

describe("SegmentedControl", () => {
  it("renderiza un botón por opción", () => {
    render(<SegmentedControl ariaLabel="Modo" value="dia" opciones={OPCIONES} onChange={() => {}} />);
    expect(screen.getByRole("button", { name: "Por día" })).not.toBeNull();
    expect(screen.getByRole("button", { name: "Por mes" })).not.toBeNull();
  });

  it("marca como activa la opción seleccionada con aria-pressed", () => {
    render(<SegmentedControl ariaLabel="Modo" value="mes" opciones={OPCIONES} onChange={() => {}} />);
    expect(screen.getByRole("button", { name: "Por mes" }).getAttribute("aria-pressed")).toBe("true");
    expect(screen.getByRole("button", { name: "Por día" }).getAttribute("aria-pressed")).toBe("false");
  });

  it("dispara onChange con el value de la opción clickeada", () => {
    const onChange = vi.fn();
    render(<SegmentedControl ariaLabel="Modo" value="dia" opciones={OPCIONES} onChange={onChange} />);
    fireEvent.click(screen.getByRole("button", { name: "Por mes" }));
    expect(onChange).toHaveBeenCalledWith("mes");
  });

  it("no dispara onChange al clickear la opción ya activa", () => {
    const onChange = vi.fn();
    render(<SegmentedControl ariaLabel="Modo" value="dia" opciones={OPCIONES} onChange={onChange} />);
    fireEvent.click(screen.getByRole("button", { name: "Por día" }));
    expect(onChange).not.toHaveBeenCalled();
  });
});
