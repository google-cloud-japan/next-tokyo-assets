'use client';

import { useAtom } from 'jotai';
import Link from 'next/link';
import { MdOutlineMenu } from 'react-icons/md';

import { APPLICATION_NAME } from '@/lib/constants';
import { sidebarOpenAtom } from '@/lib/state';
import { cn } from '@/lib/utils';

import SelectAllSources from './select-all-sources';
import SourceItems from './source-items';
import SourceUpload from './source-upload';

const Sidebar = () => {
  const [sidebarOpen, setSidebarOpen] = useAtom(sidebarOpenAtom);

  const toggleOpen = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <aside
      className={cn('hidden', 'bg-[#F7FBFF]', 'py-2', 'pl-1', 'min-[800px]:block', {
        'w-[260px]': sidebarOpen,
        'w-[64px]': !sidebarOpen
      })}
    >
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
    </aside>
  );
};

export default Sidebar;
