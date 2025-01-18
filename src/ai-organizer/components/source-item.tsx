'use client';

import { useAtomValue, useSetAtom } from 'jotai';
import { FormEvent, useState } from 'react';
import { BsTrash } from 'react-icons/bs';
import { BsFiletypeHtml, BsFiletypeJson, BsMarkdown, BsThreeDotsVertical } from 'react-icons/bs';
import { FaRegFileWord } from 'react-icons/fa';
import { FaRegFilePowerpoint } from 'react-icons/fa';
import { FaRegFilePdf } from 'react-icons/fa6';
import { LuFileQuestion } from 'react-icons/lu';
import { MdOutlineEdit } from 'react-icons/md';
import { RxFileText } from 'react-icons/rx';
import ClipLoader from 'react-spinners/ClipLoader';
import PuffLoader from 'react-spinners/PuffLoader';

import { Dialog, DialogContent, DialogDescription, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import VisuallyHidden from '@/components/visually-hidden';
import { deleteSource, Source, toggleSourceSelected, updateSourceName } from '@/lib/firebase/firestore';
import { sidebarOpenAtom, sourceAtom } from '@/lib/state';
import { cn } from '@/lib/utils';

export type SourceItemProps = {
  source: Source;
  uid: string;
  notebookId: string;
};

const SourceItem = ({ source, uid, notebookId }: SourceItemProps) => {
  const { id, name, type, selected, status } = source;
  const [dialogForDeleteOpen, setDialogForDeleteOpen] = useState(false);
  const [dialogForNameChangeOpen, setDialogForNameChangeOpen] = useState(false);
  const [dropdownMenuOpen, setDropdownMenuOpen] = useState(false);
  const [hover, setHover] = useState(false);
  const open = useAtomValue(sidebarOpenAtom);
  const [editableName, setEditableName] = useState(name);
  const setSource = useSetAtom(sourceAtom);

  const disabled = status !== 'created';

  const handleMouseOver = () => {
    setHover(true);
  };

  const handleMouseOut = () => {
    setHover(false);
  };

  const handleClickCheckbox = async () => {
    await toggleSourceSelected(uid, notebookId, id, !selected);
  };

  const handleClickDelete = async () => {
    await deleteSource(id, uid, notebookId);
    setDialogForDeleteOpen(false);
    setDropdownMenuOpen(false);
    setHover(false);
  };

  const handleSubmitNameChange = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await updateSourceName(id, uid, notebookId, editableName);
    setDialogForNameChangeOpen(false);
    setDropdownMenuOpen(false);
    setHover(false);
  };

  const handleClickName = () => {
    setSource(source);
  };

  const fileIcon = () => {
    switch (true) {
      case /application\/pdf/.test(type):
        return <FaRegFilePdf size={24} color="red" />;
      case /text\/plain/.test(type):
        return <RxFileText size={24} color="#6F51A1" />;
      case /text\/markdown/.test(type):
        return <BsMarkdown size={24} />;
      case /text\/html/.test(type):
        return <BsFiletypeHtml size={24} color="#E54C21" />;
      case /application\/json/.test(type):
        return <BsFiletypeJson size={24} color="#1D1D1D" />;
      case /application\/vnd\.openxmlformats-officedocument\.wordprocessingml\.document/.test(type):
        return <FaRegFileWord size={24} color="#2A5599" />;
      case /application\/vnd\.openxmlformats-officedocument\.presentationml\.presentation/.test(type):
        return <FaRegFilePowerpoint size={24} color="#D14425" />;
      default:
        return <LuFileQuestion size={24} />;
    }
  };

  return (
    <div
      className="flex h-14 w-full cursor-pointer items-center rounded-lg pr-[14px] transition hover:bg-slate-100"
      onMouseOver={handleMouseOver}
      onMouseOut={handleMouseOut}
    >
      <DropdownMenu open={dropdownMenuOpen} onOpenChange={setDropdownMenuOpen}>
        <DropdownMenuTrigger disabled={status !== 'created'} asChild>
          {hover ? (
            <button className="flex size-12 min-w-12 items-center justify-center rounded-full transition hover:bg-[#DFE5EC]">
              <BsThreeDotsVertical size={20} />
            </button>
          ) : (
            <div className="flex size-12 min-w-12 items-center justify-center rounded-full transition hover:bg-[#DFE5EC]">
              {fileIcon()}
            </div>
          )}
        </DropdownMenuTrigger>
        <DropdownMenuContent className="p-0" align="start">
          <Dialog open={dialogForDeleteOpen} onOpenChange={setDialogForDeleteOpen}>
            <DialogTrigger className="flex h-12 w-full items-center px-2 py-[6px] hover:bg-[#EDEEEE]">
              <BsTrash size={18} className="mr-2" />
              <span className="text-sm">ソースを削除</span>
            </DialogTrigger>
            <DialogContent className="w-fit max-w-[120%] p-0">
              <VisuallyHidden>
                <DialogTitle>Delete source</DialogTitle>
                <DialogDescription>Delete source</DialogDescription>
              </VisuallyHidden>
              <div className="p-4">
                <p className="px-6 py-5 text-lg">{name} を削除しますか？</p>
                <div className="flex h-[52px] items-center justify-end px-2 py-[2px]">
                  <span
                    className="m-2 cursor-pointer p-2 text-sm text-blue-500 hover:bg-[#F7FAFE] hover:text-blue-800"
                    onClick={() => setDialogForDeleteOpen(false)}
                  >
                    キャンセル
                  </span>
                  <span
                    className="m-2 cursor-pointer p-2 text-sm text-blue-500 hover:bg-[#F7FAFE] hover:text-blue-800"
                    onClick={handleClickDelete}
                  >
                    削除
                  </span>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog open={dialogForNameChangeOpen} onOpenChange={setDialogForNameChangeOpen}>
            <DialogTrigger className="flex h-12 w-full items-center px-2 py-[6px] hover:bg-[#EDEEEE]">
              <MdOutlineEdit size={18} className="mr-2" />
              <span className="text-sm">ソース名を変更</span>
            </DialogTrigger>
            <DialogContent className="w-fit max-w-[120%] p-0">
              <VisuallyHidden>
                <DialogTitle>Submit name change</DialogTitle>
                <DialogDescription>Update source name</DialogDescription>
              </VisuallyHidden>
              <form className="px-6 py-5" onSubmit={handleSubmitNameChange}>
                <p className="pb-4 text-lg">{name} の名前を変更しますか？</p>
                <input
                  type="text"
                  value={editableName}
                  onChange={(event) => setEditableName(event.target.value)}
                  className="mb-4 w-full rounded-sm border border-black px-6 py-5"
                  minLength={3}
                  maxLength={50}
                  required
                />
                <div className="flex h-[52px] items-center justify-end px-2 py-[2px]">
                  <span
                    className="m-2 cursor-pointer p-2 text-sm text-blue-500 hover:bg-[#F7FAFE] hover:text-blue-800"
                    onClick={() => setDialogForNameChangeOpen(false)}
                  >
                    キャンセル
                  </span>
                  <button
                    type="submit"
                    className="m-2 cursor-pointer p-2 text-sm text-blue-500 hover:bg-[#F7FAFE] hover:text-blue-800"
                  >
                    保存
                  </button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </DropdownMenuContent>
      </DropdownMenu>
      {open && (
        <>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <span
                  className={cn('flex-1 truncate text-sm', { 'font-semibold': source.summarization })}
                  onClick={handleClickName}
                >
                  {name}
                </span>
              </TooltipTrigger>
              <TooltipContent side="bottom" className="border-[#616161] bg-[#616161] text-white">
                <p className="flex-1 text-xs">{name}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <div className="flex w-8 items-center justify-center">
            {status === 'created' && (
              <input
                type="checkbox"
                className="size-4 cursor-pointer"
                checked={selected}
                onChange={handleClickCheckbox}
                disabled={disabled}
              />
            )}
            {status === 'creating' && <ClipLoader size={20} color="#0075FF" />}
            {status === 'deleting' && <PuffLoader size={20} color="#FF0000" />}
          </div>
        </>
      )}
    </div>
  );
};

export default SourceItem;
