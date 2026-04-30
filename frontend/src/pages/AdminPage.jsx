import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";

// ─── Config périmètre par rôle ─────────────────────────────────────────────────
const PERIMETRE = {
  directeur_adjoint: {
    label: "Directeur Adjoint Pédagogie",
    color: "#1B3A6B",
    bg: "bg-blue-50",
    text: "text-blue-700",
    border: "border-blue-200",
    departements: ["TRI", "STIN"],
    filieres: ["ISIC", "CCN", "2ITE", "G2E", "GI", "GC"],
    acces: "Accès total — toutes filières, tous départements",
  },
  chef_departement_TRI: {
    label: "Chef Département TRI",
    color: "#1B3A6B",
    bg: "bg-blue-50",
    text: "text-blue-700",
    border: "border-blue-200",
    departements: ["TRI"],
    filieres: ["ISIC", "CCN", "2ITE"],
    acces: "Accès département TRI — filières ISIC, CCN, 2ITE",
  },
  chef_departement_STIN: {
    label: "Chef Département STIN",
    color: "#e87722",
    bg: "bg-orange-50",
    text: "text-orange-700",
    border: "border-orange-200",
    departements: ["STIN"],
    filieres: ["G2E", "GI", "GC"],
    acces: "Accès département STIN — filières G2E, GI, GC",
  },
  chef_filiere_ISIC: { label: "Chef Filière ISIC", color: "#3b82f6", bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200", departements: ["TRI"], filieres: ["ISIC"], acces: "Accès filière ISIC uniquement" },
  chef_filiere_CCN:  { label: "Chef Filière CCN",  color: "#8b5cf6", bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-200", departements: ["TRI"], filieres: ["CCN"],  acces: "Accès filière CCN uniquement" },
  chef_filiere_2ITE: { label: "Chef Filière 2ITE", color: "#06b6d4", bg: "bg-cyan-50", text: "text-cyan-700", border: "border-cyan-200", departements: ["TRI"], filieres: ["2ITE"], acces: "Accès filière 2ITE uniquement" },
  chef_filiere_G2E:  { label: "Chef Filière G2E",  color: "#f97316", bg: "bg-orange-50", text: "text-orange-700", border: "border-orange-200", departements: ["STIN"], filieres: ["G2E"], acces: "Accès filière G2E uniquement" },
  chef_filiere_GI:   { label: "Chef Filière GI",   color: "#10b981", bg: "bg-green-50", text: "text-green-700", border: "border-green-200", departements: ["STIN"], filieres: ["GI"],  acces: "Accès filière GI uniquement" },
  chef_filiere_GC:   { label: "Chef Filière GC",   color: "#f59e0b", bg: "bg-yellow-50", text: "text-yellow-700", border: "border-yellow-200", departements: ["STIN"], filieres: ["GC"],  acces: "Accès filière GC uniquement" },
};

const FILIERE_COLORS = {
  ISIC: "#3b82f6", CCN: "#8b5cf6", "2ITE": "#06b6d4",
  G2E: "#f97316", GI: "#10b981", GC: "#f59e0b",
};

// ─── Mocks logs ────────────────────────────────────────────────────────────────
const MOCK_LOGS_CONNEXION = [
  { id: 1,  user: "Mohammed Benali",   role: "chef_departement_TRI",  action: "Connexion",       date: "2025-04-20T08:32:00", ip: "192.168.1.12", status: "success" },
  { id: 2,  user: "Youssef Alaoui",    role: "chef_filiere_ISIC",     action: "Connexion",       date: "2025-04-20T08:45:00", ip: "192.168.1.23", status: "success" },
  { id: 3,  user: "Inconnu",           role: "—",                     action: "Tentative échouée",date: "2025-04-20T09:10:00", ip: "10.0.0.45",    status: "error" },
  { id: 4,  user: "Fatima Zahra",      role: "chef_departement_STIN", action: "Connexion",       date: "2025-04-20T09:15:00", ip: "192.168.1.34", status: "success" },
  { id: 5,  user: "Samira Idrissi",    role: "chef_filiere_G2E",      action: "Connexion",       date: "2025-04-20T10:00:00", ip: "192.168.1.56", status: "success" },
  { id: 6,  user: "Rachid Tazi",       role: "chef_filiere_2ITE",     action: "Déconnexion",     date: "2025-04-20T11:30:00", ip: "192.168.1.78", status: "info" },
  { id: 7,  user: "Inconnu",           role: "—",                     action: "Tentative échouée",date: "2025-04-19T22:05:00", ip: "85.12.34.56",  status: "error" },
  { id: 8,  user: "Khadija Mansouri",  role: "chef_filiere_CCN",      action: "Connexion",       date: "2025-04-19T14:20:00", ip: "192.168.1.90", status: "success" },
];

const MOCK_LOGS_ACTIONS = [
  { id: 1,  user: "Youssef Alaoui",    role: "chef_filiere_ISIC",     action: "Ajout étudiant",           cible: "Mehdi Barka — ISIC",        date: "2025-04-20T08:50:00" },
  { id: 2,  user: "Mohammed Benali",   role: "chef_departement_TRI",  action: "Modification chef filière", cible: "CCN → Rachid Tazi",         date: "2025-04-20T09:05:00" },
  { id: 3,  user: "Fatima Zahra",      role: "chef_departement_STIN", action: "Import étudiants Excel",    cible: "28 étudiants — G2E",        date: "2025-04-20T09:20:00" },
  { id: 4,  user: "Samira Idrissi",    role: "chef_filiere_G2E",      action: "Envoi recommandation",      cible: "Sara Douiri — G2E",         date: "2025-04-20T10:15:00" },
  { id: 5,  user: "Khadija Mansouri",  role: "chef_filiere_CCN",      action: "Prédiction générée",        cible: "Omar Chakir — CCN",         date: "2025-04-20T10:45:00" },
  { id: 6,  user: "Mohammed Benali",   role: "chef_departement_TRI",  action: "Suppression étudiant",      cible: "Ali Hassan — ISIC",         date: "2025-04-19T15:30:00" },
  { id: 7,  user: "Rachid Tazi",       role: "chef_filiere_2ITE",     action: "Modification étudiant",     cible: "Nadia Alami — 2ITE",        date: "2025-04-19T16:00:00" },
  { id: 8,  user: "Samira Idrissi",    role: "chef_filiere_G2E",      action: "Envoi recommandation",      cible: "Khalid Bennis — G2E",       date: "2025-04-19T17:10:00" },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────
function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

function RoleBadge({ role }) {
  const cfg = PERIMETRE[role];
  if (!cfg) return <span className="text-xs text-gray-400">{role || "—"}</span>;
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cfg.bg} ${cfg.text}`}>
      {cfg.label}
    </span>
  );
}

function StatusDot({ status }) {
  if (status === "success") return <span className="w-2 h-2 rounded-full bg-green-400 inline-block" />;
  if (status === "error")   return <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />;
  return <span className="w-2 h-2 rounded-full bg-gray-300 inline-block" />;
}

// ─── Page principale ───────────────────────────────────────────────────────────
export default function AdminPage() {
  const { user, isAdmin, isChefDepartement, isChefFiliere, getAllowedFilieres } = useAuth();

  const [activeTab, setActiveTab] = useState("perimetre");
  const [filterStatus, setFilterStatus] = useState("all");
  const [searchLogs, setSearchLogs] = useState("");

  const perimetre = PERIMETRE[user?.role] || null;
  const allowedFilieres = getAllowedFilieres();
  const visibleFilieres = allowedFilieres === null
    ? ["ISIC", "CCN", "2ITE", "G2E", "GI", "GC"]
    : allowedFilieres;

  // Filtrer logs connexion selon le rôle et la recherche
  const logsConnexion = MOCK_LOGS_CONNEXION.filter(l => {
    const matchSearch = !searchLogs || `${l.user} ${l.action} ${l.ip}`.toLowerCase().includes(searchLogs.toLowerCase());
    const matchStatus = filterStatus === "all" || l.status === filterStatus;
    return matchSearch && matchStatus;
  });

  const logsActions = MOCK_LOGS_ACTIONS.filter(l => {
    const matchSearch = !searchLogs || `${l.user} ${l.action} ${l.cible}`.toLowerCase().includes(searchLogs.toLowerCase());
    // Filtrer selon périmètre : chefs de filière voient uniquement leurs actions
    if (isChefFiliere()) {
      const myFiliere = user.role.replace("chef_filiere_", "");
      return matchSearch && l.cible?.includes(myFiliere);
    }
    if (isChefDepartement()) {
      const myFilieres = allowedFilieres || [];
      return matchSearch && myFilieres.some(f => l.cible?.includes(f));
    }
    return matchSearch;
  });

  const tabs = [
    { id: "perimetre",  label: "Mon périmètre",     icon: "🗺️" },
    { id: "connexions", label: "Logs connexions",    icon: "🔐" },
    { id: "actions",    label: "Logs actions",       icon: "📋" },
  ];

  // Stats rapides
  const statsConnexion = {
    total:   MOCK_LOGS_CONNEXION.length,
    success: MOCK_LOGS_CONNEXION.filter(l => l.status === "success").length,
    errors:  MOCK_LOGS_CONNEXION.filter(l => l.status === "error").length,
  };

  return (
    <Layout>
      <div className="p-6 space-y-6 max-w-5xl">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Administration</h1>
          <p className="text-sm text-gray-500 mt-1">
            Logs système et périmètre d'accès
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === t.id
                  ? "bg-white text-[#1B3A6B] shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>

        {/* ── ONGLET PÉRIMÈTRE ── */}
        {activeTab === "perimetre" && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">

            {/* Carte rôle actuel */}
            {perimetre && (
              <div className={`bg-white rounded-2xl p-6 shadow-sm border ${perimetre.border}`}>
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-white text-lg flex-shrink-0"
                    style={{ backgroundColor: perimetre.color }}>
                    🎓
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h2 className="text-lg font-bold text-gray-800">{perimetre.label}</h2>
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${perimetre.bg} ${perimetre.text}`}>
                        {user?.prenom} {user?.nom}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">{perimetre.acces}</p>
                    <p className="text-xs text-gray-400 mt-1">{user?.email}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Départements accessibles */}
            <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Départements accessibles</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {perimetre?.departements.map(dept => {
                  const isDeptAccessible = perimetre.departements.includes(dept);
                  const deptColor = dept === "TRI" ? "#1B3A6B" : "#e87722";
                  const deptFilieres = dept === "TRI"
                    ? ["ISIC", "CCN", "2ITE"]
                    : ["G2E", "GI", "GC"];
                  return (
                    <div key={dept} className="border border-gray-100 rounded-xl p-4">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white text-sm font-bold"
                          style={{ backgroundColor: deptColor }}>
                          {dept}
                        </div>
                        <div>
                          <p className="text-sm font-bold text-gray-800">Département {dept}</p>
                          <p className="text-xs text-gray-400">
                            {dept === "TRI" ? "Technologies et Réseaux Informatiques" : "Sciences et Technologies de l'Ingénieur"}
                          </p>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {deptFilieres.map(f => {
                          const hasAccess = visibleFilieres.includes(f);
                          return (
                            <span key={f}
                              className={`text-xs px-2.5 py-1 rounded-full font-medium border transition-all ${
                                hasAccess
                                  ? "text-white border-transparent"
                                  : "bg-gray-50 text-gray-300 border-gray-100"
                              }`}
                              style={hasAccess ? { backgroundColor: FILIERE_COLORS[f] } : {}}
                            >
                              {hasAccess ? "✓ " : ""}{f}
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}

                {/* Si directeur adjoint, afficher les 2 départements */}
                {isAdmin() && !perimetre?.departements && (
                  ["TRI", "STIN"].map(dept => (
                    <div key={dept} className="border border-gray-100 rounded-xl p-4">
                      <p className="text-sm font-bold text-gray-800">{dept}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Filières accessibles */}
            <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">
                Filières accessibles
                <span className="ml-2 text-xs font-normal text-gray-400">
                  ({visibleFilieres.length} / 6)
                </span>
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {["ISIC", "CCN", "2ITE", "G2E", "GI", "GC"].map(f => {
                  const hasAccess = visibleFilieres.includes(f);
                  const dept = ["ISIC", "CCN", "2ITE"].includes(f) ? "TRI" : "STIN";
                  return (
                    <div key={f}
                      className={`rounded-xl p-4 border transition-all ${
                        hasAccess ? "border-transparent shadow-sm" : "border-gray-100 opacity-40"
                      }`}
                      style={hasAccess ? { backgroundColor: `${FILIERE_COLORS[f]}15`, borderColor: `${FILIERE_COLORS[f]}30` } : {}}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-base font-bold" style={{ color: hasAccess ? FILIERE_COLORS[f] : "#9ca3af" }}>
                          {f}
                        </span>
                        {hasAccess
                          ? <svg className="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                          : <svg className="w-4 h-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>
                        }
                      </div>
                      <p className="text-xs text-gray-400">Dép. {dept}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        )}

        {/* ── ONGLET LOGS CONNEXIONS ── */}
        {activeTab === "connexions" && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">

            {/* Stats rapides */}
            <div className="grid grid-cols-3 gap-4">
              {[
                { label: "Total connexions", value: statsConnexion.total, color: "text-gray-800", bg: "bg-gray-50" },
                { label: "Réussies", value: statsConnexion.success, color: "text-green-700", bg: "bg-green-50" },
                { label: "Échouées", value: statsConnexion.errors, color: "text-red-700", bg: "bg-red-50" },
              ].map((s, i) => (
                <div key={i} className={`${s.bg} rounded-2xl p-4 border border-gray-100`}>
                  <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
                  <p className="text-xs text-gray-500 mt-1">{s.label}</p>
                </div>
              ))}
            </div>

            {/* Filtres */}
            <div className="flex gap-3 flex-wrap">
              <input
                value={searchLogs} onChange={e => setSearchLogs(e.target.value)}
                placeholder="Rechercher..."
                className="flex-1 min-w-[200px] border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#1B3A6B]/20"
              />
              <select
                value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
                className="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none"
              >
                <option value="all">Tous les statuts</option>
                <option value="success">Réussies</option>
                <option value="error">Échouées</option>
                <option value="info">Info</option>
              </select>
            </div>

            {/* Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-100">
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Statut</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Utilisateur</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Rôle</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Action</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">IP</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {logsConnexion.length === 0 ? (
                      <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400 text-sm">Aucun log trouvé</td></tr>
                    ) : logsConnexion.map(l => (
                      <tr key={l.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <StatusDot status={l.status} />
                            <span className={`text-xs font-medium ${
                              l.status === "success" ? "text-green-600"
                              : l.status === "error" ? "text-red-600"
                              : "text-gray-400"
                            }`}>
                              {l.status === "success" ? "OK" : l.status === "error" ? "Échec" : "Info"}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm font-medium text-gray-800">{l.user}</td>
                        <td className="px-4 py-3"><RoleBadge role={l.role} /></td>
                        <td className="px-4 py-3 text-sm text-gray-600">{l.action}</td>
                        <td className="px-4 py-3 text-xs font-mono text-gray-400">{l.ip}</td>
                        <td className="px-4 py-3 text-xs text-gray-400">{formatDate(l.date)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )}

        {/* ── ONGLET LOGS ACTIONS ── */}
        {activeTab === "actions" && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">

            {/* Recherche */}
            <input
              value={searchLogs} onChange={e => setSearchLogs(e.target.value)}
              placeholder="Rechercher par utilisateur, action, cible..."
              className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#1B3A6B]/20"
            />

            {/* Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-100">
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Utilisateur</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Rôle</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Action</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Cible</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {logsActions.length === 0 ? (
                      <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400 text-sm">Aucun log dans votre périmètre</td></tr>
                    ) : logsActions.map(l => (
                      <tr key={l.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-7 h-7 rounded-full bg-[#1B3A6B]/10 flex items-center justify-center flex-shrink-0">
                              <span className="text-[#1B3A6B] text-xs font-bold">
                                {l.user?.split(" ").map(w => w[0]).join("").slice(0, 2)}
                              </span>
                            </div>
                            <span className="text-sm font-medium text-gray-800">{l.user}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3"><RoleBadge role={l.role} /></td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-1 rounded-lg font-medium ${
                            l.action.includes("Ajout") ? "bg-green-50 text-green-700"
                            : l.action.includes("Suppression") ? "bg-red-50 text-red-700"
                            : l.action.includes("Modification") ? "bg-yellow-50 text-yellow-700"
                            : "bg-blue-50 text-blue-700"
                          }`}>
                            {l.action}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">{l.cible}</td>
                        <td className="px-4 py-3 text-xs text-gray-400">{formatDate(l.date)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Note périmètre */}
            {!isAdmin() && (
              <div className="flex items-start gap-2 p-3 bg-blue-50 rounded-xl border border-blue-100">
                <svg className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-xs text-blue-700">
                  Vous visualisez uniquement les actions effectuées dans votre périmètre ({visibleFilieres.join(", ")}).
                </p>
              </div>
            )}
          </motion.div>
        )}

      </div>
    </Layout>
  );
}