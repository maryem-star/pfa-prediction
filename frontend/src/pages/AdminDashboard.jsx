import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import Layout from "../components/Layout";

const FILIERES = ["Tous", "ISIC", "CCN", "2ITE", "GC", "GI", "G2E"];

const mockStudents = [
  { id: 1,  name: "Yassine Alaoui",      filiere: "ISIC", score: 87, status: "success" },
  { id: 2,  name: "Nadia Benali",         filiere: "ISIC", score: 72, status: "warning" },
  { id: 3,  name: "Omar Tahiri",          filiere: "ISIC", score: 41, status: "danger"  },
  { id: 4,  name: "Salma Idrissi",        filiere: "ISIC", score: 91, status: "success" },
  { id: 5,  name: "Hamza Bouazza",        filiere: "CCN",  score: 65, status: "warning" },
  { id: 6,  name: "Fatima Zahra",         filiere: "CCN",  score: 88, status: "success" },
  { id: 7,  name: "Amine Rami",           filiere: "CCN",  score: 35, status: "danger"  },
  { id: 8,  name: "Karim Mansouri",       filiere: "2ITE", score: 79, status: "success" },
  { id: 9,  name: "Layla Chraibi",        filiere: "2ITE", score: 58, status: "warning" },
  { id: 10, name: "Reda Filali",          filiere: "2ITE", score: 29, status: "danger"  },
  { id: 11, name: "Sara Tazi",            filiere: "GC",   score: 93, status: "success" },
  { id: 12, name: "Bilal Hassani",        filiere: "GC",   score: 67, status: "warning" },
  { id: 13, name: "Imane Bouchaib",       filiere: "GC",   score: 44, status: "danger"  },
  { id: 14, name: "Mehdi Ouali",          filiere: "GI",   score: 85, status: "success" },
  { id: 15, name: "Zineb Amrani",         filiere: "GI",   score: 71, status: "warning" },
  { id: 16, name: "Tariq Bennani",        filiere: "GI",   score: 38, status: "danger"  },
  { id: 17, name: "Houda Kettani",        filiere: "G2E",  score: 90, status: "success" },
  { id: 18, name: "Youssef Mrabet",       filiere: "G2E",  score: 63, status: "warning" },
  { id: 19, name: "Asmaa Lahcen",         filiere: "G2E",  score: 47, status: "danger"  },
  { id: 20, name: "Soufiane Benkirane",   filiere: "G2E",  score: 82, status: "success" },
];

const pieData = [
  { name: "Réussite", value: 58, color: "#16a34a" },
  { name: "Moyen",    value: 27, color: "#d97706" },
  { name: "À risque", value: 15, color: "#dc2626" },
];

const barData = FILIERES.slice(1).map((f) => {
  const s = mockStudents.filter((x) => x.filiere === f);
  return {
    filiere: f,
    Réussite: s.filter((x) => x.status === "success").length,
    Moyen:    s.filter((x) => x.status === "warning").length,
    Risque:   s.filter((x) => x.status === "danger").length,
  };
});

const statusConfig = {
  success: { bg: "#f0fdf4", border: "#bbf7d0", text: "#16a34a", badge: { bg: "#dcfce7", color: "#15803d" }, dot: "#22c55e", label: "Réussite" },
  warning: { bg: "#fffbeb", border: "#fde68a", text: "#d97706", badge: { bg: "#fef3c7", color: "#b45309" }, dot: "#f59e0b", label: "Moyen"    },
  danger:  { bg: "#fff1f2", border: "#fecaca", text: "#dc2626", badge: { bg: "#fee2e2", color: "#b91c1c" }, dot: "#ef4444", label: "À risque" },
};

