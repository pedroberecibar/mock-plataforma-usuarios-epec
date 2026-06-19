export interface AlertaConfigItem {
  tipo: string;
  habilitado: boolean;
}

export async function fetchAlertasConfig(_token: string): Promise<AlertaConfigItem[]> {
  return [
    { tipo: "consumo_objetivo", habilitado: true },
    { tipo: "vencimiento_factura", habilitado: false },
  ];
}

export async function patchAlertaConfig(
  _token: string,
  tipo: string,
  habilitado: boolean
): Promise<AlertaConfigItem> {
  return { tipo, habilitado };
}
