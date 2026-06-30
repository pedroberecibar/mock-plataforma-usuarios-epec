import type { DocumentoPago, FacturaDatosResponse } from "../api/types";
import { fixture } from "./_fixtures";

export async function fetchLinkFactura(
  _token: string,
  _numeroCliente: string,
  _numeroContrato: string
): Promise<string> {
  throw new Error("No disponible en modo demo");
}

export async function fetchFacturaDatos(_token: string): Promise<FacturaDatosResponse> {
  return fixture<FacturaDatosResponse>("factura");
}

export async function fetchDocumentosFactura(
  _token: string,
  _numeroCliente: string,
  _numeroContrato: string
): Promise<DocumentoPago[]> {
  // Sin pasarela de pago en la demo — lista vacía de documentos.
  return [];
}

export async function evaluarVencimiento(_token: string): Promise<void> {
  // no-op en modo demo
}
