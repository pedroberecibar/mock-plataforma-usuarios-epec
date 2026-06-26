import type { CuentaResponse } from "../api/types";
import { fixture } from "./_fixtures";

export async function fetchCuenta(_token: string): Promise<CuentaResponse> {
  return fixture<CuentaResponse>("cuenta");
}
