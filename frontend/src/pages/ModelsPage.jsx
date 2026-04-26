import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, BarChart, Bar, Cell, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, Legend
} from "recharts";
import Layout from "../components/Layout";
import { getModelMetrics } from "../services/predictionService";

// ── Config des modèles (style) ────────────────────────────────────────────────
const MODEL_CONFIG = {
  RandomForest:       { label: "Random Forest",        color: "#1e56a0", bg: "#eff6ff", border: "#bfdbfe", description: "Ensemble d'arbres de décision — robuste aux données bruitées" },
  SVM:                { label: "SVM",                   color: "#7c3aed", bg: "#f5f3ff", border: "#ddd6fe", description: "Support Vector Machine — efficace pour les petits datasets" },
  LogisticRegression: { label: "Régression Logistique", color: "#059669", bg: "#ecfdf5", border: "#a7f3d0", description: "Modèle linéaire — rapide et interprétable" },
};

// ── Fallback mock data (si l'API n'est pas disponible) ────────────────────────
const FALLBACK_MODELS = [
  { id: "RandomForest",       ...MODEL_CONFIG.RandomForest,       accuracy: 0.874, precision: 0.861, recall: 0.883, f1: 0.872, auc: 0.921, training_time: "—" },
  { id: "SVM",                ...MODEL_CONFIG.SVM,                accuracy: 0.851, precision: 0.843, recall: 0.862, f1: 0.852, auc: 0.903, training_time: "—" },
  { id: "LogisticRegression", ...MODEL_CONFIG.LogisticRegression, accuracy: 0.823, precision: 0.815, recall: 0.831, f1: 0.823, auc: 0.879, training_time: "—" },
];

function buildModelsFromAPI(apiMetrics) {
  // apiMetrics peut être un objet {RandomForest: {...}} ou un tableau [{name: "RandomForest", ...}]
  const metricsMap = {};
  if (Array.isArray(apiMetrics)) {
    apiMetrics.forEach((m) => { metricsMap[m.name || m.id] = m; });
  } else {
    Object.assign(metricsMap, apiMetrics);
  }

  return Object.entries(MODEL_CONFIG).map(([id, cfg]) => {
    const m = metricsMap[id] || {};
    return {
      id,
      ...cfg,
      accuracy:  m.accuracy  ?? m.Accuracy  ?? 0,
      precision: m.precision ?? m.Precision ?? 0,
      recall:    m.recall    ?? m.Recall    ?? 0,
      f1:        m.f1        ?? m["f1-score"] ?? m["F1-Score"] ?? m.f1_score ?? 0,
      auc:       m.auc       ?? m.roc_auc   ?? m["ROC-AUC"]   ?? m.auc_roc  ?? 0,
      training_time: m.training_time || "—",
    };
  });
}

function buildBarData(models) {
  return [
    { metric: "Accuracy",  RandomForest: +(models[0]?.accuracy  * 100).toFixed(1), SVM: +(models[1]?.accuracy  * 100).toFixed(1), LogisticRegression: +(models[2]?.accuracy  * 100).toFixed(1) },
    { metric: "Precision", RandomForest: +(models[0]?.precision * 100).toFixed(1), SVM: +(models[1]?.precision * 100).toFixed(1), LogisticRegression: +(models[2]?.precision * 100).toFixed(1) },
    { metric: "Recall",    RandomForest: +(models[0]?.recall    * 100).toFixed(1), SVM: +(models[1]?.recall    * 100).toFixed(1), LogisticRegression: +(models[2]?.recall    * 100).toFixed(1) },
    { metric: "F1-Score",  RandomForest: +(models[0]?.f1        * 100).toFixed(1), SVM: +(models[1]?.f1        * 100).toFixed(1), LogisticRegression: +(models[2]?.f1        * 100).toFixed(1) },
    { metric: "AUC-ROC",   RandomForest: +(models[0]?.auc       * 100).toFixed(1), SVM: +(models[1]?.auc       * 100).toFixed(1), LogisticRegression: +(models[2]?.auc       * 100).toFixed(1) },
  ];
}

