'use client';

import { getDownloadURL, ref, uploadBytesResumable } from 'firebase/storage';
import { customAlphabet } from 'nanoid';
import { alphanumeric } from 'nanoid-dictionary';
import { useParams } from 'next/navigation';
import { useState } from 'react';
import { BsFiletypeHtml, BsFiletypeJson, BsMarkdown } from 'react-icons/bs';
import { FaRegFilePowerpoint, FaRegFileWord, FaRegPlusSquare } from 'react-icons/fa';
import { FaRegFilePdf } from 'react-icons/fa6';
import { RiShieldUserLine } from 'react-icons/ri';
import { RxFileText } from 'react-icons/rx';
import { toast } from 'sonner';

import FilePicker from '@/components/file-picker';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
import VisuallyHidden from '@/components/visually-hidden';
import { MAX_FILE_SIZE } from '@/lib/constants';
import { storage } from '@/lib/firebase/client-app';
import { addSource } from '@/lib/firebase/firestore';
import { useUserId } from '@/lib/hooks/auth';
import { isAcceptableFileType } from '@/lib/utils';

const SourceUpload = () => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { slug: notebookId } = useParams();
  const uid = useUserId();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const file = e.target.files[0];

    setDialogOpen(false);

    if (!isAcceptableFileType(file.type)) {
      toast.error('ファイルのアップロードに失敗しました: 許可されていないファイル形式です');
      return;
    }
    const maxFileSizeForFile = (
      Object.entries(MAX_FILE_SIZE).find(([key]) => key === file.type) as [string, number]
    )[1];
    if (file.size > maxFileSizeForFile) {
      toast.error('ファイルのアップロードに失敗しました: ファイルサイズが大きすぎます');
      return;
    }

    const fileId = customAlphabet(alphanumeric, 20)();
    const fileExtension = file.name.split('.').pop();
    const filePath = `/files/${uid}/${fileId}.${fileExtension}`;
    const storageRef = ref(storage, filePath);

    const uploadTask = uploadBytesResumable(storageRef, file, {
      contentType: file.type
    });

    toast.success('ファイルのアップロードを開始しました');

    uploadTask.on(
      'state_changed',
      (snapshot) => {
        const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        console.log('upload is ' + progress + '% done');
        switch (snapshot.state) {
          case 'paused':
            console.log('upload is paused');
            break;
          case 'running':
            console.log('upload is running');
            break;
        }
      },
      (error) => {
        switch (error.code) {
          case 'storage/unauthorized':
            toast.error('ファイルのアップロードに失敗しました: 権限がありません');
            break;
          case 'storage/canceled':
            toast.error('ファイルのアップロードがキャンセルされました');
            break;
          case 'storage/unknown':
            toast.error('不明なエラーが発生しました');
            break;
        }
      },
      async () => {
        console.log('upload finished!!');
        const downloadURL = await getDownloadURL(storageRef);
        await addSource(fileId, uid as string, file.type, filePath, notebookId as string, file.name, downloadURL);
      }
    );
  };

  return (
    <div className="flex h-9 items-center justify-between">
      <div className="flex">
        <span className="flex items-center text-sm">ソース</span>
        <div className="pl-1">
          <RiShieldUserLine size={24} />
        </div>
      </div>
      <div className="flex w-8 items-center justify-center">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger>
            <FaRegPlusSquare size={18} className="cursor-pointer" />
          </DialogTrigger>
          <DialogContent className="w-[256px] gap-0 p-4">
            <DialogHeader>
              <DialogTitle className="flex h-12 min-h-12 items-center text-xl">アップロード元</DialogTitle>
            </DialogHeader>
            <VisuallyHidden>
              <DialogDescription>Upload files</DialogDescription>
            </VisuallyHidden>
            <FilePicker id="pdf" handleUpload={handleUpload} accept=".pdf" label="PDF">
              <FaRegFilePdf size={24} />
            </FilePicker>
            <FilePicker id="text" handleUpload={handleUpload} accept=".txt" label="テキスト ファイル">
              <RxFileText size={24} />
            </FilePicker>
            <FilePicker id="markdown" handleUpload={handleUpload} accept=".md" label="マークダウン ファイル">
              <BsMarkdown size={24} />
            </FilePicker>
            {/* <FilePicker id="word" handleUpload={handleUpload} accept=".docx" label="ワード ファイル">
              <FaRegFileWord size={24} />
            </FilePicker>
            <FilePicker id="powerpoint" handleUpload={handleUpload} accept=".pptx" label="パワーポイント ファイル">
              <FaRegFilePowerpoint size={24} />
            </FilePicker> */}
            <FilePicker id="html" handleUpload={handleUpload} accept=".html,.htm" label="HTML ファイル">
              <BsFiletypeHtml size={24} />
            </FilePicker>
            <FilePicker id="json" handleUpload={handleUpload} accept=".json" label="JSON ファイル">
              <BsFiletypeJson size={24} />
            </FilePicker>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default SourceUpload;
