import { Timestamp } from 'firebase/firestore';
import Link from 'next/link';
import { BsThreeDotsVertical } from 'react-icons/bs';

export type Notebook = {
  id: string;
  title: string;
  count: number;
  createdAt: Timestamp;
};

const NotebookCard = ({ id, title, count, createdAt }: Notebook) => {
  return (
    <Link href={`/notebook/${id}`}>
      <div className="flex size-[224px] flex-col rounded-2xl bg-[#CDD2D9]">
        <div className="flex h-[106px] justify-between p-3">
          <div className="flex size-8 items-center justify-center rounded-full bg-white">
            <p>K</p>
          </div>
          <div className="flex size-8 items-center justify-center rounded-full hover:bg-[#C8CFD6] ">
            <BsThreeDotsVertical size={20} />
          </div>
        </div>
        <p className="line-clamp-2 h-16 px-4 text-2xl font-semibold">{title}</p>
        <div className="flex h-[52px] p-4 text-sm">
          <p>{createdAt?.toDate().toLocaleDateString()}</p>
          <p>・</p>
          <p>{count} 個のソース</p>
        </div>
      </div>
    </Link>
  );
};

export default NotebookCard;
