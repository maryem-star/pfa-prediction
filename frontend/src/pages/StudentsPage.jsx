import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

const FILIERES = ["ISIC", "CCN", "2ITE", "GC", "GI", "G2E"];

export default function StudentsPage() {
  const { getAllowedFilieres, user } = useAuth();
  const navigate = useNavigate();
  const allowedFilieres = getAllowedFilieres();
  const visibleFilieres = allowedFilieres === null ? FILIERES : allowedFilieres;

  const canCRUD = user?.role === "super_admin";

  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterFiliere, setFilterFiliere] = useState("all");
  const [modal, setModal] = useState(null);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({
    nom: "", prenom: "", cne: "", email: "",
    filiere: visibleFilieres[0] || "ISIC", annee: 1
  });
  const [toast, setToast] = useState(null);

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const res = await api.get("/v2/students/");
      setStudents(res.data);
    } catch {
      setStudents(Array.from({ length: 18 }, (_, i) => ({
        id: i + 1,
        nom: ["Alaoui", "Benali", "Chakir", "Douiri", "El Fassi", "Fassi"][i % 6],
        prenom: ["Yassine", "Nadia", "Omar", "Sara", "Khalid", "Amine"][i % 6],
        cne: `R${100000 + i}`,
        email: `etudiant${i + 1}@ensa.ma`,
        filiere: visibleFilieres[i % visibleFilieres.length] || "ISIC",
        annee: (i % 3) + 1,
      })));
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchStudents(); }, []);

  const showToast = (msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleAdd = async () => {
    try {
      await api.post("/students/", { ...form, password: "student123", role: "etudiant" });
      showToast("Étudiant ajouté avec succès");
      fetchStudents();
      setModal(null);
    } catch { showToast("Erreur lors de l'ajout", "error"); }
  };

  const handleEdit = async () => {
    try {
      await api.put(`/students/${selected.id}`, form);
      showToast("Étudiant modifié");
      fetchStudents();
      setModal(null);
    } catch { showToast("Erreur lors de la modification", "error"); }
  };

  const handleDelete = async () => {
    try {
      await api.delete(`/students/${selected.id}`);
      showToast("Étudiant supprimé");
      fetchStudents();
      setModal(null);
    } catch { showToast("Erreur lors de la suppression", "error"); }
  };

  // FIX: navigate with student data in state so the profile page
  // always shows the correct student even if the API call fails
  const goToStats = (s) => {
    navigate(`/students/${s.id}/stats`, { state: { student: s } });
  };

  const filtered = students.filter(s => {
    const q = search.toLowerCase();
    const matchSearch = !search ||
      s.nom?.toLowerCase().includes(q) ||
      s.prenom?.toLowerCase().includes(q) ||
      s.cne?.toLowerCase().includes(q);
    const matchFiliere = filterFiliere === "all" || s.filiere === filterFiliere;
    return matchSearch && matchFiliere;
  });

  return (
    <Layout>
      <div className="p-6 space-y-5">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Gestion des Étudiants</h1>
            <p className="text-sm text-gray-500 mt-1">
              {students.length} étudiant(s) dans votre périmètre
            </p>
          </div>
          {canCRUD && (
            <button
              onClick={() => {
                setForm({ nom: "", prenom: "", cne: "", email: "", filiere: visibleFilieres[0] || "ISIC", annee: 1 });
                setModal("add");
              }}
              className="flex items-center gap-2 bg-[#1B3A6B] text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-[#152d54] transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Ajouter
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="flex gap-3 flex-wrap">
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Rechercher par nom, prénom, CNE..."
            className="flex-1 min-w-[200px] border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#1B3A6B]/20"
          />
          <select
            value={filterFiliere} onChange={e => setFilterFiliere(e.target.value)}
            className="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none"
          >
            <option value="all">Toutes les filières</option>
            {visibleFilieres.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>

        {/* Table */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Étudiant</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">CNE</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Filière</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Année</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-400 text-sm">
                      Chargement...
                    </td>
                  </tr>
                ) : filtered.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-400 text-sm">
                      Aucun étudiant trouvé
                    </td>
                  </tr>
                ) : filtered.map(s => (
                  <tr
                    key={s.id}
                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => goToStats(s)}  // FIX: pass the full student object
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-[#1B3A6B]/10 flex items-center justify-center flex-shrink-0">
                          <span className="text-[#1B3A6B] text-xs font-bold">
                            {s.prenom?.[0]}{s.nom?.[0]}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-800">{s.prenom} {s.nom}</p>
                          <p className="text-xs text-gray-400">{s.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{s.cne}</td>
                    <td className="px-4 py-3">
                      <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-full font-medium">
                        {s.filiere}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {s.annee ? `${s.annee}ème année` : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1" onClick={e => e.stopPropagation()}>
                        <button
                          onClick={() => goToStats(s)}  // FIX: pass the full student object
                          title="Voir statistiques"
                          className="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                          </svg>
                        </button>
                        {canCRUD && (
                          <button
                            onClick={() => {
                              setSelected(s);
                              setForm({ nom: s.nom, prenom: s.prenom, cne: s.cne, email: s.email || "", filiere: s.filiere, annee: s.annee || 1 });
                              setModal("edit");
                            }}
                            title="Modifier"
                            className="p-1.5 rounded-lg text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                        )}
                        {canCRUD && (
                          <button
                            onClick={() => { setSelected(s); setModal("delete"); }}
                            title="Supprimer"
                            className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 40 }}
            className={`fixed bottom-6 right-6 px-4 py-3 rounded-xl shadow-lg text-sm font-medium text-white z-50 ${
              toast.type === "error" ? "bg-red-500" : "bg-green-500"
            }`}
          >
            {toast.msg}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal Ajouter / Modifier */}
      <AnimatePresence>
        {(modal === "add" || modal === "edit") && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div initial={{ scale: 0.95, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95 }}
              className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl">
              <h2 className="text-lg font-bold text-gray-800 mb-4">
                {modal === "add" ? "Ajouter un étudiant" : "Modifier l'étudiant"}
              </h2>
              <div className="space-y-3">
                {[
                  { key: "nom", label: "Nom" },
                  { key: "prenom", label: "Prénom" },
                  { key: "cne", label: "CNE" },
                  { key: "email", label: "Email" },
                ].map(f => (
                  <input key={f.key} placeholder={f.label} value={form[f.key]}
                    onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                    className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#1B3A6B]/20" />
                ))}
                <select value={form.filiere} onChange={e => setForm({ ...form, filiere: e.target.value })}
                  className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none">
                  {FILIERES.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
                <select value={form.annee} onChange={e => setForm({ ...form, annee: +e.target.value })}
                  className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none">
                  {[1, 2, 3].map(a => <option key={a} value={a}>{a}ème année</option>)}
                </select>
              </div>
              <div className="flex gap-3 mt-5">
                <button onClick={() => setModal(null)}
                  className="flex-1 border border-gray-200 rounded-xl py-2.5 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                  Annuler
                </button>
                <button onClick={modal === "add" ? handleAdd : handleEdit}
                  className="flex-1 bg-[#1B3A6B] text-white rounded-xl py-2.5 text-sm font-medium hover:bg-[#152d54] transition-colors">
                  {modal === "add" ? "Ajouter" : "Sauvegarder"}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal Supprimer */}
      <AnimatePresence>
        {modal === "delete" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }}
              className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl text-center">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-lg font-bold text-gray-800">Supprimer l'étudiant ?</h2>
              <p className="text-sm text-gray-500 mt-1">
                {selected?.prenom} {selected?.nom} sera supprimé définitivement.
              </p>
              <div className="flex gap-3 mt-5">
                <button onClick={() => setModal(null)}
                  className="flex-1 border border-gray-200 rounded-xl py-2.5 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                  Annuler
                </button>
                <button onClick={handleDelete}
                  className="flex-1 bg-red-500 text-white rounded-xl py-2.5 text-sm font-medium hover:bg-red-600 transition-colors">
                  Supprimer
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </Layout>
  );
}