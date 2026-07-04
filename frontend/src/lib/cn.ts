/**
 * Class name utility — combines clsx + tailwind-merge.
 * Standard shadcn/ui pattern. Use for conditional Tailwind classes.
 */

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
