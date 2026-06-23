import { describe, expect, it } from "vitest";
import { render } from "@testing-library/react";
import { LoadingSkeleton } from "./LoadingSkeleton";

describe("LoadingSkeleton", () => {
  it("renderiza 1 bloque por defecto", () => {
    const { container } = render(<LoadingSkeleton />);
    expect(container.querySelectorAll("[data-testid='skeleton-block']").length).toBe(1);
  });

  it("renderiza N bloques cuando se especifica count", () => {
    const { container } = render(<LoadingSkeleton count={3} />);
    expect(container.querySelectorAll("[data-testid='skeleton-block']").length).toBe(3);
  });

  it("aplica el aria-label de carga", () => {
    const { container } = render(<LoadingSkeleton />);
    expect(container.querySelector("[aria-label='Cargando']")).toBeDefined();
  });

  it("variante card tiene mayor altura", () => {
    const { container: c1 } = render(<LoadingSkeleton variant="line" />);
    const { container: c2 } = render(<LoadingSkeleton variant="card" />);
    const lineH = parseInt(
      (c1.querySelector("[data-testid='skeleton-block']") as HTMLElement)?.style.height ?? "0"
    );
    const cardH = parseInt(
      (c2.querySelector("[data-testid='skeleton-block']") as HTMLElement)?.style.height ?? "0"
    );
    expect(cardH).toBeGreaterThan(lineH);
  });
});
