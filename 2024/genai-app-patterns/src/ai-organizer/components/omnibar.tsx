'use client';

import { useAtom, useAtomValue } from 'jotai';
import { useParams } from 'next/navigation';
import { FaArrowRight } from 'react-icons/fa6';
import { GoNorthStar } from 'react-icons/go';
import { PiChatsFill } from 'react-icons/pi';

import { APPLICATION_NAME } from '@/lib/constants';
import { sendChatMessage } from '@/lib/firebase/firestore';
import { useUserId } from '@/lib/hooks/auth';
import { chatMessagesAtom, commonQuestionsAtom, messageAtom, showChatModalAtom, sourcesAtom } from '@/lib/state';

const Omnibar = () => {
  const [showChatModal, setShowChatModal] = useAtom(showChatModalAtom);
  const chatMessages = useAtomValue(chatMessagesAtom);
  const sources = useAtomValue(sourcesAtom);
  const [message, setMessage] = useAtom(messageAtom);
  const { slug: notebookId } = useParams();
  const uid = useUserId();
  const commonQuestions = useAtomValue(commonQuestionsAtom);

  const selectedSourceCount = sources
    .filter((source) => source.status === 'created')
    .filter((source) => source.selected).length;

  const canSendMessage =
    selectedSourceCount > 0 && !(chatMessages.at(-1)?.role === 'model' && chatMessages.at(-1)?.loading);

  const sourceRagFileIds = sources
    .filter((source) => source.status === 'created' && source.selected)
    .map((source) => source.ragFileId);

  const labelToogleChat = showChatModal ? 'チャットを非表示' : 'チャットを表示';

  const handleClick = () => {
    setShowChatModal((prev) => !prev);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await sendChatMessage(uid as string, notebookId as string, message, sourceRagFileIds);
    setMessage('');
    setShowChatModal(true);
  };

  const handleClickCommonQuestion = async (e: React.MouseEvent<HTMLElement>) => {
    await sendChatMessage(
      uid as string,
      notebookId as string,
      e.currentTarget.dataset.question as string,
      sourceRagFileIds
    );
    setShowChatModal(true);
  };

  return (
    <div className="pointer-events-auto z-20 flex flex-col rounded-t-3xl bg-[#F7FBFF] p-2">
      <div className="flex h-[42px] items-center gap-x-2 overflow-x-auto px-[15px] py-[5px]">
        {commonQuestions &&
          commonQuestions.length > 0 &&
          commonQuestions.map((question, index) => (
            <button
              key={index}
              onClick={handleClickCommonQuestion}
              className="h-8 whitespace-nowrap rounded-full bg-[#DCE1E8] px-4 text-sm"
              data-question={question}
              disabled={!canSendMessage}
            >
              {question}
            </button>
          ))}
      </div>
      <div className="flex h-[72px] items-center justify-evenly pt-2">
        <div className="flex grow items-center justify-center gap-1 text-sm text-[#4966FF]">
          <span className="flex items-center justify-center gap-1 rounded-lg p-2 hover:bg-[#F1F5FA]">
            <PiChatsFill size={20} />
            <span className="whitespace-nowrap" onClick={handleClick}>
              {labelToogleChat}
            </span>
          </span>
        </div>
        <div className="flex grow-[2.5] items-center justify-center">
          <div className="flex h-16 min-w-[100px] items-center justify-center whitespace-nowrap rounded-l-full bg-[#DCE1E8] pl-5 pr-4 text-xs">
            {selectedSourceCount} 個のソース
          </div>
          <form
            className="flex h-16 max-w-[max(50%,min(500px,100%))] flex-1 items-center justify-center rounded-r-full bg-[#E3E8EE]"
            onSubmit={handleSubmit}
          >
            <input
              type="text"
              className="grow bg-[#E3E8EE] px-2 outline-none"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={!canSendMessage}
              minLength={2}
              required
            />
            <button type="submit" className="mx-2 flex size-12 items-center justify-center rounded-full bg-[#ABC8FA]">
              <FaArrowRight size={20} />
            </button>
          </form>
        </div>
        <div className="flex grow items-center justify-center gap-1 text-sm text-[#4966FF]">
          <span className="flex items-center justify-center gap-1 rounded-lg p-2 hover:bg-[#F1F5FA]">
            <GoNorthStar />
            <span className="whitespace-nowrap">ノートブックガイド</span>
          </span>
        </div>
      </div>
      <div className="mb-4 flex items-center justify-center whitespace-nowrap pt-3 text-xs">
        {APPLICATION_NAME} はまだ不正確な回答をすることがあるため、ご自身で事実確認されることをおすすめします。
      </div>
    </div>
  );
};

export default Omnibar;
