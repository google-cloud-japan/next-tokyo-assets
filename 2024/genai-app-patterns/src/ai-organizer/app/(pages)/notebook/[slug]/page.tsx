import { FaCheck } from 'react-icons/fa6';
import { MdOutlineTextSnippet } from 'react-icons/md';

import ChatModal from '@/components/chat-modal';
import NotesLayout from '@/components/notes-layout';
import Omnibar from '@/components/omnibar';
import PageHeader from '@/components/page-header';
import Sidebar from '@/components/sidebar';

export default function NotebookPage() {
  return (
    <div className="flex h-screen flex-col">
      <div className="flex flex-1 overflow-y-hidden">
        <div className="flex size-full">
          <Sidebar />
          <div className="flex flex-1 flex-col">
            <PageHeader />
            <div className="relative flex h-full grow flex-col">
              <div className="flex h-14 min-h-14 items-center gap-1 bg-[#E3E8EE] px-5 pb-2 pt-1">
                <button className="flex items-center justify-center gap-1 rounded-md px-4 py-[6px] transition hover:bg-[#D0D5DA] hover:shadow">
                  <MdOutlineTextSnippet size={20} />
                  <span className="text-sm">メモを追加</span>
                </button>
                <button className="flex items-center justify-center gap-1 rounded-md px-4 py-[6px] transition hover:bg-[#D0D5DA] hover:shadow">
                  <FaCheck size={20} />
                  <span className="text-sm">すべて選択</span>
                </button>
              </div>
              <div className="flex grow flex-col overflow-hidden bg-[#E3E8EE]">
                <NotesLayout />
                <div className="pointer-events-none absolute flex size-full justify-center">
                  <div className="pointer-events-none z-20 mx-1 flex max-w-[1130px] grow flex-col overflow-hidden">
                    <div className="pointer-events-none flex h-[calc(100%-40px)] flex-col-reverse">
                      <Omnibar />
                    </div>
                  </div>
                </div>
              </div>
              <ChatModal />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
