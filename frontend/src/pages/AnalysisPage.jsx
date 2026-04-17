import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Legend, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis
} from "recharts";
import Layout from "../components/Layout";
import api from "../services/api";

const mockTrends = [
  { mois: "Oct", reussite: 62, moyen: 25, risque: 13 },
  { mois: "Nov", reussite: 65, moyen: 23, risque: 12 },
  { mois: "Dec", reussite: 58, moyen: 28, risque: 14 },
  { mois: "Jan", reussite: 70, moyen: 20, risque: 10 },
  { mois: "Fev", reussite: 72, moyen: 19, risque: 9  },
  { mois: "Mar", reussite: 75, moyen: 18, risque: 7  },
];
const mockFiliereStats = [
  { filiere: "ISIC", reussite: 78, moyen: 15, risque: 7  },
  { filiere: "CCN",  reussite: 65, moyen: 22, risque: 13 },
  { filiere: "2ITE", reussite: 72, moyen: 18, risque: 10 },
  { filiere: "GC",   reussite: 80, moyen: 14, risque: 6  },
  { filiere: "GI",   reussite: 68, moyen: 20, risque: 12 },
  { filiere: "G2E",  reussite: 74, moyen: 17, risque: 9  },
];
const mockModuleAvg = [
  { module: "Maths 1",   moyenne: 13.5 },
  { module: "Algo",      moyenne: 14.2 },
  { module: "Archi",     moyenne: 12.8 },
  { module: "Electro",   moyenne: 11.9 },
  { module: "Reseaux 1", moyenne: 13.1 },
  { module: "Maths 2",   moyenne: 14.0 },
  { module: "Struct.",   moyenne: 13.7 },
  { module: "Sys. Exp.", moyenne: 12.5 },
  { module: "BD",        moyenne: 15.1 },
  { module: "Reseaux 2", moyenne: 13.9 },
];
const mockRadar = [
  { subject: "Maths",    score: 13.5 },
  { subject: "Info",     score: 14.8 },
  { subject: "Reseaux",  score: 13.2 },
  { subject: "Langues",  score: 15.0 },
  { subject: "Systemes", score: 12.5 },
  { subject: "BD",       score: 15.1 },
];
const mockAbsences = [
  { range: "0-2",  count: 45 },
  { range: "3-5",  count: 32 },
  { range: "6-10", count: 18 },
  { range: ">10",  count: 8  },
];
const correlationData = [
  { module: "Bases de Donnees",     moyenne: 15.1, correlation: 0.87, impact: "Tres eleve" },
  { module: "Algorithmique",        moyenne: 14.2, correlation: 0.82, impact: "Tres eleve" },
  { module: "Mathematiques 2",      moyenne: 14.0, correlation: 0.79, impact: "Eleve"      },
  { module: "Structures Donnees",   moyenne: 13.7, correlation: 0.75, impact: "Eleve"      },
  { module: "Reseaux Info 2",       moyenne: 13.9, correlation: 0.71, impact: "Modere"     },
  { module: "Sys. Exploitation",    moyenne: 12.5, correlation: 0.65, impact: "Modere"     },
  { module: "Electronique Num.",    moyenne: 11.9, correlation: 0.58, impact: "Faible"     },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl px-3 py-2.5 text-xs shadow-lg">
        {label && <p className="font-bold text-gray-700 mb-1">{label}</p>}
        {payload.map((p, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ background: p.color || p.fill }} />
            <span className="text-gray-600">{p.name}: <strong>{p.value}</strong></span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

const StatCard = ({ label, value, sub, color, icon, delay }) => (
  <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.4 }}
    className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm"
    style={{ borderLeftWidth: 4, borderLeftColor: color }}>
    <div className="flex items-start justify-between">
      <div>
        <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">{label}</p>
        <p className="text-3xl font-bold text-gray-800">{value}</p>
        <p className="text-xs mt-1 font-medium" style={{ color }}>{sub}</p>
      </div>
      <div className="p-2.5 rounded-xl" style={{ background: color + "18" }}>
        <span style={{ color }}>{icon}</span>
      </div>
    </div>
  </motion.div>
);

