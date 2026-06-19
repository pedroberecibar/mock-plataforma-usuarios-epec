import type { HomeResponse } from "../api/types";
import { fixture } from "./_fixtures";

export async function fetchHome(
  _token: string,
  _mes: string
): Promise<HomeResponse> {
  return fixture<HomeResponse>("home");
}
