import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis,
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell
} from "recharts";
import Layout from "../components/Layout";
import {
  getStudents, getStudent,
  getStudentPredictions, getStudentGrades,
  predictML
} from "../services/predictionService";

// ── Couleurs selon statut ─────────────────────────────────────────────────────
const STATUS_CONFIG = {
  VERT: {
    label: "EXCELLENT", color: "#16a34a", bg: "#f0fdf4",
    border: "#bbf7d0", badgeBg: "#dcfce7", badgeColor: "#15803d",
    icon: "🎯", title: "Réussite prévue",
    desc: "L'étudiant est sur la bonne voie pour réussir.",
  },
  JAUNE: {
    label: "MOYEN", color: "#d97706", bg: "#fffbeb",
    border: "#fde68a", badgeBg: "#fef3c7", badgeColor: "#b45309",
    icon: "⚠️", title: "Suivi recommandé",
    desc: "L'étudiant nécessite un suivi régulier.",
  },
  ROUGE: {
    label: "À RISQUE", color: "#dc2626", bg: "#fff1f2",
    border: "#fecaca", badgeBg: "#fee2e2", badgeColor: "#b91c1c",
    icon: "🚨", title: "Intervention urgente",
    desc: "L'étudiant est en situation de risque d'échec.",
  },
};

const MODELES = ["RandomForest", "SVM", "LogisticRegression"];
const MODELE_LABELS = {
  RandomForest: "Random Forest",
  SVM: "SVM",
  LogisticRegression: "Régression Logistique",
};

const MODULES_S1 = [
  { key: "Mathematiques_1", label: "Maths 1" },
  { key: "Algorithmique_Prog", label: "Algo & Prog" },
  { key: "Architecture_Ord", label: "Archi Ord." },
  { key: "Electronique_Num", label: "Électronique" },
  { key: "Reseaux_Info_1", label: "Réseaux 1" },
  { key: "Anglais_Tech_1", label: "Anglais 1" },
  { key: "Francais_Pro_1", label: "Français 1" },
];

const MODULES_S2 = [
  { key: "Mathematiques_2", label: "Maths 2" },
  { key: "Structures_Donnees", label: "Struct. Données" },
  { key: "Systemes_Exploitation", label: "Sys. Exploit." },
  { key: "Bases_Donnees", label: "Bases Données" },
  { key: "Reseaux_Info_2", label: "Réseaux 2" },
  { key: "Anglais_Tech_2", label: "Anglais 2" },
  { key: "Francais_Pro_2", label: "Français 2" },
  { key: "PFA_2", label: "PFA" },
];

// ── Gauge Chart ───────────────────────────────────────────────────────────────
const GaugeChart = ({ value, color }) => {
  const pct = Math.round((value || 0) * 100);
  return (
    <div className="relative flex items-center justify-center" style={{ height: 160 }}>
      <ResponsiveContainer width="100%" height={160}>
        <RadialBarChart cx="50%" cy="75%" innerRadius="70%" outerRadius="100%"
          startAngle={180} endAngle={0} data={[{ value: pct, fill: color }]}>
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar dataKey="value" cornerRadius={8} background={{ fill: "#f1f5f9" }} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute bottom-2 text-center">
        <p className="text-3xl font-bold" style={{ color }}>{pct}%</p>
        <p className="text-xs text-gray-400">Probabilité</p>
      </div>
    </div>
  );
};

// ── Tooltip custom ────────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs shadow-lg">
        <p className="font-semibold text-gray-700">{payload[0].payload.label}</p>
        <p style={{ color: payload[0].fill }}>Note: <strong>{payload[0].value}/20</strong></p>
      </div>
    );
  }
  return null;
};

