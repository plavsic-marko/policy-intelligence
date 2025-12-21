const Topbar = () => {
  return (
    <div className="h-14 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6">

      <div className="text-lg font-semibold text-white tracking-wide">
        Policy Intelligence Assistant
      </div>

      <div className="flex items-center gap-2 text-slate-400 text-sm">
        <img
          src="/flags/switzerland.png"
          alt="Swiss flag"
          className="w-4 h-4"
        />
        <span>Swiss Canton Edition</span>
      </div>

    </div>
  );
};

export default Topbar;
