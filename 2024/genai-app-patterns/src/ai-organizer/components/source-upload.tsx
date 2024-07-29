'use client';

import { ref, uploadBytesResumable } from 'firebase/storage';
import { customAlphabet } from 'nanoid';
import { alphanumeric } from 'nanoid-dictionary';
import { useParams } from 'next/navigation';
import { useState } from 'react';
import { BsMarkdown } from 'react-icons/bs';
import { FaRegPlusSquare } from 'react-icons/fa';
import { FaRegFilePdf } from 'react-icons/fa6';
import { PiFileAudio } from 'react-icons/pi';
import { RiShieldUserLine } from 'react-icons/ri';
import { RiMovieLine } from 'react-icons/ri';
import { RxFileText } from 'react-icons/rx';

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
import { storage } from '@/lib/firebase/client-app';
import { addSource } from '@/lib/firebase/firestore';
import { useUserId } from '@/lib/hooks/auth';

const SourceUpload = () => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { slug: notebookId } = useParams();
  const uid = useUserId();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const file = e.target.files[0];
    const fileId = customAlphabet(alphanumeric, 20)();
    const fileExtension = file.name.split('.').pop();
    const filePath = `/files/${uid}/${fileId}.${fileExtension}`;
    const storageRef = ref(storage, filePath);

    const uploadTask = uploadBytesResumable(storageRef, file, {
      contentType: file.type
    });

    setDialogOpen(false);

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
            console.log('NO PERMISSION');
            break;
          case 'storage/canceled':
            break;
          case 'storage/unknown':
            break;
        }
      },
      async () => {
        console.log('upload finished!!');
        await addSource(fileId, uid as string, file.type, filePath, notebookId as string, file.name);
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
            <FilePicker id="audio" handleUpload={handleUpload} accept="audio/*" label="音声ファイル">
              <PiFileAudio size={24} />
            </FilePicker>
            <FilePicker id="movie" handleUpload={handleUpload} accept="video/*" label="動画ファイル">
              <RiMovieLine size={24} />
            </FilePicker>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default SourceUpload;
