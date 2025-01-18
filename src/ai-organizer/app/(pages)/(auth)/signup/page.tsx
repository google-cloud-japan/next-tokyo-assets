'use client';

import { useSetAtom } from 'jotai';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';
import { toast } from 'sonner';

import { createSession } from '@/lib/actions/auth';
import { HOME_ROUTE } from '@/lib/constants';
import { createUserWithEmailAndPassword } from '@/lib/firebase/auth';
import { addUser, getUserByUid } from '@/lib/firebase/firestore';
import { userAtom } from '@/lib/state';

const SignupPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const setUser = useSetAtom(userAtom);
  const router = useRouter();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const user = await createUserWithEmailAndPassword(email, password);
      await createSession(user.uid);
      await addUser(user.uid, user.email as string);
      const userInFirestore = await getUserByUid(user.uid);
      setUser(userInFirestore);
      router.replace(HOME_ROUTE);
      toast.success('アカウント登録が完了しました');
    } catch (e) {
      toast.error('アカウント登録に失敗しました');
      console.log(e);
    }
  };

  return (
    <>
      <div className="flex h-screen items-center justify-center">
        <div className="w-80 rounded-md p-8 shadow-lg">
          <p className="mb-4 text-xl font-bold">アカウント登録</p>
          <form action="submit" autoComplete="off" onSubmit={handleSubmit}>
            <label htmlFor="email" className="mb-1 block ">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="mb-4 w-full rounded-md border border-[#E1E1E1] p-2 outline-none"
              required
              minLength={6}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
            <label htmlFor="password" className="mb-1 block">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="mb-8 w-full rounded-md border border-[#E1E1E1] p-2 outline-none"
              required
              minLength={6}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
            <button type="submit" className="mb-2 w-full rounded-md bg-primary px-4 py-2 font-bold text-white">
              アカウント登録
            </button>
          </form>
          <p className="text-center text-sm">
            アカウントをお持ちの方は
            <Link href="/signin" className="font-bold text-blue-500">
              こちら
            </Link>
          </p>
        </div>
      </div>
    </>
  );
};

export default SignupPage;
