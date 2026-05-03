import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer, PieChart, Pie } from "recharts";
import Layout from "../components/Layout";
import api from "../services/api";

// ── Config ────────────────────────────────────────────────────────────────────
const STATUS_CONFIG = {
  VERT:  { label: "Réussite",  color: "#16a34a", bg: "#f0fdf4", border: "#bbf7d0", badgeBg: "#dcfce7", badgeColor: "#15803d" },
  JAUNE: { label: "Moyen",     color: "#d97706", bg: "#fffbeb", border: "#fde68a", badgeBg: "#fef3c7", badgeColor: "#b45309" },
  ROUGE: { label: "À risque",  color: "#dc2626", bg: "#fff1f2", border: "#fecaca", badgeBg: "#fee2e2", badgeColor: "#b91c1c" },
};

const MODELES = ["RandomForest", "SVM", "LogisticRegression"];
const MODELE_LABELS = { RandomForest: "Random Forest", SVM: "SVM", LogisticRegression: "Régression Logistique" };

const CustomTooltip = ({ active, payload }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs shadow-lg">
        <p style={{ color: payload[0].fill }}>{payload[0].name}: <strong>{payload[0].value}</strong></p>
      </div>
    );
  }
  return null;
};

// ── CSV Template download ─────────────────────────────────────────────────────
const downloadTemplate = () => {
  const headers = [
    "Nom", "Prenom", "Absences_S1", "Mathematiques_1", "Algorithmique_Prog",
    "Architecture_Ord", "Electronique_Num", "Reseaux_Info_1", "Anglais_Tech_1",
    "Francais_Pro_1", "Absences_S2", "Mathematiques_2",
    "Structures_Donnees", "Systemes_Exploitation", "Bases_Donnees",
    "Reseaux_Info_2", "Anglais_Tech_2", "Francais_Pro_2", "PFA_2",
    "Modules_Non_Valides", "Redoublant"
  ].join(",");
  const example = "Dupont,Marie,2,14.5,15,12,11.5,13,16,14,3,15,14,13.5,16,14.5,15.5,14,16,0,0";
  const csv = `${headers}\n${example}`;
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "template_prediction.csv"; a.click();
};

