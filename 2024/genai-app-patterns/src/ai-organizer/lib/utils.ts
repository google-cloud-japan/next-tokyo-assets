import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

import { MAX_FILE_SIZE } from '@/lib/constants';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const isAcceptableFileType = (type: string): boolean => {
  return Object.keys(MAX_FILE_SIZE).includes(type);
};
