import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, Legend
} from "recharts";
import Layout from "../components/Layout";

// ─── Mock Data ───────────────────────────────────────────────────────────────
const FILIERES = ["Tous", "ISIC", "CCN", "2ITE", "GC", "GI", "G2E"];

const mockStudents = [
  // ISIC
  { id: 1, name: "Yassine Alaoui", filiere: "ISIC", score: 87, status: "success" },
  { id: 2, name: "Nadia Benali", filiere: "ISIC", score: 72, status: "warning" },
  { id: 3, name: "Omar Tahiri", filiere: "ISIC", score: 41, status: "danger" },
  { id: 4, name: "Salma Idrissi", filiere: "ISIC", score: 91, status: "success" },
  // CCN
  { id: 5, name: "Hamza Bouazza", filiere: "CCN", score: 65, status: "warning" },
  { id: 6, name: "Fatima Zahra", filiere: "CCN", score: 88, status: "success" },
  { id: 7, name: "Amine Rami", filiere: "CCN", score: 35, status: "danger" },
  // 2ITE
  { id: 8, name: "Karim Mansouri", filiere: "2ITE", score: 79, status: "success" },
  { id: 9, name: "Layla Chraibi", filiere: "2ITE", score: 58, status: "warning" },
  { id: 10, name: "Reda Filali", filiere: "2ITE", score: 29, status: "danger" },
  // GC
  { id: 11, name: "Sara Tazi", filiere: "GC", score: 93, status: "success" },
  { id: 12, name: "Bilal Hassani", filiere: "GC", score: 67, status: "warning" },
  { id: 13, name: "Imane Bouchaib", filiere: "GC", score: 44, status: "danger" },
  // GI
  { id: 14, name: "Mehdi Ouali", filiere: "GI", score: 85, status: "success" },
  { id: 15, name: "Zineb Amrani", filiere: "GI", score: 71, status: "warning" },
  { id: 16, name: "Tariq Bennani", filiere: "GI", score: 38, status: "danger" },
  // G2E
  { id: 17, name: "Houda Kettani", filiere: "G2E", score: 90, status: "success" },
  { id: 18, name: "Youssef Mrabet", filiere: "G2E", score: 63, status: "warning" },
  { id: 19, name: "Asmaa Lahcen", filiere: "G2E", score: 47, status: "danger" },
  { id: 20, name: "Soufiane Benkirane", filiere: "G2E", score: 82, status: "success" },
];

const pieData = [
  { name: "Réussite", value: 58, color: "#22c55e" },
  { name: "Moyen", value: 27, color: "#eab308" },
  { name: "À risque", value: 15, color: "#ef4444" },
];

const barData = FILIERES.slice(1).map((f) => {
  const students = mockStudents.filter((s) => s.filiere === f);
  return {
    filiere: f,
    Réussite: students.filter((s) => s.status === "success").length,
    Moyen: students.filter((s) => s.status === "warning").length,
    Risque: students.filter((s) => s.status === "danger").length,
  };
});

