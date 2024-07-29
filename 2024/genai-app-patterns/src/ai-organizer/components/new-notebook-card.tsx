'use client';

import { useRouter } from 'next/navigation';
import { FaPlus } from 'react-icons/fa6';

import { auth } from '@/lib/firebase/client-app';
import { addNotebook } from '@/lib/firebase/firestore';

const NewNotebookCard = () => {
  const router = useRouter();
  const uid = auth.currentUser?.uid as string;

  const handleClick = async () => {
    const notebookId = await addNotebook(uid, 'New notebook');
    router.push(`/notebook/${notebookId}`);
  };

  return (
    <div
      className="flex size-[224px] cursor-pointer flex-col items-center rounded-2xl border border-gray-400"
      onClick={handleClick}
    >
      <FaPlus size={40} className="h-[144px] pt-9" />
      <p className="px-1 text-center text-2xl">
        新しい
        <br />
        ノートブック
      </p>
    </div>
  );
};

export default NewNotebookCard;
