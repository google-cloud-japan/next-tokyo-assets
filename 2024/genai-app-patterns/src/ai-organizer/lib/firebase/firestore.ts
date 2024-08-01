import {
  addDoc,
  collection,
  deleteDoc,
  doc,
  getDoc,
  getDocs,
  getFirestore,
  increment,
  onSnapshot,
  orderBy,
  query,
  runTransaction,
  serverTimestamp,
  setDoc,
  Timestamp,
  updateDoc,
  where
} from 'firebase/firestore';

import { db } from '@/lib/firebase/client-app';

export type Source = {
  id: string;
  name: string;
  selected: boolean;
  type: string;
  storagePath: string;
  ragFileId: string;
  status: 'creating' | 'created' | 'deleting' | 'error';
  downloadURL: string;
  summarization: string | null;
  questions: string[] | null;
  createdAt: Timestamp;
  updatedAt: Timestamp;
};

type GetSourcesSnapshotCallback = (sources: Source[]) => void;

export const getSourcesSnapshot = (uid: string, notebookId: string, cb: GetSourcesSnapshotCallback) => {
  const q = query(collection(db, 'users', uid, 'notebooks', notebookId, 'sources'), orderBy('createdAt', 'desc'));

  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    const sources = querySnapshot.docs.map(
      (doc) =>
        ({
          id: doc.id,
          ...doc.data()
        }) as Source
    );
    cb(sources);
  });

  return unsubscribe;
};

export const toggleSourceSelected = async (uid: string, notebookId: string, id: string, selected: boolean) => {
  const sourceRef = doc(collection(db, 'users', uid, 'notebooks', notebookId, 'sources'), id);
  if (sourceRef) {
    await updateDoc(sourceRef, {
      selected: selected
    });
  }
};

export const addSource = async (
  id: string,
  uid: string,
  type: string,
  storagePath: string,
  notebookId: string,
  name: string,
  downloadURL: string
) => {
  await setDoc(doc(db, 'users', uid, 'notebooks', notebookId, 'sources', id), {
    name: name,
    selected: false,
    type: type,
    storagePath: storagePath,
    ragFileId: null,
    status: 'creating',
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
    downloadURL: downloadURL,
    summarization: null,
    questions: null
  });
  await updateDoc(doc(db, 'users', uid, 'notebooks', notebookId), {
    sourceCount: increment(1)
  });
};

export const deleteSource = async (id: string, uid: string, notebookId: string) => {
  await updateDoc(doc(db, 'users', uid, 'notebooks', notebookId, 'sources', id), {
    status: 'deleting'
  });
};

export const updateSourceName = async (id: string, uid: string, notebookId: string, name: string) => {
  await updateDoc(doc(db, 'users', uid, 'notebooks', notebookId, 'sources', id), {
    name: name
  });
};

export type Message = {
  id: string;
  content: string;
  loading: boolean;
  ragFileIds: string[];
  role: 'user' | 'model';
  status: 'success' | 'failed';
  createdAt: Timestamp;
};

type GetChatHistorySnapshotCallback = (messages: Message[]) => void;

export const getChatHistorySnapshot = (uid: string, notebookId: string, cb: GetChatHistorySnapshotCallback) => {
  const q = query(collection(db, 'users', uid, 'notebooks', notebookId, 'chat'), orderBy('createdAt'));

  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    const messages = querySnapshot.docs.map(
      (doc) =>
        ({
          id: doc.id,
          ...doc.data()
        }) as Message
    );
    cb(messages);
  });

  return unsubscribe;
};

export const deleteChatHistory = async (uid: string, notebookId: string) => {
  const q = await getDocs(collection(db, 'users', uid, 'notebooks', notebookId, 'chat'));
  for (const doc of q.docs) {
    await deleteDoc(doc.ref);
  }
};

export const sendChatMessage = async (uid: string, notebookId: string, content: string, ragFileIds: string[]) => {
  await addDoc(collection(db, 'users', uid, 'notebooks', notebookId, 'chat'), {
    content: content,
    loading: false,
    ragFileIds: ragFileIds,
    role: 'user',
    status: 'success',
    createdAt: serverTimestamp()
  });
};

export type Note = {
  id: string;
  content: string;
  status: 'created' | 'creating';
  createdAt: Timestamp;
};

type GetNotesSnapshotCallback = (messages: Note[]) => void;

export const getNotesSnapshot = (uid: string, notebookId: string, cb: GetNotesSnapshotCallback) => {
  const q = query(collection(db, 'users', uid, 'notebooks', notebookId, 'notes'), orderBy('createdAt', 'desc'));

  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    const notes = querySnapshot.docs.map(
      (doc) =>
        ({
          id: doc.id,
          ...doc.data()
        }) as Note
    );
    cb(notes);
  });

  return unsubscribe;
};

export const addNote = async (uid: string, notebookId: string, content: string) => {
  await addDoc(collection(db, 'users', uid, 'notebooks', notebookId, 'notes'), {
    content: content,
    status: 'created',
    createdAt: serverTimestamp()
  });
};

export type Notebook = {
  id: string;
  title: string;
  createdAt: Timestamp;
  sourceCount: number;
};

type GetNotebooksSnapshotCallback = (notebooks: Notebook[]) => void;

export const getNotebooksSnapshot = (uid: string, cb: GetNotebooksSnapshotCallback) => {
  const q = query(collection(db, 'users', uid, 'notebooks'), orderBy('createdAt', 'desc'));

  const unsubscribe = onSnapshot(q, (querySnapshot) => {
    const notebooks = querySnapshot.docs.map(
      (doc) =>
        ({
          id: doc.id,
          ...doc.data()
        }) as Notebook
    );
    cb(notebooks);
  });

  return unsubscribe;
};

export const addNotebook = async (uid: string, title: string): Promise<string> => {
  const docRef = await addDoc(collection(db, 'users', uid, 'notebooks'), {
    title: title,
    sourceCount: 0,
    createdAt: serverTimestamp()
  });
  return docRef.id;
};

export const getNotebook = async (uid: string, notebookId: string): Promise<Notebook> => {
  const docRef = await getDoc(doc(db, 'users', uid, 'notebooks', notebookId));
  return {
    id: docRef.id,
    ...docRef.data()
  } as Notebook;
};

export const updateNotebookTitle = async (uid: string, notebookId: string, title: string) => {
  await updateDoc(doc(db, 'users', uid, 'notebooks', notebookId), {
    title: title
  });
};

export type User = {
  id: string;
  email: string;
  createdAt: Timestamp;
  status: 'creating' | 'created';
  corpusName: string;
};

type GetUserSnapshotCallback = (user: User) => void;

export const getUserSnapshot = (uid: string, cb: GetUserSnapshotCallback) => {
  const q = doc(db, 'users', uid);
  const unsubscribe = onSnapshot(q, (doc) => {
    const user = {
      id: doc.id,
      ...doc.data()
    } as User;
    cb(user);
  });

  return unsubscribe;
};

export const addUser = async (uid: string, email: string): Promise<void> => {
  try {
    await setDoc(doc(db, 'users', uid), {
      email: email,
      createdAt: serverTimestamp(),
      status: 'creating'
    });
  } catch (error) {
    console.error('Error adding document: ', error);
  }
};

export const getUserByUid = async (uid: string): Promise<User> => {
  const docRef = await getDoc(doc(db, 'users', uid));
  return {
    id: docRef.id,
    ...docRef.data()
  } as User;
};
