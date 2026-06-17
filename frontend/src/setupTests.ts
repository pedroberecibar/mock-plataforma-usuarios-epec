import { vi } from "vitest";

// Recharts' ResponsiveContainer uses ResizeObserver which jsdom doesn't implement
vi.stubGlobal(
  "ResizeObserver",
  class {
    observe() {}
    unobserve() {}
    disconnect() {}
  },
);
