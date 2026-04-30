import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { motion, AnimatePresence } from "framer-motion";

const icons = {
  dashboard: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>,
  students: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>,
  prediction: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>,
  batch: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>,
  analysis: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" /></svg>,
  users: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>,
  admin: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>,
};

const ROLE_LABELS = {
  super_admin:           { label: "Super Administrateur",      color: "bg-purple-100 text-purple-700" },
  directeur_adjoint:     { label: "Directeur Adjoint",         color: "bg-blue-100 text-blue-700" },
  chef_departement_STIN: { label: "Chef Dép. STIN",            color: "bg-orange-100 text-orange-700" },
  chef_departement_TRI:  { label: "Chef Dép. TRI",             color: "bg-orange-100 text-orange-700" },
  chef_filiere_G2E:      { label: "Chef Filière G2E",          color: "bg-green-100 text-green-700" },
  chef_filiere_GC:       { label: "Chef Filière GC",           color: "bg-green-100 text-green-700" },
  chef_filiere_GI:       { label: "Chef Filière GI",           color: "bg-green-100 text-green-700" },
  chef_filiere_ISIC:     { label: "Chef Filière ISIC",         color: "bg-teal-100 text-teal-700" },
  chef_filiere_2ITE:     { label: "Chef Filière 2ITE",         color: "bg-teal-100 text-teal-700" },
  chef_filiere_CCN:      { label: "Chef Filière CCN",          color: "bg-teal-100 text-teal-700" },
  etudiant:              { label: "Étudiant",                  color: "bg-sky-100 text-sky-700" },
};

const ALL_NAV = [
  {
    icon: icons.dashboard,
    label: "Dashboard",
    path: "/dashboard",
    roles: ["super_admin", "directeur_adjoint", "chef_departement", "chef_filiere"],
  },
  {
    icon: icons.students,
    label: "Étudiants",
    path: "/students",
    roles: ["super_admin", "directeur_adjoint", "chef_departement", "chef_filiere"],
  },
  {
    icon: icons.prediction,
    label: "Prédiction",
    path: "/prediction",
    roles: ["super_admin", "directeur_adjoint", "chef_departement", "chef_filiere"],
  },
  {
    icon: icons.batch,
    label: "Prédiction par Lot",
    path: "/batch",
    roles: ["super_admin", "directeur_adjoint", "chef_departement"],
  },
  {
    icon: icons.analysis,
    label: "Analyse",
    path: "/analysis",
    roles: ["super_admin", "directeur_adjoint", "chef_departement", "chef_filiere"],
  },
  {
    icon: icons.users,
    label: "Gestion Utilisateurs",
    path: "/users",
    // ✅ super_admin ajouté
    roles: ["super_admin", "directeur_adjoint", "chef_departement"],
  },
  {
    icon: icons.admin,
    label: "Administration",
    path: "/admin",
    roles: ["super_admin", "directeur_adjoint", "chef_departement", "chef_filiere"],
  },
];

export default function Sidebar({ collapsed, setCollapsed }) {
  const { user, logout, getAllowedFilieres, getDisplayName, getInitials } = useAuth();
  const navigate = useNavigate();

  const allowedFilieres = getAllowedFilieres();
  const roleInfo = ROLE_LABELS[user?.role] || { label: user?.role, color: "bg-gray-100 text-gray-700" };

  const visibleNav = ALL_NAV.filter(item =>
    item.roles.some(r => user?.role?.startsWith(r) || user?.role === r)
  );

  // ✅ Redirige vers /home au lieu de /login
  const handleLogout = () => {
    logout();
    navigate("/home");
  };

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 260 }}
      transition={{ duration: 0.2, ease: "easeInOut" }}
      className="h-screen bg-white border-r border-gray-100 flex flex-col shadow-sm overflow-hidden flex-shrink-0"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-gray-100">
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.15 }}
              className="flex items-center gap-2"
            >
              <img src="/ensa-logo.png" alt="ENSA" className="h-8 w-auto"
                onError={e => { e.target.style.display = "none"; }} />
              <span className="text-sm font-bold text-[#1B3A6B]">PredictEdu</span>
            </motion.div>
          )}
        </AnimatePresence>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors ml-auto"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d={collapsed ? "M13 5l7 7-7 7M5 5l7 7-7 7" : "M11 19l-7-7 7-7m8 14l-7-7 7-7"} />
          </svg>
        </button>
      </div>

      {/* Badge rôle + filières */}
      {!collapsed && (
        <div className="px-4 py-3 border-b border-gray-50">
          <div className={`text-xs font-medium px-2 py-1 rounded-full inline-block ${roleInfo.color}`}>
            {roleInfo.label}
          </div>
          {allowedFilieres && allowedFilieres.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {allowedFilieres.map(f => (
                <span key={f} className="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">
                  {f}
                </span>
              ))}
            </div>
          )}
          {allowedFilieres === null && (
            <p className="text-xs text-gray-400 mt-1">Accès total — toutes filières</p>
          )}
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-0.5 overflow-y-auto">
        {visibleNav.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-150 group ${
                isActive
                  ? "bg-[#1B3A6B] text-white shadow-sm"
                  : "text-gray-500 hover:bg-gray-50 hover:text-gray-700"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <span className={isActive ? "text-white" : "text-gray-400 group-hover:text-gray-600"}>
                  {item.icon}
                </span>
                <AnimatePresence>
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="text-sm font-medium whitespace-nowrap"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User info + logout */}
      <div className="border-t border-gray-100 p-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-[#1B3A6B] flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-bold">
              {getInitials
                ? getInitials()
                : user?.prenom?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "U"}
            </span>
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 min-w-0"
              >
                <p className="text-sm font-medium text-gray-700 truncate">
                  {getDisplayName
                    ? getDisplayName()
                    : `${user?.prenom || ""} ${user?.nom || ""}`.trim() || user?.email}
                </p>
                <p className="text-xs text-gray-400 truncate">{user?.email}</p>
              </motion.div>
            )}
          </AnimatePresence>
          {!collapsed && (
            <button
              onClick={handleLogout}
              className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors flex-shrink-0"
              title="Déconnexion"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </motion.aside>
  );
}