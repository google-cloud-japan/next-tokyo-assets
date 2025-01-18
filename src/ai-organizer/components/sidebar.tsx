'use client';

import { useAtom } from 'jotai';
import Link from 'next/link';
import { MdOutlineClose, MdOutlineMenu } from 'react-icons/md';
import ReactMarkdown from 'react-markdown';
import PacmanLoader from 'react-spinners/PacmanLoader';
import remarkGfm from 'remark-gfm';

import SelectAllSources from '@/components/select-all-sources';
import SourceItems from '@/components/source-items';
import SourceUpload from '@/components/source-upload';
import { APPLICATION_NAME } from '@/lib/constants';
import { sidebarOpenAtom } from '@/lib/state';
import { sourceAtom } from '@/lib/state';
import { cn } from '@/lib/utils';

const Sidebar = () => {
  const [sidebarOpen, setSidebarOpen] = useAtom(sidebarOpenAtom);
  const [source, setSource] = useAtom(sourceAtom);

  const toggleOpen = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <aside
      className={cn('hidden', 'bg-[#F7FBFF]', 'py-2', 'pl-1', 'min-[800px]:block', {
        'w-[260px]': sidebarOpen,
        'w-[64px]': !sidebarOpen,
        'w-[700px]': source,
        'pl-0': source,
        'py-0': source
      })}
    >
      {source ? (
        <div className="flex h-screen w-[700px] flex-col">
          <div className="flex h-[88px] min-h-[88px] items-center justify-between px-[34px] py-5">
            <p className="text-[22px]">{source.name}</p>
            <MdOutlineClose className="cursor-pointer" size={24} onClick={(e) => setSource(null)} />
          </div>
          <div className="flex grow flex-col bg-[#D6E5FF] px-[34px] pb-3">
            <p className="h-12 min-h-12 py-3 font-bold">要約</p>
            {source.summarization ? (
              <div className="h-[calc(100vh-136px)] overflow-y-scroll">
                <ReactMarkdown remarkPlugins={[remarkGfm]} className="markdown">
                  {source.summarization}
                </ReactMarkdown>
              </div>
            ) : (
              <div>
                <p className="text-lg">生成中です。。。</p>
                <div className="flex h-[200px] w-full items-center pl-4">
                  <PacmanLoader size={60} color="#AAAAAA" />
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <>
          <div className="flex h-[72px] pb-6 pr-[10px]">
            <div
              className="flex size-12 items-center justify-center rounded-full transition hover:bg-[#DFE5EC]"
              onClick={toggleOpen}
            >
              <MdOutlineMenu size={24} />
            </div>
            {sidebarOpen && (
              <Link href="/">
                <div className="flex h-12 items-center text-xl">{APPLICATION_NAME}</div>
              </Link>
            )}
          </div>
          {sidebarOpen && (
            <div className="px-[14px]">
              <SourceUpload />
              <SelectAllSources />
            </div>
          )}
          <SourceItems />
        </>
      )}
    </aside>
  );
};

export default Sidebar;
