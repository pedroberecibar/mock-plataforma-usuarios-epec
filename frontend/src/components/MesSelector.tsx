import type { MesOpcion } from "../utils/meses";
import { SelectControl } from "./SelectControl";

interface Props {
  value: string;
  meses: MesOpcion[];
  onChange: (value: string) => void;
}

export function MesSelector({ value, meses, onChange }: Props) {
  return <SelectControl label="Mes" value={value} opciones={meses} onChange={onChange} />;
}
