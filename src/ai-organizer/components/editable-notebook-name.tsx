'use client';

import { useParams } from 'next/navigation';
import { FormEvent, useEffect, useRef, useState } from 'react';

import { getNotebook, updateNotebookTitle } from '@/lib/firebase/firestore';
import { useUserId } from '@/lib/hooks/auth';

const EditableNotebookName = () => {
  const [title, setTitle] = useState('');
  const inputTitleRef = useRef<HTMLInputElement>(null);
  const { slug: notebookId } = useParams();
  const uid = useUserId();

  useEffect(() => {
    if (!uid) {
      return;
    }
    (async () => {
      const notebook = await getNotebook(uid, notebookId as string);
      setTitle(notebook.title);
    })();
  }, [uid, notebookId]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await updateNotebookTitle(uid as string, notebookId as string, title);
    inputTitleRef.current?.blur();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        minLength={3}
        maxLength={20}
        required
        ref={inputTitleRef}
        type="text"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
        className="rounded-md border-2 border-[#F7FBFF] bg-[#F7FBFF] p-2 text-xl hover:border-[#005FCC]"
      />
    </form>
  );
};

export default EditableNotebookName;
