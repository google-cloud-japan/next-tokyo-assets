import Link from 'next/link';
import { FaArrowLeft } from 'react-icons/fa6';

import HeaderMenu from '@/components/header-menu';

import EditableNotebookName from './editable-notebook-name';

const PageHeader = () => {
  return (
    <header className="flex h-16 min-h-16 items-center justify-between border-l-2 border-[#E3E8EE] bg-[#F7FBFF] px-3">
      <div className="flex items-center justify-center">
        <div className="flex size-12 items-center justify-center min-[800px]:hidden">
          <Link href="/">
            <FaArrowLeft size={20} />
          </Link>
        </div>
        <EditableNotebookName />
      </div>
      <HeaderMenu />
    </header>
  );
};

export default PageHeader;
