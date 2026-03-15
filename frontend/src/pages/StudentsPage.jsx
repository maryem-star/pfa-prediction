import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Layout from "../components/Layout";
import {
  getStudents, addStudent, updateStudent,
  deleteStudent, importStudents,
} from "../services/studentService";
import { useNavigate } from "react-router-dom";

const FILIERES = ["ISIC", "CCN", "2ITE", "GC", "GI", "G2E"];

const emptyForm = {
  nom: "", prenom: "", cne: "", email: "",
  filiere: "ISIC", annee_etude: 1, absences: 0,
};

// ── Status badge ──────────────────────────────────────────────────────────────
const statusConfig = {
  success: { bg: "#dcfce7", color: "#15803d", label: "Réussite" },
  warning: { bg: "#fef3c7", color: "#b45309", label: "Moyen"    },
  danger:  { bg: "#fee2e2", color: "#b91c1c", label: "À risque" },
};

const getStatus = (student) => {
  if (!student.prediction) return null;
  const p = student.prediction.probabilite_reussite;
  if (p >= 0.85) return "success";
  if (p >= 0.5)  return "warning";
  return "danger";
};

// ── Modal Formulaire ──────────────────────────────────────────────────────────
const StudentModal = ({ student, onClose, onSave }) => {
  const [form, setForm] = useState(student || emptyForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const isEdit = !!student;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await onSave(form);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Erreur lors de la sauvegarde.");
    } finally {
      setLoading(false);
    }
  };

  const inputClass = "w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-800 bg-gray-50 outline-none focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-50 transition-all";
  const labelClass = "block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg border border-gray-100"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <div>
            <h2 className="text-lg font-bold text-gray-800">
              {isEdit ? "Modifier l'étudiant" : "Ajouter un étudiant"}
            </h2>
            <p className="text-xs text-gray-400 mt-0.5">
              {isEdit ? "Modifiez les informations" : "Remplissez le formulaire"}
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Nom</label>
              <input name="nom" value={form.nom} onChange={handleChange} required placeholder="Alaoui" className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Prénom</label>
              <input name="prenom" value={form.prenom} onChange={handleChange} required placeholder="Yassine" className={inputClass} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>CNE</label>
              <input name="cne" value={form.cne} onChange={handleChange} required placeholder="R123456" className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Email</label>
              <input name="email" type="email" value={form.email} onChange={handleChange} placeholder="etudiant@ensa.ma" className={inputClass} />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className={labelClass}>Filière</label>
              <select name="filiere" value={form.filiere} onChange={handleChange} className={inputClass}>
                {FILIERES.map((f) => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
            <div>
              <label className={labelClass}>Année</label>
              <select name="annee_etude" value={form.annee_etude} onChange={handleChange} className={inputClass}>
                {[1, 2, 3].map((a) => <option key={a} value={a}>Année {a}</option>)}
              </select>
            </div>
            <div>
              <label className={labelClass}>Absences</label>
              <input name="absences" type="number" min="0" value={form.absences} onChange={handleChange} className={inputClass} />
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-xl px-3 py-2.5 text-xs text-red-500">
              <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
              Annuler
            </button>
            <button type="submit" disabled={loading}
              className="flex-1 py-2.5 rounded-xl text-sm font-bold text-white transition-all disabled:opacity-60"
              style={{ background: "linear-gradient(135deg, #1e56a0, #2568b5)" }}>
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  Sauvegarde...
                </span>
              ) : isEdit ? "Modifier" : "Ajouter"}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

// ── Confirm Delete Modal ───────────────────────────────────────────────────────
const DeleteModal = ({ student, onClose, onConfirm }) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 border border-gray-100"
    >
      <div className="text-center">
        <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
          <svg className="w-6 h-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </div>
        <h3 className="text-base font-bold text-gray-800 mb-1">Supprimer l'étudiant ?</h3>
        <p className="text-sm text-gray-400 mb-6">
          <strong>{student.prenom} {student.nom}</strong> sera supprimé définitivement.
        </p>
        <div className="flex gap-3">
          <button onClick={onClose}
            className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
            Annuler
          </button>
          <button onClick={onConfirm}
            className="flex-1 py-2.5 rounded-xl text-sm font-bold text-white bg-red-500 hover:bg-red-600 transition-colors">
            Supprimer
          </button>
        </div>
      </div>
    </motion.div>
  </div>
);

