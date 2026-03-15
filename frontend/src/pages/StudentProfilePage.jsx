import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  Tooltip, Cell
} from "recharts";
import Layout from "../components/Layout";
import api from "../services/api";

// ── Status config ─────────────────────────────────────────────────────────────
const STATUS_CONFIG = {
  VERT:  { label: "EXCELLENT",  color: "#16a34a", bg: "#f0fdf4", border: "#bbf7d0", badgeBg: "#dcfce7", badgeColor: "#15803d", icon: "🎯" },
  JAUNE: { label: "MOYEN",      color: "#d97706", bg: "#fffbeb", border: "#fde68a", badgeBg: "#fef3c7", badgeColor: "#b45309", icon: "⚠️" },
  ROUGE: { label: "À RISQUE",   color: "#dc2626", bg: "#fff1f2", border: "#fecaca", badgeBg: "#fee2e2", badgeColor: "#b91c1c", icon: "🚨" },
};

const MODULES_S1 = [
  { key: "Mathematiques_1",    label: "Maths 1" },
  { key: "Algorithmique_Prog", label: "Algo & Prog" },
  { key: "Architecture_Ord",   label: "Archi. Ord." },
  { key: "Electronique_Num",   label: "Électronique" },
  { key: "Reseaux_Info_1",     label: "Réseaux 1" },
  { key: "Anglais_Tech_1",     label: "Anglais 1" },
  { key: "Francais_Pro_1",     label: "Français 1" },
];

const MODULES_S2 = [
  { key: "Mathematiques_2",       label: "Maths 2" },
  { key: "Structures_Donnees",    label: "Struct. Données" },
  { key: "Systemes_Exploitation", label: "Sys. Exploit." },
  { key: "Bases_Donnees",         label: "Bases Données" },
  { key: "Reseaux_Info_2",        label: "Réseaux 2" },
  { key: "Anglais_Tech_2",        label: "Anglais 2" },
  { key: "Francais_Pro_2",        label: "Français 2" },
  { key: "PFA_2",                 label: "PFA" },
];

// ── Tooltip ───────────────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs shadow-lg">
        <p className="font-semibold text-gray-700">{payload[0].payload.label}</p>
        <p style={{ color: payload[0].fill || "#1e56a0" }}>
          Note: <strong>{payload[0].value}/20</strong>
        </p>
      </div>
    );
  }
  return null;
};

// ── Info row ──────────────────────────────────────────────────────────────────
const InfoRow = ({ label, value, highlight }) => (
  <div className="flex items-center justify-between py-2 border-b border-gray-50">
    <span className="text-xs text-gray-400">{label}</span>
    <span className={`text-xs font-semibold ${highlight ? "" : "text-gray-700"}`}
      style={highlight ? { color: highlight } : {}}>
      {value ?? "—"}
    </span>
  </div>
);

