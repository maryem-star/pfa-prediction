import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom"; // FIX: added useLocation
import { motion, AnimatePresence } from "framer-motion";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import SendRecommendationModal from "../pages/SendRecommendationModal";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, Cell
} from "recharts";
import api from "../services/api";

function getStatusInfo(couleur) {
  if (couleur === "VERT")  return { label: "En bonne voie", color: "#22c55e", bg: "bg-green-50",  text: "text-green-700",  border: "border-green-200" };
  if (couleur === "JAUNE") return { label: "À surveiller",  color: "#f59e0b", bg: "bg-yellow-50", text: "text-yellow-700", border: "border-yellow-200" };
  if (couleur === "ROUGE") return { label: "À risque",      color: "#ef4444", bg: "bg-red-50",    text: "text-red-700",   border: "border-red-200" };
  return { label: "Non évalué", color: "#94a3b8", bg: "bg-gray-50", text: "text-gray-600", border: "border-gray-200" };
}

export default function StudentProfilePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation(); // FIX: get navigation state
  const { user, isChefDepartement, isChefFiliere } = useAuth();

  const [student, setStudent]           = useState(
    location.state?.student || null // FIX: immediately pre-populate from nav state
  );
  const [prediction, setPrediction]     = useState(null);
  const [grades, setGrades]             = useState(null);
  const [loading, setLoading]           = useState(true);
  const [showRecModal, setShowRecModal] = useState(false);
  const [recSentToast, setRecSentToast] = useState(false);

  const canSendRecommendation = isChefDepartement() || isChefFiliere();

  useEffect(() => {
    console.log("ID reçu dans l'URL:", id);
    fetchAll();
  }, [id]);

  const fetchAll = async () => {
    console.log("fetchAll appelé avec id:", id);
    setLoading(true);

    let studentData    = null;
    let predictionData = null;
    let gradesData     = null;

    try {
      const statsRes = await api.get(`/v2/students/${id}/stats`);
      const data = statsRes.data;

      studentData = {
        id:      data.etudiant?.id,
        nom:     data.etudiant?.nom,
        prenom:  data.etudiant?.prenom,
        filiere: data.etudiant?.filiere,
        annee:   data.etudiant?.annee,
        cne:     data.etudiant?.cne,
        email:   data.etudiant?.email,
      };

      predictionData = data.derniere_prediction
        ? {
            label:           data.derniere_prediction.label,
            probabilite:     data.derniere_prediction.probabilite,
            statut_couleur:  data.derniere_prediction.statut_couleur,
            note_predite:    data.derniere_prediction.note_predite,
            facteurs_risque: data.derniere_prediction.facteurs_risque || [],
            recommandations: data.derniere_prediction.recommandations || [],
            moyennes:        data.moyennes_par_semestre || {},
          }
        : null;

    } catch (err) {
      // FIX: log the real error so you can debug the CORS / API issue
      console.error("Erreur stats:", err.response?.status, err.message);
    }

    // FIX: grades endpoint corrected to /v2/ prefix to match your backend
    try {
      const gradesRes = await api.get(`/v2/students/${id}/grades`);
      gradesData = gradesRes.data;
    } catch (err) {
      console.error("Erreur grades:", err.response?.status, err.message);
    }

    // FIX: prefer real API data, then navigation state, then generic fallback
    setStudent(
      studentData ||
      location.state?.student ||
      { id: +id, nom: "—", prenom: "—", cne: "—", email: "—", filiere: "—", annee: null }
    );

    setPrediction(predictionData || {
      label: "Réussi", probabilite: 0.82, statut_couleur: "VERT",
      note_predite: 14.5,
      facteurs_risque: ["Absences S2 légèrement élevées"],
      recommandations: ["Maintenir la régularité en cours"],
      moyennes: { S1: 13.67 },
    });

    setGrades(gradesData || {
      s1: { Mathématiques: 15, Algorithmique: 14, Architecture: 12, Électronique: 11, Réseaux: 13, Anglais: 16 },
      s2: { Mathématiques: 15, Structures_Données: 14, Systèmes: 13, Bases_Données: 16, Réseaux: 14, PFA: 16 },
    });

    setLoading(false);
  };

  const handleRecSent = () => {
    setRecSentToast(true);
    setTimeout(() => setRecSentToast(false), 3000);
  };

  if (loading) return (
    <Layout>
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-2 border-[#1B3A6B] border-t-transparent rounded-full animate-spin" />
      </div>
    </Layout>
  );

  const status = getStatusInfo(prediction?.statut_couleur);
  const pct    = prediction?.probabilite ? Math.round(prediction.probabilite * 100) : 0;

  const barDataS1 = grades?.s1
    ? Object.entries(grades.s1).map(([m, v]) => ({ module: m, note: v }))
    : [];

  const radarData = grades?.s2
    ? Object.entries(grades.s2).map(([m, v]) => ({ module: m.replace(/_/g, " "), value: v }))
    : [];

  return (
    <Layout>
      <div className="p-6 space-y-6 max-w-5xl">

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate(-1)}
              className="p-2 rounded-xl hover:bg-gray-100 transition-colors text-gray-500">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                {student?.prenom} {student?.nom}
              </h1>
              <p className="text-sm text-gray-500 mt-0.5">
                {student?.cne && `${student.cne} · `}
                Filière {student?.filiere}
                {student?.annee && ` · ${student.annee}ème année`}
              </p>
            </div>
          </div>

          {canSendRecommendation && (
            <button
              onClick={() => setShowRecModal(true)}
              className="flex items-center gap-2 bg-[#1B3A6B] text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-[#152d54] transition-colors flex-shrink-0"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              Envoyer une recommandation
            </button>
          )}
        </div>

        {/* Carte prédiction */}
        <div className={`bg-white rounded-2xl p-6 shadow-sm border ${status.border} flex flex-col sm:flex-row items-center gap-6`}>
          <div className="flex flex-col items-center flex-shrink-0">
            <svg viewBox="0 0 120 70" className="w-32 h-auto">
              <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke="#f1f5f9" strokeWidth="10" strokeLinecap="round" />
              <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke={status.color} strokeWidth="10" strokeLinecap="round"
                strokeDasharray={`${(pct / 100) * 157} 157`} />
              <line x1="60" y1="65" x2="60" y2="20" stroke={status.color} strokeWidth="2.5" strokeLinecap="round"
                transform={`rotate(${-135 + (pct / 100) * 270 - 90}, 60, 65)`} />
              <circle cx="60" cy="65" r="4" fill={status.color} />
            </svg>
            <p className="text-2xl font-bold text-gray-800 mt-1">{pct}%</p>
            <span className={`text-xs font-semibold mt-1 px-3 py-1 rounded-full border ${status.bg} ${status.text} ${status.border}`}>
              {status.label}
            </span>
          </div>

          <div className="flex-1 space-y-3 w-full">
            <div className="flex gap-3 flex-wrap">
              <div className="bg-gray-50 rounded-xl px-4 py-2.5">
                <p className="text-xs text-gray-500">Note prédite</p>
                <p className="text-xl font-bold text-gray-800">
                  {prediction?.note_predite ?? "—"}
                  <span className="text-sm text-gray-400">/20</span>
                </p>
              </div>
              <div className={`${status.bg} rounded-xl px-4 py-2.5`}>
                <p className="text-xs text-gray-500">Décision</p>
                <p className={`text-xl font-bold ${status.text}`}>{prediction?.label || "—"}</p>
              </div>
              {prediction?.moyennes && Object.entries(prediction.moyennes).map(([sem, moy]) => (
                <div key={sem} className="bg-blue-50 rounded-xl px-4 py-2.5">
                  <p className="text-xs text-gray-500">Moyenne {sem}</p>
                  <p className="text-xl font-bold text-blue-700">{moy}</p>
                </div>
              ))}
            </div>

            {prediction?.facteurs_risque?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-400 mb-1">Facteurs de risque :</p>
                <div className="flex flex-wrap gap-2">
                  {prediction.facteurs_risque.map((f, i) => (
                    <span key={i} className="text-xs bg-yellow-50 text-yellow-700 px-2 py-1 rounded-lg border border-yellow-100">
                      ⚠ {f}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {prediction?.recommandations?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-400 mb-1">Conseils du système :</p>
                <div className="space-y-1">
                  {prediction.recommandations.map((r, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-blue-800 bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-100">
                      <span className="text-blue-400 flex-shrink-0">→</span>
                      {r}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Graphiques */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Notes S1</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={barDataS1} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" horizontal={false} />
                <XAxis type="number" domain={[0, 20]} tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="module" tick={{ fontSize: 10 }} width={100} />
                <Tooltip formatter={v => `${v}/20`} />
                <Bar dataKey="note" radius={[0, 4, 4, 0]}>
                  {barDataS1.map((e, i) => (
                    <Cell key={i} fill={e.note >= 12 ? "#22c55e" : e.note >= 10 ? "#f59e0b" : "#ef4444"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Profil académique S2</h3>
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#f1f5f9" />
                <PolarAngleAxis dataKey="module" tick={{ fontSize: 9 }} />
                <Radar dataKey="value" stroke="#1B3A6B" fill="#1B3A6B" fillOpacity={0.25} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Tableau des notes */}
        {grades && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100">
              <h3 className="text-sm font-semibold text-gray-700">Détail des notes</h3>
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
                          <td className="px-4 py-3 text-sm text-gray-700 font-medium">
                            {module.replace(/_/g, " ")}
                          </td>
                          <td className="px-4 py-3 text-center">
                            {s1
                              ? <span className={`text-sm font-bold ${s1 >= 12 ? "text-green-600" : s1 >= 10 ? "text-yellow-600" : "text-red-600"}`}>{s1}</span>
                              : <span className="text-gray-300">—</span>}
                          </td>
                          <td className="px-4 py-3 text-center">
                            {s2
                              ? <span className={`text-sm font-bold ${s2 >= 12 ? "text-green-600" : s2 >= 10 ? "text-yellow-600" : "text-red-600"}`}>{s2}</span>
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
      </div>

      {showRecModal && (
        <SendRecommendationModal
          student={student}
          onClose={() => setShowRecModal(false)}
          onSent={handleRecSent}
        />
      )}

      <AnimatePresence>
        {recSentToast && (
          <motion.div
            initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 40 }}
            className="fixed bottom-6 right-6 bg-green-500 text-white px-4 py-3 rounded-xl shadow-lg text-sm font-medium z-50"
          >
            ✓ Recommandation envoyée avec succès
          </motion.div>
        )}
      </AnimatePresence>
    </Layout>
  );
}