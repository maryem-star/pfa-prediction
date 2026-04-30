import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { motion } from "framer-motion";
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";
import api from "../services/api";

const ALL_FILIERES = ["ISIC", "CCN", "2ITE", "GC", "GI", "G2E"];

const RISK_COLORS = {
  success: "#22c55e",
  warning: "#f59e0b",
  danger: "#ef4444",
};

const FILIERE_COLORS = {
  ISIC: "#3b82f6", CCN: "#8b5cf6", "2ITE": "#06b6d4",
  GC: "#f59e0b", GI: "#10b981", G2E: "#f97316",
};

export default function AdminDashboard() {
  const { user, getAllowedFilieres, isAdmin, isChefDepartement, isChefFiliere } = useAuth();
  const navigate = useNavigate();

  const allowedFilieres = getAllowedFilieres();
  const visibleFilieres = allowedFilieres === null ? ALL_FILIERES : allowedFilieres;

  const [selectedFiliere, setSelectedFiliere] = useState(visibleFilieres[0] || "ISIC");
  const [stats, setStats] = useState(null);
  const [students, setStudents] = useState([]);
  const [loadingStats, setLoadingStats] = useState(true);

  // Role-based page title
  const getTitle = () => {
    if (isAdmin()) return "Dashboard — Vue Globale";
    if (isChefDepartement()) {
      const dept = user.role.includes("STIN") ? "STIN" : "TRI";
      return `Dashboard — Département ${dept}`;
    }
    if (isChefFiliere()) {
      const filiere = user.role.replace("chef_filiere_", "");
      return `Dashboard — Filière ${filiere}`;
    }
    return "Dashboard";
  };

  useEffect(() => {
    fetchStats();
    fetchStudents();
  }, [selectedFiliere]);

  const fetchStats = async () => {
    setLoadingStats(true);
    try {
      const res = await api.get("/dashboard/stats");
      setStats(res.data);
    } catch {
      // mock data for dev
      setStats({
        total_etudiants: 248,
        taux_reussite: 78.2,
        en_surveillance: 42,
        a_risque: 28,
        predictions_par_filiere: visibleFilieres.map(f => ({
          filiere: f,
          reussite: Math.floor(Math.random() * 30) + 50,
          moyen: Math.floor(Math.random() * 20) + 15,
          risque: Math.floor(Math.random() * 15) + 5,
        }))
      });
    } finally {
      setLoadingStats(false);
    }
  };

  const fetchStudents = async () => {
    try {
      const res = await api.get(`/v2/students/?filiere=${selectedFiliere}&limit=50`);
      setStudents(res.data);
    } catch {
      // mock
      setStudents(Array.from({ length: 12 }, (_, i) => ({
        id: i + 1,
        nom: ["Alaoui", "Benali", "Chakir", "Douiri", "El Fassi"][i % 5],
        prenom: ["Yassine", "Nadia", "Omar", "Sara", "Khalid"][i % 5],
        cne: `R${100000 + i}`,
        filiere: selectedFiliere,
        prediction: { statut_couleur: ["VERT", "JAUNE", "ROUGE"][Math.floor(Math.random() * 3)], probabilite: Math.random() * 0.5 + 0.5 }
      })));
    }
  };

  const getRiskBadge = (couleur) => {
    if (couleur === "VERT") return "bg-green-100 text-green-700 border border-green-200";
    if (couleur === "JAUNE") return "bg-yellow-100 text-yellow-700 border border-yellow-200";
    if (couleur === "ROUGE") return "bg-red-100 text-red-700 border border-red-200";
    return "bg-gray-100 text-gray-500";
  };

  const getRiskLabel = (couleur) => {
    if (couleur === "VERT") return "En bonne voie";
    if (couleur === "JAUNE") return "À surveiller";
    if (couleur === "ROUGE") return "À risque";
    return "Non évalué";
  };

  const pieData = [
    { name: "Réussite", value: stats?.taux_reussite || 78, color: RISK_COLORS.success },
    { name: "Moyen", value: Math.round((stats?.en_surveillance / (stats?.total_etudiants || 248)) * 100) || 17, color: RISK_COLORS.warning },
    { name: "À risque", value: Math.round((stats?.a_risque / (stats?.total_etudiants || 248)) * 100) || 11, color: RISK_COLORS.danger },
  ];

  const statCards = [
    { label: "Total étudiants", value: stats?.total_etudiants ?? "—", icon: "👥", color: "text-blue-600", bg: "bg-blue-50" },
    { label: "Taux de réussite", value: stats?.taux_reussite ? `${stats.taux_reussite}%` : "—", icon: "✅", color: "text-green-600", bg: "bg-green-50" },
    { label: "En surveillance", value: stats?.en_surveillance ?? "—", icon: "⚠️", color: "text-yellow-600", bg: "bg-yellow-50" },
    { label: "À risque", value: stats?.a_risque ?? "—", icon: "🔴", color: "text-red-600", bg: "bg-red-50" },
  ];

  return (
    <Layout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-800">{getTitle()}</h1>
          <p className="text-sm text-gray-500 mt-1">
            Suivi des prédictions de réussite — {visibleFilieres.join(", ")}
          </p>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map((card, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100"
            >
              <div className={`w-10 h-10 rounded-xl ${card.bg} flex items-center justify-center text-xl mb-3`}>
                {card.icon}
              </div>
              <p className="text-2xl font-bold text-gray-800">{card.value}</p>
              <p className="text-xs text-gray-500 mt-1">{card.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pie */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Répartition globale</h2>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} dataKey="value" label={({ name, value }) => `${name} ${value}%`} labelLine={false}>
                  {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip formatter={(v) => `${v}%`} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Bar by filiere */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Par filière</h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={stats?.predictions_par_filiere || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis dataKey="filiere" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="reussite" name="Réussite" fill={RISK_COLORS.success} radius={[4,4,0,0]} />
                <Bar dataKey="moyen" name="Moyen" fill={RISK_COLORS.warning} radius={[4,4,0,0]} />
                <Bar dataKey="risque" name="À risque" fill={RISK_COLORS.danger} radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Students by filiere */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-5 border-b border-gray-100 flex items-center justify-between flex-wrap gap-3">
            <h2 className="text-sm font-semibold text-gray-700">Étudiants par filière</h2>
            {/* Filiere tabs */}
            <div className="flex gap-2 flex-wrap">
              {visibleFilieres.map(f => (
                <button
                  key={f}
                  onClick={() => setSelectedFiliere(f)}
                  className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                    selectedFiliere === f
                      ? "text-white shadow-sm"
                      : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                  }`}
                  style={selectedFiliere === f ? { backgroundColor: FILIERE_COLORS[f] || "#1B3A6B" } : {}}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Étudiant</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">CNE</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Statut prédiction</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Probabilité</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {students.map((s) => (
                  <tr
                    key={s.id}
                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => navigate(`/students/${s.id}/stats`)}
                  >
                    <td className="px-4 py-3">
                      <p className="text-sm font-medium text-gray-800">{s.prenom} {s.nom}</p>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">{s.cne}</td>
                    <td className="px-4 py-3">
                      {s.prediction ? (
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${getRiskBadge(s.prediction.statut_couleur)}`}>
                          {getRiskLabel(s.prediction.statut_couleur)}
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">Non évalué</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {s.prediction?.probabilite ? (
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-100 rounded-full h-1.5 w-20">
                            <div
                              className="h-1.5 rounded-full"
                              style={{
                                width: `${Math.round(s.prediction.probabilite * 100)}%`,
                                backgroundColor: s.prediction.statut_couleur === "VERT" ? RISK_COLORS.success : s.prediction.statut_couleur === "JAUNE" ? RISK_COLORS.warning : RISK_COLORS.danger
                              }}
                            />
                          </div>
                          <span className="text-xs text-gray-600">{Math.round(s.prediction.probabilite * 100)}%</span>
                        </div>
                      ) : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={(e) => { e.stopPropagation(); navigate(`/students/${s.id}/stats`); }}
                        className="text-xs text-[#1B3A6B] hover:underline font-medium"
                      >
                        Voir statistiques →
                      </button>
                    </td>
                  </tr>
                ))}
                {students.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-400 text-sm">
                      Aucun étudiant dans cette filière
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
}