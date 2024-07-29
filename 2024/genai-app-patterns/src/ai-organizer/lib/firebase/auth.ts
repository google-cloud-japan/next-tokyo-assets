import {
  createUserWithEmailAndPassword as _createUserWithEmailAndPassword,
  onAuthStateChanged as _onAuthStateChanged,
  signInWithEmailAndPassword as _signInWithEmailAndPassword,
  signOut as _signOut,
  type User
} from 'firebase/auth';

import { auth } from '@/lib/firebase/client-app';

export function onAuthStateChanged(callback: (authUser: User | null) => void) {
  return _onAuthStateChanged(auth, callback);
}

export const signInWithEmailAndPassword = async (email: string, password: string): Promise<User> => {
  const userCredential = await _signInWithEmailAndPassword(auth, email, password);
  return userCredential.user;
};

export const createUserWithEmailAndPassword = async (email: string, password: string): Promise<User> => {
  const userCredential = await _createUserWithEmailAndPassword(auth, email, password);
  return userCredential.user;
};

export const signOut = async (): Promise<void> => {
  await _signOut(auth);
};
