'use client';

import { useAtom } from 'jotai';
import { useParams } from 'next/navigation';
import { useEffect } from 'react';
import { BsTrash } from 'react-icons/bs';
import { MdOutlineClose } from 'react-icons/md';

import MessageModel from '@/components/message-model';
import MessageUser from '@/components/message-user';
import { deleteChatHistory, getChatHistorySnapshot } from '@/lib/firebase/firestore';
import { useUserId } from '@/lib/hooks/auth';
import { chatMessagesAtom, showChatModalAtom } from '@/lib/state';
import { cn } from '@/lib/utils';

const ChatModal = () => {
  const [chatMessages, setChatMessages] = useAtom(chatMessagesAtom);
  const [showChatModal, setShowChatModal] = useAtom(showChatModalAtom);
  const { slug: notebookId } = useParams();
  const uid = useUserId();

  useEffect(() => {
    if (!uid || !notebookId) return;
    const unsubscribe = getChatHistorySnapshot(uid, notebookId as string, (data) => {
      setChatMessages(data);
    });

    return () => unsubscribe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uid, notebookId]);

  const clearMessages = async () => {
    await deleteChatHistory(uid as string, notebookId as string);
  };

  return (
    <div
      className={cn(
        'absolute',
        'flex',
        'z-10',
        'w-full',
        'overflow-hidden',
        'justify-center',
        'transition-[height,visibility,opacity,top]',
        'duration-300',
        'ease-in-out',
        'bg-[#CCD0D6]',
        {
          'top-full': !showChatModal,
          'top-0': showChatModal,
          visible: showChatModal,
          invisible: !showChatModal,
          'h-full': showChatModal,
          'h-0': !showChatModal,
          'opacity-0': !showChatModal,
          'opacity-100': showChatModal
        }
      )}
    >
      <div className="relative z-10 m-1 flex max-w-[1130px] flex-1 flex-col overflow-hidden">
        <div className="absolute right-0 top-0 flex gap-6 px-8 pt-4">
          <BsTrash size={28} onClick={clearMessages} className="cursor-pointer" />
          <MdOutlineClose size={28} onClick={() => setShowChatModal(false)} className="cursor-pointer" />
        </div>
        <div className="hidden-scrollbar overflow-y-auto overflow-x-hidden px-8 pb-[160px] pt-16">
          {chatMessages.map((message) => {
            return message.role === 'model' ? (
              <MessageModel
                key={message.id}
                content={message.content}
                loading={message.loading}
                uid={uid as string}
                notebookId={notebookId as string}
              />
            ) : (
              <MessageUser key={message.id} content={message.content} />
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ChatModal;
