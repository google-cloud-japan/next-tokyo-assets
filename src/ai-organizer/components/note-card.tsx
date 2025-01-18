import { Timestamp } from 'firebase/firestore';
import { MdOutlineChat } from 'react-icons/md';
import ReactMarkdown from 'react-markdown';
import { RingLoader } from 'react-spinners';
import remarkGfm from 'remark-gfm';

import { Dialog, DialogContent, DialogDescription, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

type NoteCardProps = {
  id: string;
  content: string;
  status: string;
  createdAt: Timestamp;
};

const NoteCard = ({ id, content, status, createdAt }: NoteCardProps) => {
  return (
    <div className="m-3 h-[338px] w-[349px] rounded-2xl bg-[#F2F6FA]">
      {status === 'creating' ? (
        <div className="flex h-full items-center justify-center p-4">
          <RingLoader color="#000000" size={120} />
        </div>
      ) : (
        <>
          <Dialog>
            <DialogTrigger className="cursor-pointer text-left">
              <div className="flex h-[69px] min-h-[69px] justify-between px-4 pt-4">
                <div>
                  <div className="flex h-[29px] min-h-[29px] items-center gap-2 text-sm text-[#6EA2FF]">
                    <MdOutlineChat size={18} />
                    <p>保存済みの回答</p>
                  </div>
                  <p className="text-lg">新しい保存済みメモ</p>
                </div>
              </div>
              <div className="h-[217px] min-h-[217px] overflow-hidden px-4 pt-[14px] text-sm">
                <ReactMarkdown remarkPlugins={[remarkGfm]} className="markdown">
                  {content}
                </ReactMarkdown>
              </div>
              <div className="mt-2 flex h-9 min-h-9 items-center px-4 py-2 text-sm">
                <p className="font-bold">作成日時</p>：
                {`${createdAt?.toDate().toLocaleDateString()} ${createdAt?.toDate().toLocaleTimeString()}`}
              </div>
            </DialogTrigger>
            <DialogContent className="h-[50vh] w-1/2 max-w-[50%] p-0">
              <div className="flex flex-col overflow-hidden">
                <div className="flex bg-[#F2F6FA] pl-4">
                  <div className="pt-4">
                    <DialogTitle>
                      <p className="text-lg font-semibold">新しい保存済みメモ</p>
                    </DialogTitle>
                    <DialogDescription className="text-[16px] text-black">保存済みの回答</DialogDescription>
                    <div className="py-2">
                      <p className="px-[6px] py-1 text-sm font-bold">保存した回答は表示専用です</p>
                    </div>
                  </div>
                </div>
                <div className="overflow-y-auto px-[15px] py-3">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} className="markdown">
                    {content}
                  </ReactMarkdown>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </>
      )}
    </div>
  );
};

export default NoteCard;