// ─── Sub-components ──────────────────────────────────────────────────────────
const StatCard = ({ icon, label, value, sub, color, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
    className="relative bg-slate-900 border border-slate-800 rounded-xl p-5 overflow-hidden"
  >
    <div className={`absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-${color}-500/40 to-transparent`} />
    <div className="flex items-start justify-between">
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{label}</p>
        <p className="text-3xl font-bold text-white">{value}</p>
        <p className={`text-xs mt-1 text-${color}-400`}>{sub}</p>
      </div>
      <div className={`p-2.5 rounded-lg bg-${color}-500/10 border border-${color}-500/20 text-${color}-400`}>
        {icon}
      </div>
    </div>
  </motion.div>
);

const statusConfig = {
  success: {
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    text: "text-emerald-400",
    badge: "bg-emerald-500/20 text-emerald-300",
    dot: "bg-emerald-400",
    label: "Réussite",
  },
  warning: {
    bg: "bg-yellow-500/10",
    border: "border-yellow-500/30",
    text: "text-yellow-400",
    badge: "bg-yellow-500/20 text-yellow-300",
    dot: "bg-yellow-400",
    label: "Moyen",
  },
  danger: {
    bg: "bg-red-500/10",
    border: "border-red-500/30",
    text: "text-red-400",
    badge: "bg-red-500/20 text-red-300",
    dot: "bg-red-400",
    label: "À risque",
  },
};

const CustomTooltip = ({ active, payload }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white shadow-xl">
        {payload.map((p) => (
          <div key={p.name} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ background: p.fill }} />
            {p.name}: <strong>{p.value}</strong>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

// ─── Alert Card ──────────────────────────────────────────────────────────────
const AlertCard = ({ student }) => (
  <div className="flex items-center gap-3 p-3 bg-red-500/5 border border-red-500/20 rounded-lg">
    <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse shrink-0" />
    <div className="flex-1 min-w-0">
      <p className="text-sm font-medium text-white truncate">{student.name}</p>
      <p className="text-xs text-slate-400">{student.filiere} — Score: {student.score}%</p>
    </div>
    <span className="text-xs bg-red-500/20 text-red-300 px-2 py-0.5 rounded-full shrink-0">Risque</span>
  </div>
);

// ─── Main Dashboard ───────────────────────────────────────────────────────────
const AdminDashboard = () => {
  const [selectedFiliere, setSelectedFiliere] = useState("Tous");
  const [sortBy, setSortBy] = useState("status");

  const filteredStudents = mockStudents
    .filter((s) => selectedFiliere === "Tous" || s.filiere === selectedFiliere)
    .sort((a, b) => {
      if (sortBy === "status") {
        const order = { danger: 0, warning: 1, success: 2 };
        return order[a.status] - order[b.status];
      }
      return b.score - a.score;
    });

  const atRisk = mockStudents.filter((s) => s.status === "danger");
  const successCount = mockStudents.filter((s) => s.status === "success").length;
  const warningCount = mockStudents.filter((s) => s.status === "warning").length;

  return (
    <Layout>
      <div className="min-h-full p-6 space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard Administrateur</h1>
            <p className="text-sm text-slate-400 mt-0.5">Vue d'ensemble — Année 2024/2025</p>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Données en temps réel
          </div>
        </motion.div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard
            delay={0.05}
            color="cyan"
            label="Total Étudiants"
            value={mockStudents.length}
            sub="Toutes filières"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>}
          />
          <StatCard
            delay={0.1}
            color="emerald"
            label="Taux de Réussite"
            value={`${Math.round((successCount / mockStudents.length) * 100)}%`}
            sub={`${successCount} étudiants`}
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          />
          <StatCard
            delay={0.15}
            color="yellow"
            label="En Surveillance"
            value={warningCount}
            sub="Prédictions moyennes"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>}
          />
          <StatCard
            delay={0.2}
            color="red"
            label="À Risque"
            value={atRisk.length}
            sub="Intervention requise"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>}
          />
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Pie chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25, duration: 0.4 }}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5"
          >
            <h2 className="text-sm font-semibold text-slate-300 mb-4">Répartition des Prédictions</h2>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} stroke="transparent" />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  formatter={(value) => <span className="text-xs text-slate-400">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Bar chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.4 }}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5"
          >
            <h2 className="text-sm font-semibold text-slate-300 mb-4">Prédictions par Filière</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} barSize={14}>
                <XAxis dataKey="filiere" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                <Bar dataKey="Réussite" fill="#22c55e" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Moyen" fill="#eab308" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Risque" fill="#ef4444" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Bottom row: students list + alerts */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          {/* Students list with filiere filter */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35, duration: 0.4 }}
            className="xl:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5"
          >
            {/* Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
              <h2 className="text-sm font-semibold text-slate-300">Liste des Étudiants</h2>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Trier:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="text-xs bg-slate-800 border border-slate-700 text-slate-300 rounded-lg px-2 py-1 outline-none"
                >
                  <option value="status">Par statut</option>
                  <option value="score">Par score</option>
                </select>
              </div>
            </div>

            {/* Filiere tabs */}
            <div className="flex flex-wrap gap-1.5 mb-4">
              {FILIERES.map((f) => (
                <button
                  key={f}
                  onClick={() => setSelectedFiliere(f)}
                  className={`px-3 py-1 text-xs font-medium rounded-full border transition-all duration-150 ${
                    selectedFiliere === f
                      ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-300"
                      : "bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600"
                  }`}
                >
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
                    <motion.div
                      key={student.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 10 }}
                      transition={{ delay: i * 0.03 }}
                      className={`flex items-center gap-3 p-3 rounded-lg border ${cfg.bg} ${cfg.border} cursor-pointer hover:brightness-110 transition-all`}
                    >
                      {/* Avatar */}
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${cfg.badge} shrink-0`}>
                        {student.name.split(" ").map((n) => n[0]).join("").slice(0, 2)}
                      </div>
                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">{student.name}</p>
                        <p className="text-xs text-slate-400">{student.filiere}</p>
                      </div>
                      {/* Score bar */}
                      <div className="w-24 hidden sm:block">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-slate-400">Score</span>
                          <span className={`text-xs font-semibold ${cfg.text}`}>{student.score}%</span>
                        </div>
                        <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${cfg.dot}`}
                            style={{ width: `${student.score}%` }}
                          />
                        </div>
                      </div>
                      {/* Badge */}
                      <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${cfg.badge}`}>
                        {cfg.label}
                      </span>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
            <p className="text-xs text-slate-600 mt-3">{filteredStudents.length} étudiant(s) affiché(s)</p>
          </motion.div>

          {/* Alerts panel */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.4 }}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5"
          >
            <div className="flex items-center gap-2 mb-4">
              <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
              <h2 className="text-sm font-semibold text-slate-300">Alertes — Étudiants à Risque</h2>
            </div>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {atRisk.map((s) => (
                <AlertCard key={s.id} student={s} />
              ))}
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800">
              <p className="text-xs text-slate-500">{atRisk.length} étudiants nécessitent une intervention immédiate</p>
            </div>
          </motion.div>
        </div>
      </div>
    </Layout>
  );
};

export default AdminDashboard;