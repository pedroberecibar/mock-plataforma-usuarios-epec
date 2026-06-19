import type { LucideIcon } from "lucide-react";

interface IconProps {
  icon: LucideIcon;
  size?: number;
  className?: string;
  color?: string;
}

export function Icon({ icon: IconComponent, size = 20, className, color }: IconProps) {
  return <IconComponent size={size} strokeWidth={1.5} className={className} color={color} />;
}
