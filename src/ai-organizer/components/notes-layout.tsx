'use client';

import { useAtom } from 'jotai';
import { useParams } from 'next/navigation';
import { useEffect } from 'react';

import NoteCard from '@/components/note-card';
import { getNotesSnapshot } from '@/lib/firebase/firestore';
import { useUserId } from '@/lib/hooks/auth';
import { notesAtom } from '@/lib/state';

const NotesLayout = () => {
  const [notes, setNotes] = useAtom(notesAtom);
  const { slug: notebookId } = useParams();
  const uid = useUserId();

  useEffect(() => {
    if (!uid || !notebookId) return;
    const unsubscribe = getNotesSnapshot(uid, notebookId as string, (data) => {
      setNotes(data);
    });

    return () => {
      unsubscribe();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uid, notebookId]);

  return (
    <div className="absolute box-border flex size-full grow overflow-y-auto px-4">
      <div className="size-full">
        <div className="flex flex-wrap pb-[240px]">
          {notes.map((note) => (
            <NoteCard
              key={note.id}
              id={note.id}
              content={note.content}
              createdAt={note.createdAt}
              status={note.status}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default NotesLayout;