// ── Import Modal ──────────────────────────────────────────────────────────────
const ImportModal = ({ onClose, onImport }) => {
  const [filiere, setFiliere] = useState("ISIC");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleImport = async () => {
    if (!file) { setError("Veuillez choisir un fichier."); return; }
    setLoading(true);
    setError("");
    try {
      await onImport(filiere, file);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Erreur lors de l'import.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 border border-gray-100"
      >
        <h2 className="text-lg font-bold text-gray-800 mb-1">Import Excel</h2>
        <p className="text-xs text-gray-400 mb-5">Importer des étudiants depuis un fichier Excel par filière</p>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">Filière</label>
            <select value={filiere} onChange={(e) => setFiliere(e.target.value)}
              className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-800 bg-gray-50 outline-none focus:border-blue-400 transition-all">
              {FILIERES.map((f) => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">Fichier Excel</label>
            <div className="border-2 border-dashed border-gray-200 rounded-xl p-6 text-center hover:border-blue-300 transition-colors cursor-pointer"
              onClick={() => document.getElementById("file-input").click()}>
              {file ? (
                <div>
                  <svg className="w-8 h-8 text-green-500 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm font-medium text-gray-700">{file.name}</p>
                  <p className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              ) : (
                <div>
                  <svg className="w-8 h-8 text-gray-300 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="text-sm text-gray-400">Cliquez pour choisir un fichier</p>
                  <p className="text-xs text-gray-300 mt-1">.xlsx, .xls</p>
                </div>
              )}
              <input id="file-input" type="file" accept=".xlsx,.xls" className="hidden"
                onChange={(e) => setFile(e.target.files[0])} />
            </div>
          </div>

          {error && (
            <div className="text-xs text-red-500 bg-red-50 border border-red-200 rounded-xl px-3 py-2">{error}</div>
          )}

          <div className="flex gap-3">
            <button onClick={onClose}
              className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
              Annuler
            </button>
            <button onClick={handleImport} disabled={loading}
              className="flex-1 py-2.5 rounded-xl text-sm font-bold text-white transition-all disabled:opacity-60"
              style={{ background: "linear-gradient(135deg, #1e56a0, #2568b5)" }}>
              {loading ? "Import en cours..." : "Importer"}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

// ── Main Page ─────────────────────────────────────────────────────────────────
const StudentsPage = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [filterFiliere, setFilterFiliere] = useState("Tous");
  const [modal, setModal] = useState(null); // null | "add" | "edit" | "delete" | "import"
  const [selected, setSelected] = useState(null);
  const [toast, setToast] = useState(null);
  const navigate = useNavigate();

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchStudents = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getStudents();
      setStudents(data);
    } catch (err) {
      setError("Impossible de charger les étudiants. Vérifiez que le backend est lancé.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchStudents(); }, []);

  const filtered = students.filter((s) => {
    const matchSearch = `${s.nom} ${s.prenom} ${s.cne}`.toLowerCase().includes(search.toLowerCase());
    const matchFiliere = filterFiliere === "Tous" || s.filiere === filterFiliere;
    return matchSearch && matchFiliere;
  });

  const handleSave = async (form) => {
    if (selected) {
      await updateStudent(selected.id, form);
      showToast("Étudiant modifié avec succès !");
    } else {
      await addStudent(form);
      showToast("Étudiant ajouté avec succès !");
    }
    await fetchStudents();
  };

  const handleDelete = async () => {
    await deleteStudent(selected.id);
    showToast("Étudiant supprimé.", "error");
    setModal(null);
    setSelected(null);
    await fetchStudents();
  };

  const handleImport = async (filiere, file) => {
    await importStudents(filiere, file);
    showToast(`Import ${filiere} réussi !`);
    await fetchStudents();
  };

  // Export CSV simple
  const handleExport = () => {
    const headers = ["ID", "Nom", "Prénom", "CNE", "Email", "Filière", "Année", "Absences"];
    const rows = filtered.map((s) => [s.id, s.nom, s.prenom, s.cne, s.email || "", s.filiere, s.annee_etude, s.absences]);
    const csv = [headers, ...rows].map((r) => r.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "etudiants.csv"; a.click();
    showToast("Export CSV téléchargé !");
  };

  return (
    <Layout>
      <div className="min-h-full p-6 space-y-5">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Gestion des Étudiants</h1>
            <p className="text-sm text-gray-400 mt-0.5">{students.length} étudiant(s) au total</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setModal("import")}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm font-medium text-gray-600 hover:bg-gray-50 shadow-sm transition-all">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Import Excel
            </button>
            <button onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm font-medium text-gray-600 hover:bg-gray-50 shadow-sm transition-all">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export CSV
            </button>
            <button onClick={() => { setSelected(null); setModal("add"); }}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold text-white shadow-sm transition-all"
              style={{ background: "linear-gradient(135deg, #1e56a0, #2568b5)" }}>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Ajouter
            </button>
            <button onClick={() => navigate(`/students/${student.id}`)}
              className="p-1.5 rounded-lg text-gray-400 hover:text-green-500 hover:bg-green-50 transition-colors">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm flex flex-wrap gap-3 items-center">
          {/* Search */}
          <div className="relative flex-1 min-w-48">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="Rechercher par nom, prénom, CNE..."
              className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-700 bg-gray-50 outline-none focus:border-blue-400 focus:bg-white transition-all" />
          </div>

          {/* Filiere filter */}
          <div className="flex flex-wrap gap-1.5">
            {["Tous", ...FILIERES].map((f) => (
              <button key={f} onClick={() => setFilterFiliere(f)}
                className="px-3 py-1.5 text-xs font-semibold rounded-full border transition-all"
                style={filterFiliere === f
                  ? { background: "#1e56a0", color: "#fff", borderColor: "#1e56a0" }
                  : { background: "#f9fafb", color: "#6b7280", borderColor: "#e5e7eb" }}>
                {f}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="w-8 h-8 border-2 border-blue-200 border-t-blue-500 rounded-full animate-spin" />
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-16 text-center px-4">
              <svg className="w-12 h-12 text-red-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm font-medium text-gray-600">{error}</p>
              <button onClick={fetchStudents} className="mt-3 text-xs text-blue-500 hover:underline">Réessayer</button>
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <svg className="w-12 h-12 text-gray-200 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <p className="text-sm text-gray-400">Aucun étudiant trouvé</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-100" style={{ background: "#f8fafc" }}>
                    {["Étudiant", "CNE", "Filière", "Année", "Absences", "Prédiction", "Actions"].map((h) => (
                      <th key={h} className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wider px-4 py-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <AnimatePresence>
                    {filtered.map((student, i) => {
                      const status = getStatus(student);
                      const cfg = status ? statusConfig[status] : null;
                      return (
                        <motion.tr key={student.id}
                          initial={{ opacity: 0, y: 8 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.03 }}
                          className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0"
                                style={{ background: "linear-gradient(135deg, #1e56a0, #e87722)" }}>
                                {(student.prenom?.[0] || "") + (student.nom?.[0] || "")}
                              </div>
                              <div>
                                <p className="text-sm font-semibold text-gray-800">{student.prenom} {student.nom}</p>
                                <p className="text-xs text-gray-400">{student.email || "—"}</p>
                              </div>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600 font-mono">{student.cne}</td>
                          <td className="px-4 py-3">
                            <span className="text-xs font-semibold px-2.5 py-1 rounded-full"
                              style={{ background: "#eff6ff", color: "#1e56a0" }}>
                              {student.filiere}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">Année {student.annee_etude}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{student.absences ?? "—"}</td>
                          <td className="px-4 py-3">
                            {cfg ? (
                              <span className="text-xs font-semibold px-2.5 py-1 rounded-full"
                                style={{ background: cfg.bg, color: cfg.color }}>
                                {cfg.label}
                              </span>
                            ) : (
                              <span className="text-xs text-gray-300">Non calculé</span>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-1">
                              <button onClick={() => { setSelected(student); setModal("edit"); }}
                                className="p-1.5 rounded-lg text-gray-400 hover:text-blue-500 hover:bg-blue-50 transition-colors">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                              </button>
                              <button onClick={() => { setSelected(student); setModal("delete"); }}
                                className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              </button>
                              <button onClick={() => navigate(`/students/${student.id}`)}
                                className="p-1.5 rounded-lg text-gray-400 hover:text-green-500 hover:bg-green-50 transition-colors"
                                title="Voir profil">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                              </button>
                            </div>
                          </td>
                        </motion.tr>
                      );
                    })}
                  </AnimatePresence>
                </tbody>
              </table>
            </div>
          )}
        </motion.div>

        <p className="text-xs text-gray-400">{filtered.length} étudiant(s) affiché(s)</p>
      </div>

      {/* Modals */}
      <AnimatePresence>
        {(modal === "add" || modal === "edit") && (
          <StudentModal student={modal === "edit" ? selected : null}
            onClose={() => setModal(null)} onSave={handleSave} />
        )}
        {modal === "delete" && selected && (
          <DeleteModal student={selected} onClose={() => setModal(null)} onConfirm={handleDelete} />
        )}
        {modal === "import" && (
          <ImportModal onClose={() => setModal(null)} onImport={handleImport} />
        )}
      </AnimatePresence>

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 20, x: "-50%" }}
            animate={{ opacity: 1, y: 0, x: "-50%" }}
            exit={{ opacity: 0, y: 20, x: "-50%" }}
            className="fixed bottom-6 left-1/2 z-50 px-5 py-3 rounded-xl shadow-lg text-sm font-medium text-white flex items-center gap-2"
            style={{ background: toast.type === "error" ? "#ef4444" : "#1e56a0" }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d={toast.type === "error" ? "M6 18L18 6M6 6l12 12" : "M5 13l4 4L19 7"} />
            </svg>
            {toast.message}
          </motion.div>
        )}
      </AnimatePresence>
    </Layout>
  );
};

export default StudentsPage;