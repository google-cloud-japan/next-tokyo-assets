'use client';

import { useAtom } from 'jotai';
import { toast } from 'sonner';

import { createSession, removeSession } from '@/lib/actions/auth';
import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from '@/lib/firebase/auth';
import { addUser, getUserByUid } from '@/lib/firebase/firestore';
import { userAtom } from '@/lib/state';

const Auth = () => {
  const [user, setUser] = useAtom(userAtom);

  const handleSignIn = async () => {
    const user = await signInWithEmailAndPassword('hasebok6@gmail.com', 'Passw0rd');
    if (user) {
      console.log(`User ${user.uid} signined`);
      const userInFirestore = await getUserByUid(user.uid);
      setUser(userInFirestore);
      await createSession(user.uid);
    }
  };

  const handleSignUp = async () => {
    const user = await createUserWithEmailAndPassword('hasebok6@gmail.com', 'Passw0rd');
    if (user) {
      console.log(`User ${user.uid} created`);
      await createSession(user.uid);
      await addUser(user.uid, user.email as string);
      const userInFirestore = await getUserByUid(user.uid);
      setUser(userInFirestore);
    }
  };

  const handleSignOut = async () => {
    await signOut();
    await removeSession();
    setUser(null);
  };

  if (!user) {
    return (
      <div className="flex h-screen items-center justify-center gap-4">
        <button className="rounded bg-primary px-4 py-2 font-bold text-white" onClick={handleSignUp}>
          Sign up
        </button>
        <button className="rounded bg-primary px-4 py-2 font-bold text-white" onClick={handleSignIn}>
          Sign in
        </button>
        <button
          className="rounded bg-primary px-4 py-2 font-bold text-white"
          onClick={() => {
            toast.success('success');
          }}
        >
          Toast!!!
        </button>
      </div>
    );
  }

  return (
    <div>
      <button className="rounded bg-primary px-4 py-2 font-bold text-white" onClick={handleSignOut}>
        Sign out
      </button>
    </div>
  );
};

export default Auth;
