'use client';

import { useAtomValue } from 'jotai';
import { useParams } from 'next/navigation';

import { toggleSourceSelected } from '@/lib/firebase/firestore';
import { useUserId } from '@/lib/hooks/auth';
import { sourcesAtom } from '@/lib/state';

const SelectAllSources = () => {
  const sources = useAtomValue(sourcesAtom);
  const allSelected = sources.filter((source) => source.status === 'created').every((source) => source.selected);
  const { slug: notebookId } = useParams();
  const uid = useUserId();

  const handleClickAllSelect = async () => {
    if (allSelected) {
      sources.forEach(async (source) => {
        if (source.status === 'created' && source.selected) {
          await toggleSourceSelected(uid as string, notebookId as string, source.id, false);
        }
      });
      return;
    }
    sources.forEach(async (source) => {
      if (source.status === 'created' && !source.selected) {
        await toggleSourceSelected(uid as string, notebookId as string, source.id, true);
      }
    });
  };

  return (
    <div className="flex h-10 items-center justify-between">
      <span className="flex items-center text-sm">すべてのソースを選択</span>
      <div className="flex w-8 items-center justify-center">
        <input
          type="checkbox"
          className="size-4 cursor-pointer"
          checked={allSelected}
          onChange={handleClickAllSelect}
        />
      </div>
    </div>
  );
};

export default SelectAllSources;
