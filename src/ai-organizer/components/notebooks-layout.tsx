'use client';

import { useAtom, useSetAtom } from 'jotai';
import { useEffect } from 'react';
import BounceLoader from 'react-spinners/BounceLoader';

import NewNotebookCard from '@/components/new-notebook-card';
import NotebookCard from '@/components/notebook-card';
import { getNotebooksSnapshot, getUserSnapshot } from '@/lib/firebase/firestore';
import { useUserId } from '@/lib/hooks/auth';
import { notebooksAtom, notesAtom, sourcesAtom, userAtom } from '@/lib/state';

const NotebooksLayout = () => {
  const [notebooks, setNotebooks] = useAtom(notebooksAtom);

  const setSources = useSetAtom(sourcesAtom);
  const setNotes = useSetAtom(notesAtom);
  const [user, setUser] = useAtom(userAtom);

  const resetState = () => {
    setSources([]);
    setNotes([]);
  };

  const uid = useUserId();

  useEffect(() => {
    if (!uid) return;

    const unsubscribeNotebooks = getNotebooksSnapshot(uid, (data) => {
      setNotebooks(data);
    });

    const unsubsribeUser = getUserSnapshot(uid, (data) => {
      setUser(data);
    });

    resetState();

    return () => {
      unsubscribeNotebooks();
      unsubsribeUser();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uid]);

  return (
    <div className="max-w-screen-lg px-4 pb-4 pt-12">
      {user?.status === 'creating' ? (
        <div className="flex flex-col items-center justify-center">
          <p className="pt-20 text-2xl">ユーザーを初期化中です。少しお待ち下さい。</p>
          <BounceLoader size={120} color="#666666" className="mt-20" />
        </div>
      ) : (
        <>
          <p className="my-8 h-8 text-2xl">ノートブック</p>
          <div className="flex flex-wrap gap-8">
            <NewNotebookCard />
            {notebooks.map((notebook) => {
              const { id, title, sourceCount, createdAt } = notebook;
              return <NotebookCard key={notebook.id} id={id} title={title} count={sourceCount} createdAt={createdAt} />;
            })}
          </div>
        </>
      )}
    </div>
  );
};

export default NotebooksLayout;
