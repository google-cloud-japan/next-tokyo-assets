import HeaderMenu from '@/components/header-menu';
import { APPLICATION_NAME } from '@/lib/constants';

const Header = () => {
  return (
    <header className="flex h-16 min-h-16 justify-between bg-[#F7FBFF] px-3">
      <div className="flex items-center pl-3 text-2xl">{APPLICATION_NAME}</div>
      <HeaderMenu />
    </header>
  );
};

export default Header;
