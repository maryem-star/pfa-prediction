import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Cell
} from "recharts";
import api from "../services/api";
import { getMyRecommendations, markAsRead } from "../services/recommendationService";

function getStatusInfo(couleur) {
  if (couleur === "VERT")  return { label: "En bonne voie", color: "#22c55e", bg: "bg-green-50",  text: "text-green-700",  border: "border-green-200",  glow: "shadow-green-100" };
  if (couleur === "JAUNE") return { label: "À surveiller",  color: "#f59e0b", bg: "bg-yellow-50", text: "text-yellow-700", border: "border-yellow-200", glow: "shadow-yellow-100" };
  if (couleur === "ROUGE") return { label: "À risque",      color: "#ef4444", bg: "bg-red-50",    text: "text-red-700",   border: "border-red-200",   glow: "shadow-red-100" };
  return { label: "Non évalué", color: "#94a3b8", bg: "bg-gray-50", text: "text-gray-600", border: "border-gray-200", glow: "" };
}

function ProbabilityGauge({ value, color }) {
  const pct = Math.round((value || 0) * 100);
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-40 h-24">
        <svg viewBox="0 0 120 70" className="w-full h-full">
          <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke="#f1f5f9" strokeWidth="10" strokeLinecap="round" />
          <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke={color} strokeWidth="10" strokeLinecap="round"
            strokeDasharray={`${(pct / 100) * 157} 157`}
            style={{ filter: `drop-shadow(0 0 6px ${color}80)` }}
          />
          <line x1="60" y1="65" x2="60" y2="22" stroke={color} strokeWidth="2.5" strokeLinecap="round"
            transform={`rotate(${-135 + (pct / 100) * 270 - 90}, 60, 65)`} />
          <circle cx="60" cy="65" r="5" fill={color} style={{ filter: `drop-shadow(0 0 4px ${color})` }} />
        </svg>
      </div>
      <p className="text-4xl font-black text-gray-800 -mt-3 tracking-tight">
        {pct}<span className="text-lg text-gray-400 font-normal">%</span>
      </p>
    </div>
  );
}

