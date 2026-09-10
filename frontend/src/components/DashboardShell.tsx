import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { Activity, Bell, CloudRain, LogOut, MapPinned, Route, UserRound, Waves } from "lucide-react";
import { useAuth } from "../store/AuthContext";

const links = [{ to: "/", label: "Live Map", icon: MapPinned }, { to: "/forecast", label: "Forecast", icon: CloudRain }, { to: "/routes", label: "Safe Routes", icon: Route }, { to: "/reports", label: "Reports", icon: Bell }];
function Avatar({ name, src }: { name: string; src?: string | null }) { return src ? <img className="profile-avatar" src={src} alt="Profile" /> : <span className="profile-avatar profile-initials">{name.slice(0, 1).toUpperCase()}</span>; }

export default function DashboardShell() {
  const { user, logout } = useAuth(); const navigate = useNavigate(); const [open, setOpen] = useState(false);
  async function signOut() { await logout(); navigate("/login", { replace: true }); }
  return <div className="app-shell"><header className="topbar">
    <NavLink to="/" className="brand"><span className="brand-mark"><Waves size={19} /></span><span><b>FloodFlow</b><small>Urban flood intelligence</small></span></NavLink>
    <nav className="desktop-nav">{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}><Icon size={16} />{label}</NavLink>)}</nav>
    <div className="topbar-actions"><div className="top-status"><Activity size={15} /> <span>Simulation online</span></div><div className="profile-menu-wrap"><button className="profile-trigger" onClick={() => setOpen((value) => !value)} aria-label="Open profile"><Avatar name={user?.name ?? "User"} src={user?.avatar_url} /><span className="profile-trigger-name">{user?.name}</span></button>{open && <div className="profile-menu"><div className="profile-menu-user"><b>{user?.name}</b><small>{user?.role === "ADMIN" ? "Administrator" : "Public account"}</small></div><button onClick={() => { setOpen(false); navigate("/profile"); }}><UserRound size={15} /> Profile</button><button onClick={() => void signOut()}><LogOut size={15} /> Sign out</button></div>}</div></div>
  </header><main className="page-content"><Outlet /></main><nav className="mobile-nav">{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} className={({ isActive }) => isActive ? "mobile-link active" : "mobile-link"}><Icon size={18} /><span>{label.split(" ")[0]}</span></NavLink>)}</nav></div>;
}