const StatCard = ({ icon, label, value, sub, color, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
    className="relative bg-white rounded-xl p-5 shadow-sm border"
    style={{ borderColor: "#e5e7eb", borderLeftWidth: 4, borderLeftColor: color }}
  >
    <div className="flex items-start justify-between">
      <div>
        <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">{label}</p>
        <p className="text-3xl font-bold" style={{ color: "#1e293b" }}>{value}</p>
        <p className="text-xs mt-1 font-medium" style={{ color }}>{sub}</p>
      </div>
      <div className="p-2.5 rounded-xl" style={{ background: color + "18" }}>
        <span style={{ color }}>{icon}</span>
      </div>
    </div>
  </motion.div>
);

const CustomTooltip = ({ active, payload }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs shadow-lg">
        {payload.map((p) => (
          <div key={p.name} className="flex items-center gap-2 text-gray-700">
            <span className="w-2 h-2 rounded-full" style={{ background: p.fill }} />
            {p.name}: <strong>{p.value}</strong>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

const AdminDashboard = () => {
  const [selectedFiliere, setSelectedFiliere] = useState("Tous");
  const [sortBy, setSortBy] = useState("status");

  const filteredStudents = mockStudents
    .filter((s) => selectedFiliere === "Tous" || s.filiere === selectedFiliere)
    .sort((a, b) => {
      if (sortBy === "status") { const o = { danger: 0, warning: 1, success: 2 }; return o[a.status] - o[b.status]; }
      return b.score - a.score;
    });

  const atRisk      = mockStudents.filter((s) => s.status === "danger");
  const successCount = mockStudents.filter((s) => s.status === "success").length;
  const warningCount = mockStudents.filter((s) => s.status === "warning").length;

  return (
    <Layout>
      <div className="min-h-full p-6 space-y-6">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold" style={{ color: "#1e293b" }}>Dashboard Administrateur</h1>
            <p className="text-sm text-gray-400 mt-0.5">Vue d'ensemble — Année 2024/2025</p>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400 bg-white border border-gray-200 rounded-xl px-3 py-2 shadow-sm">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            Données en temps réel
          </div>
        </motion.div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard delay={0.05} color="#1e56a0" label="Total Étudiants" value={mockStudents.length} sub="Toutes filières"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>}
          />
          <StatCard delay={0.1} color="#16a34a" label="Taux de Réussite" value={`${Math.round((successCount / mockStudents.length) * 100)}%`} sub={`${successCount} étudiants`}
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          />
          <StatCard delay={0.15} color="#d97706" label="En Surveillance" value={warningCount} sub="Prédictions moyennes"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>}
          />
          <StatCard delay={0.2} color="#dc2626" label="À Risque" value={atRisk.length} sub="Intervention requise"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Répartition des Prédictions</h2>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={85} paddingAngle={3} dataKey="value">
                  {pieData.map((entry, i) => <Cell key={i} fill={entry.color} stroke="transparent" />)}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend formatter={(v) => <span className="text-xs text-gray-500">{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Prédictions par Filière</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} barSize={14}>
                <XAxis dataKey="filiere" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
                <Bar dataKey="Réussite" fill="#16a34a" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Moyen"    fill="#d97706" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Risque"   fill="#dc2626" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Students + Alerts */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          {/* Student list */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            className="xl:col-span-2 bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
              <h2 className="text-sm font-semibold text-gray-700">Liste des Étudiants</h2>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">Trier:</span>
                <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}
                  className="text-xs border border-gray-200 text-gray-600 rounded-lg px-2 py-1 outline-none bg-gray-50">
                  <option value="status">Par statut</option>
                  <option value="score">Par score</option>
                </select>
              </div>
            </div>

            {/* Filiere tabs */}
            <div className="flex flex-wrap gap-1.5 mb-4">
              {FILIERES.map((f) => (
                <button key={f} onClick={() => setSelectedFiliere(f)}
                  className="px-3 py-1 text-xs font-semibold rounded-full border transition-all duration-150"
                  style={selectedFiliere === f
                    ? { background: "#1e56a0", color: "#fff", borderColor: "#1e56a0" }
                    : { background: "#f9fafb", color: "#6b7280", borderColor: "#e5e7eb" }}>
                  {f}
                </button>
              ))}
            </div>

            {/* Student rows */}
            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              <AnimatePresence mode="popLayout">
                {filteredStudents.map((student, i) => {
                  const cfg = statusConfig[student.status];
                  return (
                    <motion.div key={student.id}
                      initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 10 }} transition={{ delay: i * 0.03 }}
                      className="flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all hover:shadow-sm"
                      style={{ background: cfg.bg, borderColor: cfg.border }}>
                      {/* Avatar */}
                      <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
                        style={{ background: cfg.badge.bg, color: cfg.badge.color }}>
                        {student.name.split(" ").map((n) => n[0]).join("").slice(0, 2)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-800 truncate">{student.name}</p>
                        <p className="text-xs text-gray-400">{student.filiere}</p>
                      </div>
                      {/* Score bar */}
                      <div className="w-24 hidden sm:block">
                        <div className="flex justify-between mb-1">
                          <span className="text-xs text-gray-400">Score</span>
                          <span className="text-xs font-bold" style={{ color: cfg.text }}>{student.score}%</span>
                        </div>
                        <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: `${student.score}%`, background: cfg.dot }} />
                        </div>
                      </div>
                      <span className="text-xs px-2 py-0.5 rounded-full font-medium shrink-0"
                        style={{ background: cfg.badge.bg, color: cfg.badge.color }}>
                        {cfg.label}
                      </span>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
            <p className="text-xs text-gray-400 mt-3">{filteredStudents.length} étudiant(s) affiché(s)</p>
          </motion.div>

          {/* Alerts */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
              <h2 className="text-sm font-semibold text-gray-700">Alertes — Étudiants à Risque</h2>
            </div>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {atRisk.map((s) => (
                <div key={s.id} className="flex items-center gap-3 p-3 rounded-xl border"
                  style={{ background: "#fff1f2", borderColor: "#fecaca" }}>
                  <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-800 truncate">{s.name}</p>
                    <p className="text-xs text-gray-400">{s.filiere} — Score: {s.score}%</p>
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded-full font-medium shrink-0"
                    style={{ background: "#fee2e2", color: "#b91c1c" }}>Risque</span>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-3 border-t border-gray-100">
              <p className="text-xs text-gray-400">{atRisk.length} étudiants nécessitent une intervention</p>
            </div>
          </motion.div>
        </div>
      </div>
    </Layout>
  );
};

export default AdminDashboard;