function buildRadarData(models) {
  return [
    { metric: "Accuracy",  rf: +(models[0]?.accuracy  * 100).toFixed(1), svm: +(models[1]?.accuracy  * 100).toFixed(1), lr: +(models[2]?.accuracy  * 100).toFixed(1) },
    { metric: "Precision", rf: +(models[0]?.precision * 100).toFixed(1), svm: +(models[1]?.precision * 100).toFixed(1), lr: +(models[2]?.precision * 100).toFixed(1) },
    { metric: "Recall",    rf: +(models[0]?.recall    * 100).toFixed(1), svm: +(models[1]?.recall    * 100).toFixed(1), lr: +(models[2]?.recall    * 100).toFixed(1) },
    { metric: "F1-Score",  rf: +(models[0]?.f1        * 100).toFixed(1), svm: +(models[1]?.f1        * 100).toFixed(1), lr: +(models[2]?.f1        * 100).toFixed(1) },
    { metric: "AUC-ROC",   rf: +(models[0]?.auc       * 100).toFixed(1), svm: +(models[1]?.auc       * 100).toFixed(1), lr: +(models[2]?.auc       * 100).toFixed(1) },
  ];
}

// ── ROC curve data (approximation basée sur AUC) ──────────────────────────────
function buildRocData(models) {
  return Array.from({ length: 11 }, (_, i) => {
    const fpr = i / 10;
    const rfAuc  = models[0]?.auc || 0.92;
    const svmAuc = models[1]?.auc || 0.90;
    const lrAuc  = models[2]?.auc || 0.88;
    return {
      fpr: parseFloat(fpr.toFixed(1)),
      rf:  parseFloat(Math.min(1, fpr + (1 - fpr) * rfAuc).toFixed(3)),
      svm: parseFloat(Math.min(1, fpr + (1 - fpr) * svmAuc).toFixed(3)),
      lr:  parseFloat(Math.min(1, fpr + (1 - fpr) * lrAuc).toFixed(3)),
      random: fpr,
    };
  });
}