// ── Grades Bar Chart ──────────────────────────────────────────────────────────
const GradesBarChart = ({ grades, semester }) => {
  const modules = semester === 1 ? MODULES_S1 : MODULES_S2;
  const data = modules.map((m) => ({
    label: m.label,
    note: grades?.[m.key] ?? null,
    fill: !grades?.[m.key] ? "#e5e7eb"
      : grades[m.key] >= 14 ? "#16a34a"
      : grades[m.key] >= 10 ? "#d97706"
      : "#dc2626",
  })).filter((d) => d.note !== null);

  if (!data.length) return (
    <p className="text-xs text-gray-400 text-center py-8">Aucune note disponible</p>
  );

  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} barSize={16}>
        <XAxis dataKey="label" tick={{ fontSize: 9, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
        <YAxis domain={[0, 20]} tick={{ fontSize: 9, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
        <Bar dataKey="note" radius={[3, 3, 0, 0]}>
          {data.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

// ── Model Card ────────────────────────────────────────────────────────────────
const ModelCard = ({ modele, prediction, isSelected, onClick }) => {
  const cfg = prediction ? STATUS_CONFIG[prediction.statut_couleur] : null;
  return (
    <button onClick={onClick}
      className="w-full text-left p-4 rounded-xl border-2 transition-all duration-200"
      style={{
        borderColor: isSelected ? (cfg?.color || "#1e56a0") : "#e5e7eb",
        background: isSelected ? (cfg?.bg || "#eff6ff") : "#fff",
        boxShadow: isSelected ? `0 0 0 3px ${cfg?.color || "#1e56a0"}22` : "none",
      }}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-bold text-gray-600">{MODELE_LABELS[modele]}</span>
        {cfg && (
          <span className="text-xs px-2 py-0.5 rounded-full font-bold"
            style={{ background: cfg.badgeBg, color: cfg.badgeColor }}>
            {cfg.label}
          </span>
        )}
      </div>
      {prediction ? (
        <div className="flex items-end gap-2">
          <span className="text-2xl font-bold" style={{ color: cfg?.color }}>
            {Math.round(prediction.probabilite * 100)}%
          </span>
          <span className="text-xs text-gray-400 mb-0.5">probabilité</span>
          <span className="ml-auto text-sm font-semibold text-gray-700">
            {prediction.note_predite?.toFixed(1)}/20
          </span>
        </div>
      ) : (
        <p className="text-xs text-gray-400">Prédiction non disponible</p>
      )}
    </button>
  );
};

// ── Main Page ─────────────────────────────────────────────────────────────────
const PredictionPage = () => {
  const [students, setStudents] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [student, setStudent] = useState(null);
  const [predictions, setPredictions] = useState({}); // { RandomForest: {...}, SVM: {...}, ... }
  const [grades, setGrades] = useState(null);
  const [selectedModel, setSelectedModel] = useState("RandomForest");
  const [loading, setLoading] = useState(false);
  const [loadingStudents, setLoadingStudents] = useState(true);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getStudents()
      .then(setStudents)
      .catch(() => setError("Impossible de charger les étudiants."))
      .finally(() => setLoadingStudents(false));
  }, []);

  const handleSelect = async (id) => {
    if (!id) return;
    setSelectedId(id);
    setLoading(true);
    setError("");
    setPredictions({});
    setGrades(null);
    setStudent(null);

    try {
      const [studentData, gradesData, predsData] = await Promise.all([
        getStudent(id),
        getStudentGrades(id).catch(() => null),
        getStudentPredictions(id).catch(() => []),
      ]);

      setStudent(studentData);

      // Construire grades depuis les données étudiant ou API grades
      const gradesMap = {};
      if (Array.isArray(gradesData)) {
        gradesData.forEach((g) => { gradesMap[g.matiere] = g.note; });
      }
      setGrades(Object.keys(gradesMap).length ? gradesMap : studentData);

      // Organiser prédictions existantes par modèle
      const predsMap = {};
      if (Array.isArray(predsData)) {
        predsData.forEach((p) => { predsMap[p.modele_utilise] = p; });
      } else if (predsData?.modele_utilise) {
        predsMap[predsData.modele_utilise] = predsData;
      }

      // Lancer les prédictions ML pour les modèles manquants
      const missingModels = MODELES.filter((m) => !predsMap[m]);
      if (missingModels.length > 0) {
        const mlResults = await Promise.allSettled(
          missingModels.map((modele) =>
            predictML({ student_id: parseInt(id), modele_utilise: modele })
          )
        );
        mlResults.forEach((result) => {
          if (result.status === "fulfilled" && result.value) {
            predsMap[result.value.modele_utilise] = result.value;
          }
        });
      }

      setPredictions(predsMap);

    } catch {
      setError("Erreur lors du chargement des données.");
    } finally {
      setLoading(false);
    }
  };

  const filteredStudents = students.filter((s) =>
    `${s.nom} ${s.prenom} ${s.cne}`.toLowerCase().includes(search.toLowerCase())
  );

  const activePred = predictions[selectedModel];
  const activeCfg = activePred ? STATUS_CONFIG[activePred.statut_couleur] : null;

  return (
    <Layout>
      <div className="min-h-full p-6 space-y-5">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-2xl font-bold text-gray-800">Prédiction Individuelle</h1>
          <p className="text-sm text-gray-400 mt-0.5">Analysez la réussite d'un étudiant avec 3 modèles ML</p>
        </motion.div>

        {/* Student selector */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Sélectionner un étudiant</h2>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input value={search} onChange={(e) => setSearch(e.target.value)}
                placeholder="Rechercher par nom, prénom, CNE..."
                className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-700 bg-gray-50 outline-none focus:border-blue-400 focus:bg-white transition-all" />
            </div>
            <select value={selectedId} onChange={(e) => handleSelect(e.target.value)}
              className="flex-1 border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-700 bg-gray-50 outline-none focus:border-blue-400 transition-all">
              <option value="">-- Choisir un étudiant --</option>
              {filteredStudents.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.prenom} {s.nom} — {s.filiere} ({s.cne})
                </option>
              ))}
            </select>
          </div>
          {loadingStudents && (
            <p className="text-xs text-gray-400 mt-2 flex items-center gap-1">
              <div className="w-3 h-3 border border-blue-300 border-t-blue-500 rounded-full animate-spin" />
              Chargement...
            </p>
          )}
        </motion.div>

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="w-10 h-10 border-2 border-blue-200 border-t-blue-500 rounded-full animate-spin mb-3" />
            <p className="text-sm text-gray-400">Analyse ML en cours...</p>
          </div>
        )}

        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-500">
            {error}
          </div>
        )}

        {/* Results */}
        <AnimatePresence>
          {student && !loading && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="space-y-5">

              {/* Student info */}
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center text-base font-bold text-white shrink-0"
                  style={{ background: "linear-gradient(135deg, #1e56a0, #e87722)" }}>
                  {(student.prenom?.[0] || "") + (student.nom?.[0] || "")}
                </div>
                <div className="flex-1">
                  <h2 className="text-base font-bold text-gray-800">{student.prenom} {student.nom}</h2>
                  <div className="flex flex-wrap gap-3 mt-1">
                    <span className="text-xs text-gray-500">CNE: <strong>{student.cne}</strong></span>
                    <span className="text-xs px-2 py-0.5 rounded-full font-semibold" style={{ background: "#eff6ff", color: "#1e56a0" }}>{student.filiere}</span>
                    <span className="text-xs text-gray-500">Année {student.annee || "1A"}</span>
                    <span className="text-xs text-gray-500">Absences S1: <strong>{student.absences_s1 ?? 0}h</strong></span>
                    <span className="text-xs text-gray-500">Absences S2: <strong>{student.absences_s2 ?? 0}h</strong></span>
                    <span className="text-xs px-2 py-0.5 rounded-full font-semibold"
                      style={{ background: student.redoublant ? "#fee2e2" : "#dcfce7", color: student.redoublant ? "#b91c1c" : "#15803d" }}>
                      {student.redoublant ? "Redoublant" : "Non redoublant"}
                    </span>
                  </div>
                </div>
              </div>

              {/* 3 Model cards */}
              <div>
                <h2 className="text-sm font-semibold text-gray-700 mb-3">Choisir un modèle ML</h2>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {MODELES.map((m) => (
                    <ModelCard key={m} modele={m} prediction={predictions[m]}
                      isSelected={selectedModel === m} onClick={() => setSelectedModel(m)} />
                  ))}
                </div>
              </div>

              {/* No prediction */}
              {!activePred && (
                <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-sm text-center">
                  <div className="w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3">
                    <svg className="w-7 h-7 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <h3 className="text-sm font-semibold text-gray-600 mb-1">Prédiction non disponible</h3>
                  <p className="text-xs text-gray-400">Le modèle <strong>{MODELE_LABELS[selectedModel]}</strong> n'a pas encore généré de prédiction pour cet étudiant.</p>
                </div>
              )}

              {/* Prediction result */}
              {activePred && activeCfg && (
                <div className="space-y-4">
                  {/* Result + gauge + recommendations */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {/* Gauge */}
                    <div className="bg-white rounded-xl border-2 p-5 shadow-sm text-center"
                      style={{ borderColor: activeCfg.border, background: activeCfg.bg }}>
                      <div className="flex items-center justify-center gap-2 mb-2">
                        <span className="text-lg">{activeCfg.icon}</span>
                        <h3 className="text-sm font-bold" style={{ color: activeCfg.color }}>{activeCfg.title}</h3>
                      </div>
                      <GaugeChart value={activePred.probabilite} color={activeCfg.color} />
                      <span className="inline-block mt-2 px-4 py-1.5 rounded-full text-sm font-bold"
                        style={{ background: activeCfg.badgeBg, color: activeCfg.badgeColor }}>
                        {activeCfg.label}
                      </span>
                      <p className="text-sm text-gray-600 mt-2">
                        Note prédite : <strong style={{ color: activeCfg.color }}>{activePred.note_predite?.toFixed(2)}/20</strong>
                      </p>
                      <p className="text-xs text-gray-400 mt-1">{activePred.label}</p>
                    </div>

                    {/* Risk factors */}
                    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                      <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                        <svg className="w-4 h-4 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        Facteurs de risque
                      </h3>
                      {activePred.facteurs_risque?.length ? (
                        <div className="space-y-2">
                          {activePred.facteurs_risque.map((f, i) => (
                            <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-orange-50 border border-orange-100">
                              <div className="w-1.5 h-1.5 rounded-full bg-orange-400 mt-1.5 shrink-0" />
                              <p className="text-xs text-gray-700">{f}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-gray-400">Aucun facteur de risque détecté ✅</p>
                      )}
                    </div>

                    {/* Recommendations */}
                    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                      <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                        <svg className="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        Recommandations
                      </h3>
                      {activePred.recommandations?.length ? (
                        <div className="space-y-2">
                          {activePred.recommandations.map((r, i) => (
                            <div key={i} className="flex items-start gap-2">
                              <div className="w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
                                style={{ background: activeCfg.badgeBg, color: activeCfg.badgeColor }}>
                                {i + 1}
                              </div>
                              <p className="text-xs text-gray-600">{r}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-gray-400">Aucune recommandation disponible</p>
                      )}
                    </div>
                  </div>

                  {/* Grades charts */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-semibold text-gray-700">Notes Semestre 1</h3>
                        <span className="text-xs text-gray-400">
                          Moy: <strong style={{ color: "#1e56a0" }}>{student.Moyenne_S1 ?? "—"}/20</strong>
                        </span>
                      </div>
                      <GradesBarChart grades={student} semester={1} />
                    </div>
                    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-semibold text-gray-700">Notes Semestre 2</h3>
                        <span className="text-xs text-gray-400">
                          PFA: <strong style={{ color: "#1e56a0" }}>{student.PFA_2 ?? "—"}/20</strong>
                        </span>
                      </div>
                      <GradesBarChart grades={student} semester={2} />
                    </div>
                  </div>

                  {/* Notes table */}
                  <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Détail complet des notes</h3>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      {[{ title: "Semestre 1", modules: MODULES_S1 }, { title: "Semestre 2", modules: MODULES_S2 }].map((sem) => (
                        <div key={sem.title}>
                          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">{sem.title}</p>
                          <table className="w-full">
                            <tbody>
                              {sem.modules.map((m) => {
                                const note = student[m.key];
                                if (!note && note !== 0) return null;
                                const color = note >= 14 ? "#16a34a" : note >= 10 ? "#d97706" : "#dc2626";
                                const bg = note >= 14 ? "#dcfce7" : note >= 10 ? "#fef3c7" : "#fee2e2";
                                return (
                                  <tr key={m.key} className="border-b border-gray-50">
                                    <td className="py-1.5 text-xs text-gray-600">{m.label}</td>
                                    <td className="py-1.5 text-right">
                                      <span className="text-xs font-bold px-2 py-0.5 rounded-full"
                                        style={{ background: bg, color }}>
                                        {note}/20
                                      </span>
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      ))}
                    </div>

                    {/* Résumé */}
                    <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-2 sm:grid-cols-4 gap-3">
                      {[
                        { label: "Moyenne S1", value: student.Moyenne_S1 },
                        { label: "PFA (2ème année)", value: student.PFA_2 },
                        { label: "Modules non validés", value: student.Modules_Non_Valides },
                        { label: "Redoublant", value: student.Redoublant ? "Oui" : "Non" },
                      ].map((item) => (
                        <div key={item.label} className="text-center p-3 bg-gray-50 rounded-xl">
                          <p className="text-xs text-gray-400 mb-1">{item.label}</p>
                          <p className="text-sm font-bold text-gray-800">{item.value ?? "—"}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty state */}
        {!student && !loading && !error && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
            className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-20 h-20 rounded-2xl bg-blue-50 flex items-center justify-center mx-auto mb-4">
              <svg className="w-10 h-10" style={{ color: "#1e56a0" }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-base font-semibold text-gray-600 mb-2">Sélectionnez un étudiant</h3>
            <p className="text-sm text-gray-400 max-w-sm">
              Choisissez un étudiant pour analyser sa probabilité de réussite avec les 3 modèles ML
            </p>
          </motion.div>
        )}
      </div>
    </Layout>
  );
};

export default PredictionPage;