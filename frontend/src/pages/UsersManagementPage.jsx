import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

// ─── Config départements & filières ───────────────────────────────────────────
const DEPARTEMENTS = {
  TRI: {
    label: "TRI",
    fullName: "Technologies et Réseaux Informatiques",
    color: "#1B3A6B",
    bg: "bg-blue-50",
    text: "text-blue-700",
    border: "border-blue-200",
    filieres: [
      { code: "ISIC", label: "ISIC", fullName: "Ingénierie en Systèmes d'Information et de Communication" },
      { code: "CCN",  label: "CCN",  fullName: "Cybersécurité & Confiance Numérique" },
      { code: "2ITE", label: "2ITE", fullName: "Ingénierie Informatique et Technologies Émergentes" },
    ],
  },
  STIN: {
    label: "STIN",
    fullName: "Sciences et Technologies de l'Ingénieur",
    color: "#e87722",
    bg: "bg-orange-50",
    text: "text-orange-700",
    border: "border-orange-200",
    filieres: [
      { code: "G2E", label: "G2E", fullName: "Génie Énergétique et Électrique" },
      { code: "GI",  label: "GI",  fullName: "Génie Industriel" },
      { code: "GC",  label: "GC",  fullName: "Génie Civil" },
    ],
  },
};

// ─── Mocks (remplacer par vrais appels API quand backend prêt) ─────────────────
const MOCK_CHEFS_DEPT = [
  { id: 10, prenom: "Mohammed", nom: "Benali", email: "m.benali@ensa.ma", role: "chef_departement_TRI",  departement: "TRI" },
  { id: 11, prenom: "Fatima",   nom: "Zahra",  email: "f.zahra@ensa.ma",  role: "chef_departement_STIN", departement: "STIN" },
];

const MOCK_CHEFS_FILIERE = [
  { id: 20, prenom: "Youssef",  nom: "Alaoui",  email: "y.alaoui@ensa.ma",  role: "chef_filiere_ISIC", filiere: "ISIC", departement: "TRI"  },
  { id: 21, prenom: "Khadija",  nom: "Mansouri",email: "k.mansouri@ensa.ma", role: "chef_filiere_CCN",  filiere: "CCN",  departement: "TRI"  },
  { id: 22, prenom: "Rachid",   nom: "Tazi",    email: "r.tazi@ensa.ma",    role: "chef_filiere_2ITE", filiere: "2ITE", departement: "TRI"  },
  { id: 23, prenom: "Samira",   nom: "Idrissi", email: "s.idrissi@ensa.ma", role: "chef_filiere_G2E",  filiere: "G2E",  departement: "STIN" },
  { id: 24, prenom: "Omar",     nom: "Chakir",  email: "o.chakir@ensa.ma",  role: "chef_filiere_GI",   filiere: "GI",   departement: "STIN" },
  { id: 25, prenom: "Nadia",    nom: "El Fassi",email: "n.elfassi@ensa.ma", role: "chef_filiere_GC",   filiere: "GC",   departement: "STIN" },
];