// ── Main ──────────────────────────────────────────────────────────────────────
const StudentProfilePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [student, setStudent] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [grades, setGrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [studentRes, gradesRes, predsRes] = await Promise.all([
          api.get(`/students/${id}`),
          api.get(`/grades/student/${id}`).catch(() => ({ data: [] })),
          api.get(`/predictions/student/${id}`).catch(() => ({ data: [] })),
        ]);
        setStudent(studentRes.data);
        setGrades(Array.isArray(gradesRes.data) ? gradesRes.data : []);
        setPredictions(Array.isArray(predsRes.data) ? predsRes.data : predsRes.data ? [predsRes.data] : []);
      } catch {
        setError("Impossible de charger le profil de l'étudiant.");
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchAll();
  }, [id]);

  // Best prediction (highest probability)
  const bestPred = predictions.reduce((best, p) =>
    (!best || p.probabilite > best.probabilite) ? p : best, null);
  const statusCfg = bestPred ? STATUS_CONFIG[bestPred.statut_couleur] : null;

  // Radar data from student modules
  const radarData = student ? [
    ...MODULES_S1.slice(0, 5).map((m) => ({ subject: m.label, note: student[m.key] || 0 })),
    ...MODULES_S2.slice(0, 5).map((m) => ({ subject: m.label, note: student[m.key] || 0 })),
  ] : [];

  // Bar data
  const barData = student ? [
    ...MODULES_S1.map((m) => ({ label: m.label, note: student[m.key], sem: "S1" })),
    ...MODULES_S2.map((m) => ({ label: m.label, note: student[m.key], sem: "S2" })),
  ].filter((d) => d.note != null) : [];

  const TABS = [
    { id: "overview", label: "Vue générale" },
    { id: "grades",   label: "Notes détaillées" },
    { id: "prediction", label: "Prédictions ML" },
  ];

  if (loading) return (
    <Layout>
      <div className="flex items-center justify-center min-h-full">
        <div className="text-center">
          <div className="w-10 h-10 border-2 border-blue-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-gray-400">Chargement du profil...</p>
        </div>
      </div>
    </Layout>
  );

  if (error) return (
    <Layout>
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-500">{error}</div>
      </div>
    </Layout>
  );

  if (!student) return null;

  return (
    <Layout>
      <div className="min-h-full p-6 space-y-5">
        {/* Back button */}
        <button onClick={() => navigate("/students")}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-blue-600 transition-colors">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Retour à la liste
        </button>

        {/* Profile header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm overflow-hidden relative">
          {/* Top accent */}
          <div className="absolute top-0 left-0 right-0 h-1"
            style={{ background: statusCfg ? `linear-gradient(90deg, ${statusCfg.color}, #1e56a0)` : "linear-gradient(90deg, #1e56a0, #e87722)" }} />

          <div className="flex flex-wrap items-start gap-5">
            {/* Avatar */}
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-xl font-bold text-white shrink-0"
              style={{ background: "linear-gradient(135deg, #1e56a0, #e87722)" }}>
              {(student.prenom?.[0] || "") + (student.nom?.[0] || "")}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-3 mb-1">
                <h1 className="text-xl font-bold text-gray-800">{student.prenom} {student.nom}</h1>
                {statusCfg && (
                  <span className="text-xs px-3 py-1 rounded-full font-bold flex items-center gap-1"
                    style={{ background: statusCfg.badgeBg, color: statusCfg.badgeColor }}>
                    {statusCfg.icon} {statusCfg.label}
                  </span>
                )}
              </div>
              <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                <span>CNE: <strong className="text-gray-700">{student.cne}</strong></span>
                <span className="px-2 py-0.5 rounded-full text-xs font-semibold"
                  style={{ background: "#eff6ff", color: "#1e56a0" }}>{student.filiere}</span>
                <span>Année <strong className="text-gray-700">{student.annee_etude}</strong></span>
                {student.email && <span className="text-gray-400">{student.email}</span>}
              </div>
            </div>

            {/* Best prediction score */}
            {bestPred && (
              <div className="text-center shrink-0 p-4 rounded-xl border-2"
                style={{ borderColor: statusCfg?.border, background: statusCfg?.bg }}>
                <p className="text-3xl font-bold" style={{ color: statusCfg?.color }}>
                  {Math.round(bestPred.probabilite * 100)}%
                </p>
                <p className="text-xs text-gray-400 mt-1">Probabilité réussite</p>
                <p className="text-sm font-semibold mt-1" style={{ color: statusCfg?.color }}>
                  {bestPred.note_predite?.toFixed(1)}/20
                </p>
              </div>
            )}
          </div>

          {/* Quick stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
            {[
              { label: "Moyenne S1", value: student.Moyenne_S1 ? `${student.Moyenne_S1}/20` : "—", color: "#1e56a0" },
              { label: "Absences S1", value: student.Absences_S1 ?? student.absences ?? 0, color: student.Absences_S1 > 5 ? "#dc2626" : "#16a34a" },
              { label: "Absences S2", value: student.Absences_S2 ?? 0, color: student.Absences_S2 > 5 ? "#dc2626" : "#16a34a" },
              { label: "Modules non validés", value: student.Modules_Non_Valides ?? 0, color: student.Modules_Non_Valides > 0 ? "#dc2626" : "#16a34a" },
            ].map((stat) => (
              <div key={stat.label} className="bg-gray-50 rounded-xl p-3 text-center border border-gray-100">
                <p className="text-lg font-bold" style={{ color: stat.color }}>{stat.value}</p>
                <p className="text-xs text-gray-400 mt-0.5">{stat.label}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Tabs */}
        <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
          {TABS.map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
              style={activeTab === tab.id
                ? { background: "#fff", color: "#1e56a0", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }
                : { color: "#6b7280" }}>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <AnimatePresenceWrapper>
          {/* Overview */}
          {activeTab === "overview" && (
            <motion.div key="overview" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Radar */}
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Profil académique (Radar)</h3>
                {radarData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="#f1f5f9" />
                      <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: "#9ca3af" }} />
                      <Radar dataKey="note" stroke="#1e56a0" fill="#1e56a0" fillOpacity={0.15} strokeWidth={2} />
                    </RadarChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-xs text-gray-400 text-center py-10">Données insuffisantes</p>
                )}
              </div>

              {/* Info perso */}
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Informations personnelles</h3>
                <InfoRow label="Nom complet" value={`${student.prenom} ${student.nom}`} />
                <InfoRow label="CNE" value={student.cne} />
                <InfoRow label="Email" value={student.email} />
                <InfoRow label="Filière" value={student.filiere} highlight="#1e56a0" />
                <InfoRow label="Année d'étude" value={`${student.annee_etude}ème année`} />
                <InfoRow label="Redoublant" value={student.Redoublant ? "Oui" : "Non"}
                  highlight={student.Redoublant ? "#dc2626" : "#16a34a"} />
                <InfoRow label="PFA 2ème année" value={student.PFA_2 ? `${student.PFA_2}/20` : "—"} highlight="#1e56a0" />
              </div>
            </motion.div>
          )}

          {/* Grades */}
          {activeTab === "grades" && (
            <motion.div key="grades" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className="space-y-4">
              {/* Bar chart */}
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Toutes les notes</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={barData} barSize={14}>
                    <XAxis dataKey="label" tick={{ fontSize: 9, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                    <YAxis domain={[0, 20]} tick={{ fontSize: 9, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
                    <Bar dataKey="note" radius={[3, 3, 0, 0]}>
                      {barData.map((entry, i) => (
                        <Cell key={i}
                          fill={entry.note >= 14 ? "#16a34a" : entry.note >= 10 ? "#d97706" : "#dc2626"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <div className="flex gap-4 justify-center mt-2">
                  {[{ color: "#16a34a", label: "≥14" }, { color: "#d97706", label: "10–14" }, { color: "#dc2626", label: "<10" }].map((item) => (
                    <div key={item.label} className="flex items-center gap-1">
                      <div className="w-2.5 h-2.5 rounded-full" style={{ background: item.color }} />
                      <span className="text-xs text-gray-400">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Tables S1 + S2 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {[{ title: "Semestre 1", modules: MODULES_S1 }, { title: "Semestre 2", modules: MODULES_S2 }].map((sem) => (
                  <div key={sem.title} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">{sem.title}</h3>
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-100">
                          <th className="text-left text-xs font-semibold text-gray-400 pb-2">Module</th>
                          <th className="text-right text-xs font-semibold text-gray-400 pb-2">Note</th>
                          <th className="text-right text-xs font-semibold text-gray-400 pb-2">Statut</th>
                        </tr>
                      </thead>
                      <tbody>
                        {sem.modules.map((m) => {
                          const note = student[m.key];
                          if (note == null) return null;
                          const color = note >= 14 ? "#16a34a" : note >= 10 ? "#d97706" : "#dc2626";
                          const bg = note >= 14 ? "#dcfce7" : note >= 10 ? "#fef3c7" : "#fee2e2";
                          const label = note >= 14 ? "Bien" : note >= 10 ? "Passable" : "Insuffisant";
                          return (
                            <tr key={m.key} className="border-b border-gray-50 hover:bg-gray-50">
                              <td className="py-2 text-xs text-gray-700">{m.label}</td>
                              <td className="py-2 text-right text-xs font-bold" style={{ color }}>{note}/20</td>
                              <td className="py-2 text-right">
                                <span className="text-xs px-2 py-0.5 rounded-full font-medium"
                                  style={{ background: bg, color }}>{label}</span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                    {sem.title === "Semestre 1" && student.Moyenne_S1 && (
                      <div className="mt-3 pt-3 border-t border-gray-100 flex justify-between items-center">
                        <span className="text-xs font-semibold text-gray-500">Moyenne S1</span>
                        <span className="text-sm font-bold" style={{ color: "#1e56a0" }}>{student.Moyenne_S1}/20</span>
                      </div>
                    )}
                    {sem.title === "Semestre 2" && student.PFA_2 && (
                      <div className="mt-3 pt-3 border-t border-gray-100 flex justify-between items-center">
                        <span className="text-xs font-semibold text-gray-500">PFA</span>
                        <span className="text-sm font-bold" style={{ color: "#1e56a0" }}>{student.PFA_2}/20</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Predictions */}
          {activeTab === "prediction" && (
            <motion.div key="prediction" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className="space-y-4">
              {predictions.length === 0 ? (
                <div className="bg-white border border-gray-200 rounded-xl p-8 text-center shadow-sm">
                  <div className="w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3">
                    <svg className="w-7 h-7 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <p className="text-sm font-semibold text-gray-600 mb-1">Aucune prédiction disponible</p>
                  <p className="text-xs text-gray-400">Les prédictions apparaîtront dès que la collègue ML les aura générées.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {predictions.map((pred) => {
                    const cfg = STATUS_CONFIG[pred.statut_couleur];
                    return (
                      <div key={pred.modele_utilise} className="bg-white border-2 rounded-xl p-5 shadow-sm"
                        style={{ borderColor: cfg?.border, background: cfg?.bg }}>
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-xs font-bold text-gray-600">{pred.modele_utilise}</span>
                          <span className="text-lg">{cfg?.icon}</span>
                        </div>
                        <p className="text-3xl font-bold mb-1" style={{ color: cfg?.color }}>
                          {Math.round(pred.probabilite * 100)}%
                        </p>
                        <p className="text-xs text-gray-400 mb-3">Probabilité de réussite</p>
                        <span className="text-xs px-3 py-1 rounded-full font-bold"
                          style={{ background: cfg?.badgeBg, color: cfg?.badgeColor }}>
                          {cfg?.label}
                        </span>
                        {pred.note_predite && (
                          <p className="text-sm font-semibold mt-2" style={{ color: cfg?.color }}>
                            Note prédite : {pred.note_predite.toFixed(2)}/20
                          </p>
                        )}
                        {pred.recommandations?.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-gray-200 space-y-1">
                            {pred.recommandations.slice(0, 2).map((r, i) => (
                              <p key={i} className="text-xs text-gray-500">• {r}</p>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Button to full prediction page */}
              <div className="text-center">
                <button onClick={() => navigate(`/prediction?student=${id}`)}
                  className="px-6 py-2.5 rounded-xl text-sm font-bold text-white transition-all"
                  style={{ background: "linear-gradient(135deg, #1e56a0, #2568b5)" }}>
                  Voir l'analyse complète →
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresenceWrapper>
      </div>
    </Layout>
  );
};

// Simple wrapper to avoid importing AnimatePresence separately
const AnimatePresenceWrapper = ({ children }) => <>{children}</>;

export default StudentProfilePage;