function StatCard({ icon, label, value, color, bg }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
      className={`${bg} rounded-2xl p-4 border border-white/60`}
    >
      <div className="text-2xl mb-2">{icon}</div>
      <p className={`text-xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-0.5">{label}</p>
    </motion.div>
  );
}

export default function StudentDashboard() {
  const { user, logout } = useAuth();
  const [prediction, setPrediction]           = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [grades, setGrades]                   = useState(null);
  const [activeTab, setActiveTab]             = useState("overview");
  const [loading, setLoading]                 = useState(true);
  const [expandedRec, setExpandedRec]         = useState(null);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [predRes, recRes, gradesRes] = await Promise.allSettled([
        // Utilise student_id depuis le token
        api.get(`/v2/students/${user.student_id || user.id}/stats`),
        getMyRecommendations(),
        api.get(`/students/${user.student_id || user.id}/grades`),
      ]);

      if (predRes.status === "fulfilled") {
        const data = predRes.value.data;
        // Adapter la structure retournée par /v2/students/{id}/stats
        setPrediction({
          label: data.derniere_prediction?.label || null,
          probabilite: data.derniere_prediction?.probabilite || null,
          statut_couleur: data.derniere_prediction?.statut_couleur || null,
          note_predite: data.derniere_prediction?.note_predite || null,
          facteurs_risque: data.derniere_prediction?.facteurs_risque || [],
          recommandations: data.derniere_prediction?.recommandations || [],
          moyennes: data.moyennes_par_semestre || {},
        });
      }

      if (recRes.status === "fulfilled") {
        // Adapter le format retourné par le backend
        const recs = Array.isArray(recRes.value) ? recRes.value : [];
        setRecommendations(recs.map(r => ({
          id: r.id,
          expediteur: r.envoyeur,
          role: r.role,
          message: r.message,
          date: r.date,
          lu: r.statut === "lu",
        })));
      }

      if (gradesRes.status === "fulfilled") setGrades(gradesRes.value.data);

    } catch {}

    // Mocks fallback si pas de données
    setPrediction(p => p || {
      label: "Réussi", probabilite: 0.82, statut_couleur: "VERT",
      note_predite: 14.5,
      facteurs_risque: ["Taux d'absences S2 légèrement élevé"],
      recommandations: ["Maintenir votre régularité en cours"],
      moyennes: { S1: 13.67 },
    });

    setRecommendations(r => r.length > 0 ? r : [
      { id: 1, expediteur: "Chef Filière ISIC", role: "chef_filiere",
        message: "Félicitations pour vos excellents résultats en S1 !",
        date: "2025-03-15T10:30:00", lu: false },
      { id: 2, expediteur: "Chef Département TRI", role: "chef_departement",
        message: "Attention au module Réseaux — les notes de mi-parcours indiquent un risque.",
        date: "2025-03-10T14:00:00", lu: true },
    ]);

    setGrades(g => g || {
      s1: { Mathématiques: 15, Algorithmique: 14, Architecture: 12, Électronique: 11, Réseaux: 13, Anglais: 16 },
      s2: { Mathématiques: 15, Structures_Données: 14, Systèmes: 13, Bases_Données: 16, Réseaux: 14, Anglais: 15 },
    });

    setLoading(false);
  };

  // Marquer comme lu quand l'étudiant ouvre la recommandation
  const handleOpenRec = async (rec) => {
    setExpandedRec(prev => prev === rec.id ? null : rec.id);
    if (!rec.lu) {
      setRecommendations(prev =>
        prev.map(r => r.id === rec.id ? { ...r, lu: true } : r)
      );
      await markAsRead(rec.id);
    }
  };

  const status      = getStatusInfo(prediction?.statut_couleur);
  const unreadCount = recommendations.filter(r => !r.lu).length;

  const radarData = grades?.s2
    ? Object.entries(grades.s2).map(([m, v]) => ({ module: m.replace(/_/g, " "), value: v }))
    : [];
  const barDataS1 = grades?.s1
    ? Object.entries(grades.s1).map(([m, v]) => ({
        module: m, note: v,
        fill: v >= 12 ? "#22c55e" : v >= 10 ? "#f59e0b" : "#ef4444"
      }))
    : [];

  const tabs = [
    { id: "overview",        label: "Vue d'ensemble", icon: "🏠" },
    { id: "grades",          label: "Mes notes",       icon: "📊" },
    { id: "recommendations", label: "Recommandations", icon: "💬", badge: unreadCount },
  ];

  const allNotes  = [...Object.values(grades?.s1 || {}), ...Object.values(grades?.s2 || {})];
  const moyenne   = allNotes.length ? (allNotes.reduce((a, b) => a + b, 0) / allNotes.length).toFixed(1) : "—";
  const validated = allNotes.filter(n => n >= 10).length;

  // Nom affiché — depuis le token ou fallback email
  const displayName = user?.prenom && user?.nom
    ? `${user.prenom} ${user.nom}`
    : user?.email?.split("@")[0] || "Étudiant";
  const initials = user?.prenom?.[0] && user?.nom?.[0]
    ? `${user.prenom[0]}${user.nom[0]}`
    : user?.email?.[0]?.toUpperCase() || "E";

  return (
    <div className="min-h-screen" style={{ background: "linear-gradient(135deg, #f0f4ff 0%, #fafafa 50%, #fff7f0 100%)" }}>

      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-30 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/ensa-logo.png" alt="ENSA" className="h-8 w-auto"
              onError={e => { e.target.style.display = "none"; }} />
            <div>
              <p className="text-sm font-black text-[#1B3A6B] tracking-tight">PredictEdu</p>
              <p className="text-xs text-gray-400">Espace Étudiant</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Cloche notification */}
            <button onClick={() => setActiveTab("recommendations")}
              className="relative p-2 rounded-xl hover:bg-gray-50 transition-colors">
              <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <AnimatePresence>
                {unreadCount > 0 && (
                  <motion.span
                    initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }}
                    className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center font-bold"
                  >
                    {unreadCount}
                  </motion.span>
                )}
              </AnimatePresence>
            </button>

            {/* Avatar */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-[#1B3A6B] flex items-center justify-center flex-shrink-0">
                <span className="text-white text-xs font-bold">{initials}</span>
              </div>
              <div className="hidden sm:block text-right">
                <p className="text-sm font-semibold text-gray-800">{displayName}</p>
                <p className="text-xs text-gray-400">{user?.filiere || "Étudiant"}</p>
              </div>
            </div>

            <button onClick={logout}
              className="p-2 rounded-xl text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
              title="Déconnexion">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="max-w-5xl mx-auto px-4 flex gap-0">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`relative px-5 py-3 text-sm font-medium border-b-2 transition-all ${
                activeTab === t.id
                  ? "border-[#1B3A6B] text-[#1B3A6B]"
                  : "border-transparent text-gray-400 hover:text-gray-600"
              }`}
            >
              <span className="mr-1.5">{t.icon}</span>
              {t.label}
              {t.badge > 0 && (
                <span className="ml-2 bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full font-bold">
                  {t.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </header>

      {loading ? (
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="w-8 h-8 border-2 border-[#1B3A6B] border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <main className="max-w-5xl mx-auto px-4 py-6 space-y-5">

          {/* OVERVIEW */}
          {activeTab === "overview" && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">

              <div className={`bg-white rounded-3xl p-6 shadow-lg border ${status.border} ${status.glow}`}>
                <div className="flex flex-col md:flex-row items-center gap-8">
                  <div className="flex-shrink-0 flex flex-col items-center">
                    <ProbabilityGauge value={prediction?.probabilite} color={status.color} />
                    <span className={`mt-3 px-4 py-1.5 rounded-full text-sm font-bold ${status.bg} ${status.text} border ${status.border}`}>
                      {status.label}
                    </span>
                  </div>
                  <div className="flex-1 space-y-4 w-full">
                    <div>
                      <h2 className="text-xl font-black text-gray-800 tracking-tight">Ma prédiction de réussite</h2>
                      <p className="text-sm text-gray-400 mt-1">Basée sur votre parcours académique</p>
                    </div>
                    <div className="flex gap-3 flex-wrap">
                      <div className="bg-gray-50 rounded-2xl px-5 py-3 border border-gray-100">
                        <p className="text-xs text-gray-400 mb-1">Note prédite</p>
                        <p className="text-2xl font-black text-gray-800">
                          {prediction?.note_predite ?? "—"}
                          <span className="text-sm font-normal text-gray-400">/20</span>
                        </p>
                      </div>
                      <div className={`${status.bg} rounded-2xl px-5 py-3 border ${status.border}`}>
                        <p className="text-xs text-gray-400 mb-1">Décision</p>
                        <p className={`text-2xl font-black ${status.text}`}>{prediction?.label || "Non évalué"}</p>
                      </div>
                      {/* Moyennes par semestre */}
                      {prediction?.moyennes && Object.entries(prediction.moyennes).map(([sem, moy]) => (
                        <div key={sem} className="bg-blue-50 rounded-2xl px-5 py-3 border border-blue-100">
                          <p className="text-xs text-gray-400 mb-1">Moyenne {sem}</p>
                          <p className="text-2xl font-black text-blue-700">{moy}</p>
                        </div>
                      ))}
                    </div>

                    {prediction?.facteurs_risque?.length > 0 && (
                      <div className="space-y-1.5">
                        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Points d'attention</p>
                        {prediction.facteurs_risque.map((f, i) => (
                          <div key={i} className="flex items-start gap-2 bg-yellow-50 rounded-xl px-3 py-2 border border-yellow-100">
                            <span className="text-yellow-500 mt-0.5 flex-shrink-0">⚠</span>
                            <p className="text-sm text-yellow-800">{f}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <StatCard icon="📈" label="Moyenne générale" value={`${moyenne}/20`} color="text-[#1B3A6B]" bg="bg-blue-50" />
                <StatCard icon="✅" label="Modules validés" value={`${validated}/${allNotes.length}`} color="text-green-700" bg="bg-green-50" />
                <StatCard icon="💬" label="Recommandations" value={recommendations.length} color="text-orange-700" bg="bg-orange-50" />
              </div>

              {prediction?.recommandations?.length > 0 && (
                <div className="bg-gradient-to-r from-[#1B3A6B] to-[#2d5fa8] rounded-3xl p-5 text-white">
                  <p className="text-sm font-bold mb-3 flex items-center gap-2">
                    <span>💡</span> Conseils du système
                  </p>
                  <div className="space-y-2">
                    {prediction.recommandations.map((r, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <span className="text-blue-300 mt-0.5 flex-shrink-0">→</span>
                        <p className="text-sm text-blue-100">{r}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {recommendations.length > 0 && (
                <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm font-bold text-gray-700">Dernière recommandation</p>
                    <button onClick={() => setActiveTab("recommendations")}
                      className="text-xs text-[#1B3A6B] font-semibold hover:underline">
                      Voir tout →
                    </button>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
                      recommendations[0].role?.includes("departement") ? "bg-orange-100" : "bg-blue-100"
                    }`}>
                      <span className={`text-sm font-bold ${
                        recommendations[0].role?.includes("departement") ? "text-orange-700" : "text-blue-700"
                      }`}>
                        {recommendations[0].expediteur?.[0]}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-semibold text-gray-800">{recommendations[0].expediteur}</p>
                        {!recommendations[0].lu && (
                          <span className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0" />
                        )}
                      </div>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">{recommendations[0].message}</p>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* NOTES */}
          {activeTab === "grades" && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
                  <h3 className="text-sm font-bold text-gray-700 mb-4">Semestre 1</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={barDataS1} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" horizontal={false} />
                      <XAxis type="number" domain={[0, 20]} tick={{ fontSize: 10 }} />
                      <YAxis type="category" dataKey="module" tick={{ fontSize: 10 }} width={100} />
                      <Tooltip formatter={v => `${v}/20`} />
                      <Bar dataKey="note" radius={[0, 6, 6, 0]}>
                        {barDataS1.map((e, i) => <Cell key={i} fill={e.fill} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
                  <h3 className="text-sm font-bold text-gray-700 mb-4">Profil académique S2</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="#f1f5f9" />
                      <PolarAngleAxis dataKey="module" tick={{ fontSize: 9 }} />
                      <Radar dataKey="value" stroke="#1B3A6B" fill="#1B3A6B" fillOpacity={0.2} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {grades && (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                  <div className="px-5 py-4 border-b border-gray-100">
                    <h3 className="text-sm font-bold text-gray-700">Détail des notes</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="bg-gray-50">
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Module</th>
                          <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500">S1</th>
                          <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500">S2</th>
                          <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500">Statut</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-50">
                        {Object.keys({ ...grades.s1, ...grades.s2 })
                          .filter((v, i, a) => a.indexOf(v) === i)
                          .map(module => {
                            const s1  = grades.s1?.[module];
                            const s2  = grades.s2?.[module];
                            const avg = s1 && s2 ? (s1 + s2) / 2 : s1 || s2;
                            return (
                              <tr key={module} className="hover:bg-gray-50 transition-colors">
                                <td className="px-4 py-3 text-sm text-gray-700 font-medium">{module.replace(/_/g, " ")}</td>
                                <td className="px-4 py-3 text-center">
                                  {s1 ? <span className={`text-sm font-bold ${s1 >= 12 ? "text-green-600" : s1 >= 10 ? "text-yellow-600" : "text-red-600"}`}>{s1}</span>
                                      : <span className="text-gray-300">—</span>}
                                </td>
                                <td className="px-4 py-3 text-center">
                                  {s2 ? <span className={`text-sm font-bold ${s2 >= 12 ? "text-green-600" : s2 >= 10 ? "text-yellow-600" : "text-red-600"}`}>{s2}</span>
                                      : <span className="text-gray-300">—</span>}
                                </td>
                                <td className="px-4 py-3 text-center">
                                  <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
                                    avg >= 12 ? "bg-green-100 text-green-700"
                                    : avg >= 10 ? "bg-yellow-100 text-yellow-700"
                                    : "bg-red-100 text-red-700"
                                  }`}>
                                    {avg >= 12 ? "✓ Validé" : avg >= 10 ? "Passable" : "À risque"}
                                  </span>
                                </td>
                              </tr>
                            );
                          })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* RECOMMANDATIONS */}
          {activeTab === "recommendations" && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-black text-gray-800 tracking-tight">Recommandations reçues</h2>
                {unreadCount > 0 && (
                  <span className="bg-red-500 text-white text-xs px-2.5 py-1 rounded-full font-bold">
                    {unreadCount} non lue{unreadCount > 1 ? "s" : ""}
                  </span>
                )}
              </div>

              {recommendations.length === 0 ? (
                <div className="bg-white rounded-2xl p-12 shadow-sm border border-gray-100 text-center">
                  <p className="text-5xl mb-3">📭</p>
                  <p className="text-gray-400 text-sm">Aucune recommandation pour le moment</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {recommendations.map((rec) => {
                    const isExpanded = expandedRec === rec.id;
                    const isChefDept = rec.role?.includes("departement");
                    return (
                      <motion.div
                        key={rec.id}
                        layout
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        className={`bg-white rounded-2xl shadow-sm border overflow-hidden cursor-pointer ${
                          !rec.lu ? "border-[#1B3A6B]/30" : "border-gray-100"
                        }`}
                        onClick={() => handleOpenRec(rec)}
                      >
                        {!rec.lu && (
                          <div className="h-1 w-full bg-gradient-to-r from-[#1B3A6B] to-[#3b82f6]" />
                        )}
                        <div className="p-5">
                          <div className="flex items-start gap-4">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                              isChefDept ? "bg-orange-100" : "bg-blue-100"
                            }`}>
                              <span className={`text-sm font-black ${isChefDept ? "text-orange-700" : "text-blue-700"}`}>
                                {rec.expediteur?.[0]}
                              </span>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-2 flex-wrap">
                                <div className="flex items-center gap-2">
                                  <p className="text-sm font-bold text-gray-800">{rec.expediteur}</p>
                                  {!rec.lu && <span className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0" />}
                                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                    isChefDept ? "bg-orange-100 text-orange-700" : "bg-blue-100 text-blue-700"
                                  }`}>
                                    {isChefDept ? "Chef de département" : "Chef de filière"}
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <p className="text-xs text-gray-400">
                                    {new Date(rec.date).toLocaleDateString("fr-FR", { day: "numeric", month: "long" })}
                                  </p>
                                  <motion.svg
                                    animate={{ rotate: isExpanded ? 180 : 0 }}
                                    transition={{ duration: 0.2 }}
                                    className="w-4 h-4 text-gray-400 flex-shrink-0"
                                    fill="none" viewBox="0 0 24 24" stroke="currentColor"
                                  >
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                  </motion.svg>
                                </div>
                              </div>
                              <AnimatePresence initial={false}>
                                {isExpanded ? (
                                  <motion.p key="full"
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="text-sm text-gray-700 mt-3 leading-relaxed">
                                    {rec.message}
                                  </motion.p>
                                ) : (
                                  <motion.p key="preview"
                                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                                    className="text-sm text-gray-500 mt-2 line-clamp-1">
                                    {rec.message}
                                  </motion.p>
                                )}
                              </AnimatePresence>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              )}
            </motion.div>
          )}

        </main>
      )}
    </div>
  );
}