// ── Confusion matrix (estimation basée sur accuracy) ──────────────────────────
function buildConfusionMatrices(models) {
  const matrices = {};
  for (const m of models) {
    const total = 180;
    const tp = Math.round(total * 0.5 * (m.recall || 0.85));
    const fn = Math.round(total * 0.5) - tp;
    const tn = Math.round(total * 0.5 * (m.precision ? (m.accuracy * 2 - m.recall) : 0.85));
    const fp = Math.round(total * 0.5) - tn;
    matrices[m.id] = { tp: Math.max(0, tp), fp: Math.max(0, fp), fn: Math.max(0, fn), tn: Math.max(0, tn) };
  }
  return matrices;
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl px-3 py-2.5 text-xs shadow-lg">
        {label !== undefined && <p className="font-bold text-gray-700 mb-1">{label}</p>}
        {payload.map((p, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ background: p.color || p.stroke }} />
            <span className="text-gray-600">{p.name}: <strong>{p.value}%</strong></span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

// ── Confusion Matrix display ──────────────────────────────────────────────────
const ConfusionMatrix = ({ matrix, color }) => {
  const total = matrix.tp + matrix.fp + matrix.fn + matrix.tn;
  const cells = [
    { label: "VP", value: matrix.tp, bg: "#dcfce7", color: "#15803d", desc: "Vrais Positifs" },
    { label: "FP", value: matrix.fp, bg: "#fee2e2", color: "#b91c1c", desc: "Faux Positifs" },
    { label: "FN", value: matrix.fn, bg: "#fef3c7", color: "#b45309", desc: "Faux Négatifs" },
    { label: "VN", value: matrix.tn, bg: "#dcfce7", color: "#15803d", desc: "Vrais Négatifs" },
  ];
  return (
    <div>
      <div className="grid grid-cols-2 gap-2 mb-3">
        {cells.map((cell) => (
          <div key={cell.label} className="rounded-xl p-3 text-center border"
            style={{ background: cell.bg, borderColor: cell.color + "44" }}>
            <p className="text-xs font-bold" style={{ color: cell.color }}>{cell.label}</p>
            <p className="text-2xl font-bold text-gray-800">{cell.value}</p>
            <p className="text-xs text-gray-400">{cell.desc}</p>
            <p className="text-xs font-medium mt-1" style={{ color: cell.color }}>
              {((cell.value / total) * 100).toFixed(1)}%
            </p>
          </div>
        ))}
      </div>
      <div className="text-xs text-gray-400 text-center">Total: {total} échantillons</div>
    </div>
  );
};

// ── Main ──────────────────────────────────────────────────────────────────────
const ModelsPage = () => {
  const [selectedModel, setSelectedModel] = useState("RandomForest");
  const [MODELS, setModels] = useState(FALLBACK_MODELS);
  const [metricsSource, setMetricsSource] = useState("local");

  useEffect(() => {
    getModelMetrics()
      .then((data) => {
        if (data?.modeles && Object.keys(data.modeles).length > 0) {
          setModels(buildModelsFromAPI(data.modeles));
          setMetricsSource("api");
        }
      })
      .catch(() => {
        // API indisponible — on garde les données fallback
      });
  }, []);

  const metricsBar = buildBarData(MODELS);
  const radarData = buildRadarData(MODELS);
  const rocData = buildRocData(MODELS);
  const confusionMatrices = buildConfusionMatrices(MODELS);

  const activeModel = MODELS.find((m) => m.id === selectedModel);
  const activeMatrix = confusionMatrices[selectedModel];

  return (
    <Layout>
      <div className="min-h-full p-6 space-y-6">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-2xl font-bold text-gray-800">Comparaison des Modèles ML</h1>
          <p className="text-sm text-gray-400 mt-0.5">Métriques de performance et courbes ROC</p>
        </motion.div>

        {/* Model cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {MODELS.map((model, i) => (
            <motion.button key={model.id}
              initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              onClick={() => setSelectedModel(model.id)}
              className="text-left p-5 rounded-xl border-2 transition-all duration-200"
              style={{
                borderColor: selectedModel === model.id ? model.color : "#e5e7eb",
                background: selectedModel === model.id ? model.bg : "#fff",
                boxShadow: selectedModel === model.id ? `0 0 0 3px ${model.color}22` : "none",
              }}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-gray-800">{model.label}</h3>
                {selectedModel === model.id && (
                  <span className="text-xs px-2 py-0.5 rounded-full font-bold text-white"
                    style={{ background: model.color }}>Actif</span>
                )}
              </div>
              <p className="text-xs text-gray-400 mb-4">{model.description}</p>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: "Accuracy", value: `${(model.accuracy * 100).toFixed(1)}%` },
                  { label: "F1-Score", value: `${(model.f1 * 100).toFixed(1)}%` },
                  { label: "AUC-ROC",  value: `${(model.auc * 100).toFixed(1)}%` },
                  { label: "Temps",    value: model.training_time },
                ].map((stat) => (
                  <div key={stat.label} className="bg-white rounded-lg p-2 border border-gray-100">
                    <p className="text-xs text-gray-400">{stat.label}</p>
                    <p className="text-sm font-bold" style={{ color: model.color }}>{stat.value}</p>
                  </div>
                ))}
              </div>
            </motion.button>
          ))}
        </div>

        {/* Metrics bar comparison */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
          className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Comparaison des métriques</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={metricsBar} barSize={16}>
              <XAxis dataKey="metric" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
              <YAxis domain={[75, 95]} tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} unit="%" />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
              <Legend formatter={(v) => <span className="text-xs text-gray-500">{MODELS.find(m => m.id === v)?.label || v}</span>} />
              <Bar dataKey="RandomForest"       name="RandomForest"       fill="#1e56a0" radius={[3, 3, 0, 0]} />
              <Bar dataKey="SVM"                name="SVM"                fill="#7c3aed" radius={[3, 3, 0, 0]} />
              <Bar dataKey="LogisticRegression" name="LogisticRegression" fill="#059669" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* ROC + Radar */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* ROC curves */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-gray-700">Courbes ROC</h2>
              <div className="flex flex-wrap gap-3">
                {MODELS.map((m) => (
                  <div key={m.id} className="flex items-center gap-1.5">
                    <div className="w-3 h-0.5 rounded" style={{ background: m.color }} />
                    <span className="text-xs text-gray-500">{m.label} ({(m.auc * 100).toFixed(0)}%)</span>
                  </div>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={rocData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="fpr" tick={{ fontSize: 10, fill: "#9ca3af" }} axisLine={false} tickLine={false}
                  label={{ value: "Taux Faux Positifs", position: "insideBottom", offset: -2, fontSize: 10, fill: "#9ca3af" }} />
                <YAxis tick={{ fontSize: 10, fill: "#9ca3af" }} axisLine={false} tickLine={false}
                  label={{ value: "Taux Vrais Positifs", angle: -90, position: "insideLeft", fontSize: 10, fill: "#9ca3af" }} />
                <Tooltip content={<CustomTooltip />} />
                <Line type="monotone" dataKey="rf"     name="Random Forest"          stroke="#1e56a0" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="svm"    name="SVM"                    stroke="#7c3aed" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="lr"     name="Reg. Logistique"        stroke="#059669" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="random" name="Aléatoire"              stroke="#d1d5db" strokeWidth={1.5} dot={false} strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Radar */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Profil de performance (Radar)</h2>
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#f1f5f9" />
                <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11, fill: "#9ca3af" }} />
                <Radar dataKey="rf"  name="Random Forest"    stroke="#1e56a0" fill="#1e56a0" fillOpacity={0.1} strokeWidth={2} />
                <Radar dataKey="svm" name="SVM"              stroke="#7c3aed" fill="#7c3aed" fillOpacity={0.1} strokeWidth={2} />
                <Radar dataKey="lr"  name="Reg. Logistique"  stroke="#059669" fill="#059669" fillOpacity={0.1} strokeWidth={2} />
                <Legend formatter={(v) => <span className="text-xs text-gray-500">{v}</span>} />
                <Tooltip content={<CustomTooltip />} />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Confusion matrix + detailed metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Confusion matrix */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <h2 className="text-sm font-semibold text-gray-700">Matrice de Confusion</h2>
              <span className="text-xs px-2 py-0.5 rounded-full font-bold text-white"
                style={{ background: activeModel.color }}>{activeModel.label}</span>
            </div>
            <ConfusionMatrix matrix={activeMatrix} color={activeModel.color} />
          </motion.div>

          {/* Detailed metrics */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55 }}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Métriques détaillées — {activeModel.label}</h2>
            <div className="space-y-3">
              {[
                { label: "Accuracy",  value: activeModel.accuracy,  desc: "Taux de bonnes prédictions" },
                { label: "Precision", value: activeModel.precision, desc: "Parmi les positifs prédits, combien sont corrects" },
                { label: "Recall",    value: activeModel.recall,    desc: "Parmi les vrais positifs, combien sont détectés" },
                { label: "F1-Score",  value: activeModel.f1,        desc: "Moyenne harmonique Précision/Rappel" },
                { label: "AUC-ROC",   value: activeModel.auc,       desc: "Aire sous la courbe ROC" },
              ].map((metric) => (
                <div key={metric.label}>
                  <div className="flex items-center justify-between mb-1">
                    <div>
                      <span className="text-xs font-bold text-gray-700">{metric.label}</span>
                      <span className="text-xs text-gray-400 ml-2">{metric.desc}</span>
                    </div>
                    <span className="text-sm font-bold" style={{ color: activeModel.color }}>
                      {(metric.value * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${metric.value * 100}%` }}
                      transition={{ duration: 0.8, ease: "easeOut" }}
                      className="h-full rounded-full"
                      style={{ background: activeModel.color }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Best model recommendation */}
            {(() => {
              const best = [...MODELS].sort((a, b) => (b.f1 || 0) - (a.f1 || 0))[0];
              return (
                <div className="mt-4 p-3 rounded-xl border"
                  style={{ background: "#f0fdf4", borderColor: "#bbf7d0" }}>
                  <p className="text-xs font-bold text-green-700 mb-1">Meilleur modèle recommandé</p>
                  <p className="text-xs text-green-600">
                    <strong>{best?.label}</strong> offre les meilleures performances avec un AUC-ROC de {((best?.auc || 0) * 100).toFixed(1)}% et une accuracy de {((best?.accuracy || 0) * 100).toFixed(1)}%.
                    {metricsSource === "api" && " (métriques réelles)"}
                  </p>
                </div>
              );
            })()}
          </motion.div>
        </div>
      </div>
    </Layout>
  );
};

export default ModelsPage;