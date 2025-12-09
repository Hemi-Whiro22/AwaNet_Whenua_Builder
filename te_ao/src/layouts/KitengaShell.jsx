import Sidebar from "../components/chat/Sidebar";
import HeaderBar from "../components/chat/HeaderBar";

export default function KitengaShell({ children }) {
  return (
    <div className="flex h-screen overflow-hidden text-koru1 bg-transparent">
      <div className="w-16 shrink-0 overflow-y-auto border-r border-koru3">
        <Sidebar />
      </div>

      <div className="flex flex-col flex-1">
        <header className="sticky top-0 z-20 bg-back/70 border-b border-koru3">
          <HeaderBar />
        </header>

        <main className="flex-1 overflow-y-auto p-4">{children}</main>
      </div>
    </div>
  );
}
