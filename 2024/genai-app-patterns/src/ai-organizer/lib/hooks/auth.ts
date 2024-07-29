import { useEffect, useState } from 'react';

import { onAuthStateChanged } from '@/lib/firebase/auth';

export const useUserId = (): string | null => {
  const [uid, setUid] = useState<string | null>(null);

  useEffect(() => {
    onAuthStateChanged((user) => {
      if (user) {
        setUid(user.uid);
      } else {
        setUid(null);
      }
    });
  }, []);

  return uid;
};