const AnalysisPage = () => {
  const [stats, setStats] = useState(null);
  const [period, setPeriod] = useState("6mois");

  useEffect(() => {
    api.get("/dashboard/stats")
      .then((res) => setStats(res.data))
      .catch(() => setStats({ total_etudiants: 120, taux_reussite: 72, taux_moyen: 19, taux_risque: 9 }));
  }, []);

  return (
    <Layout>
      <div className="min-h-full p-6 space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Visualisation et Analyse</h1>
            <p className="text-sm text-gray-400 mt-0.5">Tendances et statistiques detaillees</p>
          </div>
          <div className="flex gap-1 bg-gray-100 p-1 rounded-xl">
            {[{ id: "3mois", label: "3 mois" }, { id: "6mois", label: "6 mois" }, { id: "1an", label: "1 an" }].map((p) => (
              <button key={p.id} onClick={() => setPeriod(p.id)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
                style={period === p.id ? { background: "#1e56a0", color: "#fff" } : { color: "#6b7280" }}>
                {p.label}
              </button>
            ))}
          </div>
        </motion.div>

        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard delay={0.05} color="#1e56a0" label="Total Etudiants" value={stats?.total_etudiants || 120} sub="Toutes filieres"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>} />
          <StatCard delay={0.1} color="#16a34a" label="Taux Reussite" value={`${stats?.taux_reussite || 72}%`} sub="+ 3% ce mois"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>} />
          <StatCard delay={0.15} color="#d97706" label="Taux Moyen" value={`${stats?.taux_moyen || 19}%`} sub="Suivi recommande"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>} />
          <StatCard delay={0.2} color="#dc2626" label="Taux Risque" value={`${stats?.taux_risque || 9}%`} sub="- 2% ce mois"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>} />
        </div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Evolution des predictions dans le temps</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={mockTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="mois" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} unit="%" />
              <Tooltip content={<CustomTooltip />} />
              <Legend formatter={(v) => <span className="text-xs text-gray-500">{v}</span>} />
              <Line type="monotone" dataKey="reussite" name="Reussite" stroke="#16a34a" strokeWidth={2.5} dot={{ fill: "#16a34a", r: 4 }} />
              <Line type="monotone" dataKey="moyen"    name="Moyen"    stroke="#d97706" strokeWidth={2.5} dot={{ fill: "#d97706", r: 4 }} />
              <Line type="monotone" dataKey="risque"   name="A risque" stroke="#dc2626" strokeWidth={2.5} dot={{ fill: "#dc2626", r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Repartition par filiere</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={mockFiliereStats} barSize={20}>
                <XAxis dataKey="filiere" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} unit="%" />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
                <Legend formatter={(v) => <span className="text-xs text-gray-500">{v}</span>} />
                <Bar dataKey="reussite" name="Reussite" stackId="a" fill="#16a34a" />
                <Bar dataKey="moyen"    name="Moyen"    stackId="a" fill="#d97706" />
                <Bar dataKey="risque"   name="A risque" stackId="a" fill="#dc2626" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Moyenne par module</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={mockModuleAvg} barSize={14} layout="vertical">
                <XAxis type="number" domain={[0, 20]} tick={{ fontSize: 10, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="module" tick={{ fontSize: 10, fill: "#6b7280" }} axisLine={false} tickLine={false} width={65} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
                <Bar dataKey="moyenne" name="Moyenne" radius={[0, 4, 4, 0]}>
                  {mockModuleAvg.map((entry, i) => (
                    <Cell key={i} fill={entry.moyenne >= 14 ? "#16a34a" : entry.moyenne >= 10 ? "#d97706" : "#dc2626"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Profil academique moyen (promotion)</h2>
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={mockRadar}>
                <PolarGrid stroke="#f1f5f9" />
                <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: "#9ca3af" }} />
                <Radar dataKey="score" name="Moyenne" stroke="#1e56a0" fill="#1e56a0" fillOpacity={0.15} strokeWidth={2} />
                <Tooltip content={<CustomTooltip />} />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Distribution des absences</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={mockAbsences} barSize={40}>
                <XAxis dataKey="range" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
                <Bar dataKey="count" name="Etudiants" radius={[6, 6, 0, 0]}>
                  {mockAbsences.map((entry, i) => (
                    <Cell key={i} fill={i === 0 ? "#16a34a" : i === 1 ? "#d97706" : i === 2 ? "#f97316" : "#dc2626"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-3 p-3 bg-orange-50 border border-orange-100 rounded-xl">
              <p className="text-xs text-orange-700">
                <strong>26 etudiants</strong> ont plus de 6 absences — correlation forte avec le risque d'echec.
              </p>
            </div>
          </motion.div>
        </div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Correlation modules et reussite</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr style={{ background: "#f8fafc" }}>
                  {["Module", "Moyenne promo", "Correlation reussite", "Impact"].map((h) => (
                    <th key={h} className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wider px-4 py-3">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {correlationData.map((row, i) => {
                  const impactColor = row.impact === "Tres eleve" ? "#dc2626" : row.impact === "Eleve" ? "#d97706" : row.impact === "Modere" ? "#1e56a0" : "#6b7280";
                  const impactBg = row.impact === "Tres eleve" ? "#fee2e2" : row.impact === "Eleve" ? "#fef3c7" : row.impact === "Modere" ? "#eff6ff" : "#f9fafb";
                  return (
                    <tr key={i} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 text-sm font-medium text-gray-800">{row.module}</td>
                      <td className="px-4 py-3 text-sm font-bold" style={{ color: row.moyenne >= 14 ? "#16a34a" : "#d97706" }}>{row.moyenne}/20</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="h-2 bg-gray-100 rounded-full overflow-hidden" style={{ width: 80 }}>
                            <div className="h-full rounded-full bg-blue-500" style={{ width: `${row.correlation * 100}%` }} />
                          </div>
                          <span className="text-xs font-semibold text-gray-600">{row.correlation}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs px-2.5 py-1 rounded-full font-bold" style={{ background: impactBg, color: impactColor }}>{row.impact}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default AnalysisPage;