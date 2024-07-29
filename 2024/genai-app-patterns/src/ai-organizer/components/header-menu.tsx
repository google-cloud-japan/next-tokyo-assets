import { BsQuestionCircle } from 'react-icons/bs';
import { MdOutlineWbSunny } from 'react-icons/md';

import SignOutAvatar from './signout-avatar';

const HeaderMenu = () => {
  return (
    <div className="flex items-center gap-1">
      <div className="flex size-12 min-w-12 items-center justify-center rounded-full transition hover:bg-[#DFE5EC]">
        <MdOutlineWbSunny size={24} />
      </div>
      <div className="flex size-12 min-w-12 items-center justify-center rounded-full transition hover:bg-[#DFE5EC]">
        <BsQuestionCircle size={24} />
      </div>
      <SignOutAvatar />
    </div>
  );
};

export default HeaderMenu;
