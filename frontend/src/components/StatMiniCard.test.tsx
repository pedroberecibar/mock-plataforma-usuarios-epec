import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { StatMiniCard } from "./StatMiniCard";

describe("StatMiniCard", () => {
  it("muestra el label, value y sub", () => {
    render(<StatMiniCard label="Día más alto" value="12,4 kWh" sub="lun 3" />);
    expect(screen.getByText("Día más alto")).toBeDefined();
    expect(screen.getByText("12,4 kWh")).toBeDefined();
    expect(screen.getByText("lun 3")).toBeDefined();
  });

  it("es clickeable cuando se provee onClick", async () => {
    const handleClick = vi.fn();
    render(
      <StatMiniCard label="Día más alto" value="12 kWh" sub="lun 3" onClick={handleClick} />
    );
    await userEvent.click(screen.getByText("Día más alto").closest("div")!);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("no lanza error al clickear sin onClick", async () => {
    render(<StatMiniCard label="Promedio" value="8 kWh" sub="este mes" />);
    await userEvent.click(screen.getByText("Promedio").closest("div")!);
  });
});