// Tous les enseignants disponibles (pour picker)
const MOCK_ENSEIGNANTS = [
  { id: 30, prenom: "Hassan",   nom: "Bouchta",  email: "h.bouchta@ensa.ma"  },
  { id: 31, prenom: "Laila",    nom: "Chraibi",  email: "l.chraibi@ensa.ma"  },
  { id: 32, prenom: "Amine",    nom: "Douiri",   email: "a.douiri@ensa.ma"   },
  { id: 33, prenom: "Zineb",    nom: "Elhilali", email: "z.elhilali@ensa.ma" },
  { id: 34, prenom: "Karim",    nom: "Fennich",  email: "k.fennich@ensa.ma"  },
  { id: 35, prenom: "Meryem",   nom: "Guessous", email: "m.guessous@ensa.ma" },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────
function initials(prenom, nom) {
  return `${prenom?.[0] ?? ""}${nom?.[0] ?? ""}`.toUpperCase();
}

function Avatar({ prenom, nom, color = "#1B3A6B", size = "w-10 h-10" }) {
  return (
    <div className={`${size} rounded-full flex items-center justify-center flex-shrink-0 text-white text-sm font-bold`}
      style={{ backgroundColor: color }}>
      {initials(prenom, nom)}
    </div>
  );
}

// ─── Modal de changement ───────────────────────────────────────────────────────
function ChangeChefModal({ type, target, enseignants, onClose, onSave }) {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);

  const filtered = enseignants.filter(e => {
    const q = search.toLowerCase();
    return `${e.prenom} ${e.nom} ${e.email}`.toLowerCase().includes(q);
  });

  const handleSave = async () => {
    if (!selected) return;
    setLoading(true);
    await onSave(selected);
    setLoading(false);
  };

  const title = type === "departement"
    ? `Changer le chef du département ${target}`
    : `Changer le chef de la filière ${target}`;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95 }}
          onClick={e => e.stopPropagation()}
          className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl"
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-5">
            <div>
              <h2 className="text-lg font-bold text-gray-800">{title}</h2>
              <p className="text-sm text-gray-500 mt-1">Sélectionnez un enseignant pour ce poste</p>
            </div>
            <button onClick={onClose} className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Search */}
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Rechercher un enseignant..."
            className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-[#1B3A6B]/20"
          />

          {/* List */}
          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {filtered.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">Aucun enseignant trouvé</p>
            ) : filtered.map(e => (
              <button
                key={e.id}
                onClick={() => setSelected(e)}
                className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all text-left ${
                  selected?.id === e.id
                    ? "bg-[#1B3A6B] text-white"
                    : "hover:bg-gray-50 border border-gray-100"
                }`}
              >
                <Avatar prenom={e.prenom} nom={e.nom}
                  color={selected?.id === e.id ? "#ffffff30" : "#1B3A6B"}
                  size="w-8 h-8"
                />
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${selected?.id === e.id ? "text-white" : "text-gray-800"}`}>
                    {e.prenom} {e.nom}
                  </p>
                  <p className={`text-xs truncate ${selected?.id === e.id ? "text-white/70" : "text-gray-400"}`}>
                    {e.email}
                  </p>
                </div>
                {selected?.id === e.id && (
                  <svg className="w-4 h-4 text-white flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-5">
            <button onClick={onClose}
              className="flex-1 border border-gray-200 rounded-xl py-2.5 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
              Annuler
            </button>
            <button onClick={handleSave} disabled={!selected || loading}
              className="flex-1 bg-[#1B3A6B] text-white rounded-xl py-2.5 text-sm font-medium hover:bg-[#152d54] transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2">
              {loading
                ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                : "Confirmer le changement"
              }
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// ─── Card Chef Département ─────────────────────────────────────────────────────
function ChefDeptCard({ dept, chef, onChangeClick }) {
  const cfg = DEPARTEMENTS[dept];
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden"
    >
      {/* Dept header */}
      <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-3"
        style={{ background: `linear-gradient(135deg, ${cfg.color}10, ${cfg.color}05)` }}>
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
          style={{ backgroundColor: cfg.color }}>
          {dept}
        </div>
        <div>
          <p className="text-sm font-bold text-gray-800">Département {cfg.label}</p>
          <p className="text-xs text-gray-500">{cfg.fullName}</p>
        </div>
      </div>

      {/* Chef info */}
      <div className="p-5">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Chef de département</p>
        {chef ? (
          <div className="flex items-center gap-4">
            <Avatar prenom={chef.prenom} nom={chef.nom} color={cfg.color} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-800">{chef.prenom} {chef.nom}</p>
              <p className="text-xs text-gray-400 truncate">{chef.email}</p>
              <span className={`mt-1 inline-block text-xs px-2 py-0.5 rounded-full font-medium ${cfg.bg} ${cfg.text}`}>
                Chef Dép. {dept}
              </span>
            </div>
            <button
              onClick={() => onChangeClick(dept, chef)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium text-white transition-colors hover:opacity-90 flex-shrink-0"
              style={{ backgroundColor: cfg.color }}
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              Changer
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-400 italic">Aucun chef assigné</p>
            <button onClick={() => onChangeClick(dept, null)}
              className="text-xs font-medium text-white px-3 py-2 rounded-xl"
              style={{ backgroundColor: cfg.color }}>
              Assigner
            </button>
          </div>
        )}
      </div>

      {/* Filières list */}
      <div className="px-5 pb-5">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Filières</p>
        <div className="flex flex-wrap gap-2">
          {cfg.filieres.map(f => (
            <span key={f.code}
              className={`text-xs px-2.5 py-1 rounded-full font-medium ${cfg.bg} ${cfg.text} border ${cfg.border}`}>
              {f.label}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

// ─── Card Chef Filière ─────────────────────────────────────────────────────────
function ChefFiliereCard({ filiere, chef, onChangeClick, deptColor }) {
  const deptCfg = Object.values(DEPARTEMENTS).find(d => d.filieres.some(f => f.code === filiere.code));
  const color = deptColor || deptCfg?.color || "#1B3A6B";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5"
    >
      {/* Filière badge */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold"
            style={{ backgroundColor: color }}>
            {filiere.code.slice(0, 2)}
          </div>
          <div>
            <p className="text-sm font-bold text-gray-800">{filiere.label}</p>
            <p className="text-xs text-gray-400 max-w-[180px] truncate">{filiere.fullName}</p>
          </div>
        </div>
      </div>

      {/* Chef */}
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Chef de filière</p>
      {chef ? (
        <div className="flex items-center gap-3">
          <Avatar prenom={chef.prenom} nom={chef.nom} color={color} size="w-9 h-9" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-800">{chef.prenom} {chef.nom}</p>
            <p className="text-xs text-gray-400 truncate">{chef.email}</p>
          </div>
          <button
            onClick={() => onChangeClick(filiere.code, chef)}
            className="p-2 rounded-xl text-gray-400 hover:text-white transition-colors flex-shrink-0"
            style={{ "--hover-bg": color }}
            onMouseEnter={e => { e.currentTarget.style.backgroundColor = color; e.currentTarget.style.color = "white"; }}
            onMouseLeave={e => { e.currentTarget.style.backgroundColor = ""; e.currentTarget.style.color = ""; }}
            title="Changer le chef de filière"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-400 italic">Non assigné</p>
          <button onClick={() => onChangeClick(filiere.code, null)}
            className="text-xs font-medium text-white px-3 py-1.5 rounded-lg"
            style={{ backgroundColor: color }}>
            Assigner
          </button>
        </div>
      )}
    </motion.div>
  );
}

// ─── Page principale ───────────────────────────────────────────────────────────
export default function UsersManagementPage() {
  const { user, isAdmin, isChefDepartement } = useAuth();

  const [chefsDept, setChefsDept]       = useState(MOCK_CHEFS_DEPT);
  const [chefsFiliere, setChefsFiliere] = useState(MOCK_CHEFS_FILIERE);
  const [enseignants]                   = useState(MOCK_ENSEIGNANTS);
  const [modal, setModal]               = useState(null); // { type, target, current }
  const [toast, setToast]               = useState(null);

  // Quel département gère cet utilisateur ?
  const visibleDepts = (isAdmin() || isChefDepartement())
    ? (isChefDepartement() ? [myDept] : ["TRI", "STIN"])
    : [];

  // Filières visibles selon le rôle
  
  const showToast = (msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  // ── Changer chef département (directeur_adjoint seulement) ──────────────────
  const handleChangeChefDept = async (nouvelEnseignant) => {
    const dept = modal.target;
    try {
      // TODO: await api.put(`/users/chef-departement/${dept}`, { user_id: nouvelEnseignant.id });
      setChefsDept(prev => prev.map(c =>
        c.departement === dept
          ? { ...c, ...nouvelEnseignant, role: `chef_departement_${dept}`, departement: dept }
          : c
      ));
      showToast(`Chef du département ${dept} mis à jour avec succès`);
    } catch {
      showToast("Erreur lors de la mise à jour", "error");
    }
    setModal(null);
  };

  // ── Changer chef filière (chef_departement ou directeur_adjoint) ────────────
  const handleChangeChefFiliere = async (nouvelEnseignant) => {
    const filiere = modal.target;
    try {
      // TODO: await api.put(`/users/chef-filiere/${filiere}`, { user_id: nouvelEnseignant.id });
      setChefsFiliere(prev => prev.map(c =>
        c.filiere === filiere
          ? { ...c, ...nouvelEnseignant, role: `chef_filiere_${filiere}`, filiere }
          : c
      ));
      showToast(`Chef de la filière ${filiere} mis à jour avec succès`);
    } catch {
      showToast("Erreur lors de la mise à jour", "error");
    }
    setModal(null);
  };

  const pageTitle = isAdmin()
    ? "Gestion des utilisateurs"
    : `Gestion des chefs de filière — Département ${myDept}`;

  const pageSubtitle = isAdmin()
    ? "Gérez les chefs de département et de filière"
    : `Gérez les chefs de filière de votre département`;

  return (
    <Layout>
      <div className="p-6 space-y-8 max-w-5xl">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-800">{pageTitle}</h1>
          <p className="text-sm text-gray-500 mt-1">{pageSubtitle}</p>
        </div>

        {/* ── SECTION CHEFS DE DÉPARTEMENT (directeur_adjoint uniquement) ── */}
        {user?.role === "super_admin" && ( 
          <section className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-1 h-6 rounded-full bg-[#1B3A6B]" />
              <h2 className="text-base font-bold text-gray-700">Chefs de département</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {["TRI", "STIN"].map(dept => (
                <ChefDeptCard
                  key={dept}
                  dept={dept}
                  chef={chefsDept.find(c => c.departement === dept)}
                  onChangeClick={(d, current) => setModal({ type: "departement", target: d, current })}
                />
              ))}
            </div>
          </section>
        )}

        {/* ── SECTION CHEFS DE FILIÈRE ── */}
        {visibleDepts.map(dept => {
          const cfg = DEPARTEMENTS[dept];
          return (
            <section key={dept} className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-1 h-6 rounded-full" style={{ backgroundColor: cfg.color }} />
                <h2 className="text-base font-bold text-gray-700">
                  Chefs de filière — Département {dept}
                </h2>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${cfg.bg} ${cfg.text}`}>
                  {cfg.filieres.length} filières
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {cfg.filieres.map(filiere => (
                  <ChefFiliereCard
                    key={filiere.code}
                    filiere={filiere}
                    chef={chefsFiliere.find(c => c.filiere === filiere.code)}
                    deptColor={cfg.color}
                    onChangeClick={(code, current) => setModal({ type: "filiere", target: code, current })}
                  />
                ))}
              </div>
            </section>
          );
        })}
      </div>

      {/* Modal */}
      {modal && (
        <ChangeChefModal
          type={modal.type}
          target={modal.target}
          enseignants={enseignants}
          onClose={() => setModal(null)}
          onSave={modal.type === "departement" ? handleChangeChefDept : handleChangeChefFiliere}
        />
      )}

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 40 }}
            className={`fixed bottom-6 right-6 px-4 py-3 rounded-xl shadow-lg text-sm font-medium text-white z-50 flex items-center gap-2 ${
              toast.type === "error" ? "bg-red-500" : "bg-green-500"
            }`}
          >
            {toast.type === "error"
              ? <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              : <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
            }
            {toast.msg}
          </motion.div>
        )}
      </AnimatePresence>
    </Layout>
  );
}