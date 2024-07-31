'use client';
import { useAtom } from 'jotai';
import { useParams } from 'next/navigation';
import { useEffect } from 'react';

import SourceItem from '@/components/source-item';
import { getSourcesSnapshot } from '@/lib/firebase/firestore';
import { useUserId } from '@/lib/hooks/auth';
import { sourcesAtom } from '@/lib/state';

const SourceItems = () => {
  const [sources, setSources] = useAtom(sourcesAtom);
  const { slug: notebookId } = useParams();
  const uid = useUserId();

  useEffect(() => {
    if (!notebookId || !uid) {
      return;
    }
    const unsubscribe = getSourcesSnapshot(uid, notebookId as string, (data) => {
      setSources(data);
    });

    return () => {
      unsubscribe();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uid, notebookId]);

  return (
    <>
      {sources.map((source) => (
        <SourceItem key={source.id} uid={uid as string} source={source} notebookId={notebookId as string} />
      ))}
    </>
  );
};

export default SourceItems;
