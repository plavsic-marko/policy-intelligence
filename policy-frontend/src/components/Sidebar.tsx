import { NavLink } from "react-router-dom";

const Sidebar = () => {
  return (
    <div className="w-48 bg-slate-950 border-r border-slate-800 min-h-screen py-6 flex flex-col gap-2">

      <div className="px-4 pb-4 text-xs uppercase text-slate-500 tracking-wider">
        Navigation
      </div>

      <NavLink
        to="/"
        className={({ isActive }) =>
          `px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 transition ${
            isActive
              ? "bg-slate-800 text-white"
              : "text-slate-300 hover:bg-slate-800/60"
          }`
        }
      >
        <span>Policy Chat</span>
      </NavLink>

      <NavLink
        to="/history"
        className={({ isActive }) =>
          `px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 transition ${
            isActive
              ? "bg-slate-800 text-white"
              : "text-slate-300 hover:bg-slate-800/60"
          }`
        }
      >
        <span>History</span>
      </NavLink>

    </div>
  );
};

export default Sidebar;
