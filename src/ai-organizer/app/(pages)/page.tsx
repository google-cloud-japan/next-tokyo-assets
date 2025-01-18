import Header from '@/components/header';
import NotebooksLayout from '@/components/notebooks-layout';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col">
      <Header />
      <div className="flex flex-1 justify-center bg-[#E5EBF2]">
        <NotebooksLayout />
      </div>
    </main>
  );
}
