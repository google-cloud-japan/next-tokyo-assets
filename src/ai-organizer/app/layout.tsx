import './globals.css';

import { Provider } from 'jotai';
import type { Metadata } from 'next';
import { Inter as FontSans } from 'next/font/google';

import { Toaster } from '@/components/ui/sonner';
import { cn } from '@/lib/utils';

const fontSans = FontSans({
  subsets: ['latin'],
  variable: '--font-sans'
});

export const metadata: Metadata = {
  title: 'AI organizer',
  description: 'Upload own assets and expand your AI'
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={cn('min-h-screen bg-background font-sans antialiased', fontSans.variable)}>
        <Provider>{children}</Provider>
        <Toaster position="top-center" duration={2000} richColors toastOptions={{}} theme="light" />
      </body>
    </html>
  );
}
