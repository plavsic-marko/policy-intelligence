import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex bg-slate-900 text-white min-h-screen">

      
      <Sidebar />

      <div className="flex-1 flex flex-col">

       
        <Topbar />

        
        <div className="p-8 overflow-y-auto h-full bg-[#0f172a]">

          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;
