'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { HOME_ROUTE, ROOT_ROUTE, SESSION_COOKIE_NAME } from '@/lib/constants';

export const createSession = async (uid: string) => {
  cookies().set(SESSION_COOKIE_NAME, uid, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 60 * 60 * 24, // One day
    path: '/'
  });

  redirect(HOME_ROUTE);
};

export const removeSession = async () => {
  cookies().delete(SESSION_COOKIE_NAME);

  redirect(ROOT_ROUTE);
};
