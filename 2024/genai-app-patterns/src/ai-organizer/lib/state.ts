// import { User } from 'firebase/auth';
import { atom } from 'jotai';

import { User } from '@/lib/firebase/firestore';
import { Message, Note, Notebook, Source } from '@/lib/firebase/firestore';

const sidebarOpenAtom = atom(true);
const showChatModalAtom = atom(false);
const chatMessagesAtom = atom<Message[]>([]);
const sourcesAtom = atom<Source[]>([]);
const notesAtom = atom<Note[]>([]);
const notebooksAtom = atom<Notebook[]>([]);
const userAtom = atom<User | null>(null);
const messageAtom = atom('');

export {
  chatMessagesAtom,
  messageAtom,
  notebooksAtom,
  notesAtom,
  showChatModalAtom,
  sidebarOpenAtom,
  sourcesAtom,
  userAtom
};