// ── Export results CSV ────────────────────────────────────────────────────────
const exportResults = (results, model) => {
  const headers = ["Student ID", "Modèle", "Label", "Probabilité", "Statut", "Note Prédite"];
  const rows = results.map((r) => [
    r.student_id, model,
    r.label || "", r.probabilite || "",
    r.statut_couleur || "", r.note_predite || ""
  ]);
  const csv = [headers, ...rows].map((r) => r.join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = `predictions_${model}_${Date.now()}.csv`; a.click();
};

// ── Main ──────────────────────────────────────────────────────────────────────
const BatchPredictionPage = () => {
  const [file, setFile] = useState(null);
  const [selectedModel, setSelectedModel] = useState("RandomForest");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [filterStatus, setFilterStatus] = useState("Tous");
  const fileRef = useRef(null);

  const handleFile = (f) => {
    if (!f) return;
    if (!f.name.endsWith(".csv")) { setError("Veuillez choisir un fichier CSV."); return; }
    setFile(f);
    setError("");
    setDone(false);
    setResults([]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const handlePredict = async () => {
    if (!file) { setError("Veuillez choisir un fichier CSV."); return; }
    setLoading(true);
    setError("");
    setResults([]);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("modele", selectedModel);

      const res = await api.post("/predictions/batch", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const data = Array.isArray(res.data) ? res.data : res.data.predictions || [];
      setResults(data);
      setDone(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Erreur lors de la prédiction. Vérifiez le format du fichier.");
    } finally {
      setLoading(false);
    }
  };

  // Stats
  const stats = {
    VERT:  results.filter((r) => r.statut_couleur === "VERT").length,
    JAUNE: results.filter((r) => r.statut_couleur === "JAUNE").length,
    ROUGE: results.filter((r) => r.statut_couleur === "ROUGE").length,
  };

  const pieData = [
    { name: "Réussite", value: stats.VERT,  fill: "#16a34a" },
    { name: "Moyen",    value: stats.JAUNE, fill: "#d97706" },
    { name: "À risque", value: stats.ROUGE, fill: "#dc2626" },
  ].filter((d) => d.value > 0);

  const filtered = filterStatus === "Tous"
    ? results
    : results.filter((r) => r.statut_couleur === filterStatus);

  return (
    <Layout>
      <div className="min-h-full p-6 space-y-5">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-2xl font-bold text-gray-800">Prédiction par Lot</h1>
          <p className="text-sm text-gray-400 mt-0.5">Uploadez un fichier CSV pour prédire la réussite de plusieurs étudiants</p>
        </motion.div>

        {/* Upload + Model selection */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-4">

          {/* Drop zone */}
          <div className="lg:col-span-2 bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-gray-700">Fichier CSV</h2>
              <button onClick={downloadTemplate}
                className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 transition-colors">
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Télécharger le modèle CSV
              </button>
            </div>

            {/* Drop area */}
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileRef.current?.click()}
              className="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all hover:border-blue-400 hover:bg-blue-50"
              style={{ borderColor: file ? "#16a34a" : "#e5e7eb" }}
            >
              {file ? (
                <div>
                  <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-sm font-semibold text-gray-700">{file.name}</p>
                  <p className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                  <button onClick={(e) => { e.stopPropagation(); setFile(null); setDone(false); setResults([]); }}
                    className="mt-2 text-xs text-red-400 hover:text-red-600">Supprimer</button>
                </div>
              ) : (
                <div>
                  <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <p className="text-sm text-gray-500">Glissez-déposez votre fichier CSV ici</p>
                  <p className="text-xs text-gray-300 mt-1">ou cliquez pour choisir</p>
                </div>
              )}
              <input ref={fileRef} type="file" accept=".csv" className="hidden"
                onChange={(e) => handleFile(e.target.files[0])} />
            </div>
          </div>

          {/* Model + Action */}
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm flex flex-col gap-4">
            <div>
              <h2 className="text-sm font-semibold text-gray-700 mb-3">Modèle ML</h2>
              <div className="space-y-2">
                {MODELES.map((m) => (
                  <button key={m} onClick={() => setSelectedModel(m)}
                    className="w-full flex items-center gap-3 p-3 rounded-xl border-2 transition-all text-left"
                    style={{
                      borderColor: selectedModel === m ? "#1e56a0" : "#e5e7eb",
                      background: selectedModel === m ? "#eff6ff" : "#fff",
                    }}>
                    <div className="w-3 h-3 rounded-full border-2 flex items-center justify-center shrink-0"
                      style={{ borderColor: selectedModel === m ? "#1e56a0" : "#d1d5db" }}>
                      {selectedModel === m && <div className="w-1.5 h-1.5 rounded-full bg-blue-600" />}
                    </div>
                    <span className="text-xs font-medium" style={{ color: selectedModel === m ? "#1e56a0" : "#6b7280" }}>
                      {MODELE_LABELS[m]}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <button onClick={handlePredict} disabled={!file || loading}
              className="w-full py-3 rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-auto"
              style={{ background: "linear-gradient(135deg, #1e56a0, #2568b5)" }}>
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  Analyse en cours...
                </span>
              ) : "Lancer la prédiction"}
            </button>
          </div>
        </motion.div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-500 flex items-center gap-2">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        {/* Results */}
        <AnimatePresence>
          {done && results.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="space-y-4">

              {/* Summary cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { label: "Total analysés", value: results.length, color: "#1e56a0", bg: "#eff6ff" },
                  { label: "Réussite", value: stats.VERT, color: "#16a34a", bg: "#f0fdf4" },
                  { label: "Moyen", value: stats.JAUNE, color: "#d97706", bg: "#fffbeb" },
                  { label: "À risque", value: stats.ROUGE, color: "#dc2626", bg: "#fff1f2" },
                ].map((s) => (
                  <div key={s.label} className="rounded-xl p-4 text-center border"
                    style={{ background: s.bg, borderColor: s.color + "33" }}>
                    <p className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</p>
                    <p className="text-xs text-gray-500 mt-1">{s.label}</p>
                  </div>
                ))}
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Répartition des prédictions</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie data={pieData} cx="50%" cy="50%" outerRadius={75} dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                        {pieData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                      </Pie>
                      <Tooltip content={<CustomTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Distribution par statut</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={[
                      { name: "Réussite", value: stats.VERT,  fill: "#16a34a" },
                      { name: "Moyen",    value: stats.JAUNE, fill: "#d97706" },
                      { name: "À risque", value: stats.ROUGE, fill: "#dc2626" },
                    ]} barSize={50}>
                      <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                      <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
                      <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                        {[{ fill: "#16a34a" }, { fill: "#d97706" }, { fill: "#dc2626" }].map((entry, i) => (
                          <Cell key={i} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Results table */}
              <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
                <div className="flex flex-wrap items-center justify-between gap-3 p-5 border-b border-gray-100">
                  <h3 className="text-sm font-semibold text-gray-700">
                    Résultats — {MODELE_LABELS[selectedModel]}
                  </h3>
                  <div className="flex items-center gap-2">
                    {/* Filter */}
                    <div className="flex gap-1.5">
                      {["Tous", "VERT", "JAUNE", "ROUGE"].map((s) => (
                        <button key={s} onClick={() => setFilterStatus(s)}
                          className="px-3 py-1 text-xs font-semibold rounded-full border transition-all"
                          style={filterStatus === s
                            ? { background: s === "Tous" ? "#1e56a0" : STATUS_CONFIG[s]?.color, color: "#fff", borderColor: "transparent" }
                            : { background: "#f9fafb", color: "#6b7280", borderColor: "#e5e7eb" }}>
                          {s === "Tous" ? "Tous" : STATUS_CONFIG[s]?.label}
                        </button>
                      ))}
                    </div>
                    {/* Export */}
                    <button onClick={() => exportResults(results, selectedModel)}
                      className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 transition-colors">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Export CSV
                    </button>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr style={{ background: "#f8fafc" }}>
                        {["Student ID", "Label", "Probabilité", "Note Prédite", "Statut"].map((h) => (
                          <th key={h} className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wider px-4 py-3">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {filtered.map((r, i) => {
                        const cfg = STATUS_CONFIG[r.statut_couleur];
                        return (
                          <motion.tr key={i}
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.02 }}
                            className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                            <td className="px-4 py-3 text-sm font-mono text-gray-700">{r.student_id}</td>
                            <td className="px-4 py-3 text-sm text-gray-700">{r.label || "—"}</td>
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden" style={{ width: 60 }}>
                                  <div className="h-full rounded-full" style={{ width: `${Math.round((r.probabilite || 0) * 100)}%`, background: cfg?.color }} />
                                </div>
                                <span className="text-sm font-semibold" style={{ color: cfg?.color }}>
                                  {Math.round((r.probabilite || 0) * 100)}%
                                </span>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-sm font-semibold" style={{ color: cfg?.color }}>
                              {r.note_predite ? `${r.note_predite.toFixed(2)}/20` : "—"}
                            </td>
                            <td className="px-4 py-3">
                              {cfg ? (
                                <span className="text-xs px-2.5 py-1 rounded-full font-bold"
                                  style={{ background: cfg.badgeBg, color: cfg.badgeColor }}>
                                  {cfg.label}
                                </span>
                              ) : "—"}
                            </td>
                          </motion.tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <div className="px-5 py-3 border-t border-gray-100">
                  <p className="text-xs text-gray-400">{filtered.length} résultat(s) affiché(s)</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty state */}
        {!done && !loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
            className="flex flex-col items-center justify-center py-16 text-center">
            <div className="w-20 h-20 rounded-2xl bg-blue-50 flex items-center justify-center mx-auto mb-4">
              <svg className="w-10 h-10" style={{ color: "#1e56a0" }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-base font-semibold text-gray-600 mb-2">Prêt pour l'analyse par lot</h3>
            <p className="text-sm text-gray-400 max-w-sm">
              Uploadez un fichier CSV contenant les données de vos étudiants pour obtenir les prédictions en masse
            </p>
            <button onClick={downloadTemplate}
              className="mt-4 text-sm font-medium text-blue-500 hover:underline flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 10v6m0 0l-3-3m3 3l3-3" />
              </svg>
              Télécharger le modèle CSV
            </button>
          </motion.div>
        )}
      </div>
    </Layout>
  );
};

export default BatchPredictionPage;