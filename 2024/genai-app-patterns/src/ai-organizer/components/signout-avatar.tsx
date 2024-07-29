'use client';

import { useSetAtom } from 'jotai';
import { useRouter } from 'next/navigation';
import { VscSignOut } from 'react-icons/vsc';

import { removeSession } from '@/lib/actions/auth';
import { ROOT_ROUTE } from '@/lib/constants';
import { signOut } from '@/lib/firebase/auth';
import { userAtom } from '@/lib/state';

const SignOutAvatar = () => {
  const setUser = useSetAtom(userAtom);
  const router = useRouter();

  const handleClick = async () => {
    await signOut();
    setUser(null);
    await removeSession();
    router.replace(ROOT_ROUTE);
  };

  return <VscSignOut size={28} onClick={handleClick} className="mx-2 cursor-pointer" />;
};

export default SignOutAvatar;
