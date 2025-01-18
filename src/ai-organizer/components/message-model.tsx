'use client';

import { useSetAtom } from 'jotai';
import { MdOutlinePushPin } from 'react-icons/md';
import ReactMarkdown from 'react-markdown';
import PulseLoader from 'react-spinners/PulseLoader';
import remarkGfm from 'remark-gfm';

import { addNote } from '@/lib/firebase/firestore';
import { showChatModalAtom } from '@/lib/state';

type MessageModelProps = {
  content: string;
  loading: boolean;
  uid: string;
  notebookId: string;
};

const MessageModel = ({ content, loading, uid, notebookId }: MessageModelProps) => {
  const setShowChatModal = useSetAtom(showChatModalAtom);

  const handleClickPin = async () => {
    await addNote(uid, notebookId, content);
    setShowChatModal(false);
  };

  return (
    <div className="flex w-full justify-start pb-5 pr-8">
      <div className="relative max-w-[900px] rounded-2xl bg-[#F7FBFF] p-5 text-sm shadow-md">
        {loading ? (
          <PulseLoader size={8} />
        ) : (
          <>
            <MdOutlinePushPin
              className="absolute right-2 top-2 cursor-pointer rounded-full bg-black/50 p-2"
              size={40}
              color="white"
              onClick={handleClickPin}
            />
            <ReactMarkdown remarkPlugins={[remarkGfm]} className="markdown">
              {content}
            </ReactMarkdown>
          </>
        )}
      </div>
    </div>
  );
};

export default MessageModel;
