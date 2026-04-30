import api from "./api";

// GET /students/
export const getStudents = async () => {
  const res = await api.get("/students/");
  return res.data;
};

// GET /students/{id}
export const getStudent = async (id) => {
  const res = await api.get(`/students/${id}`);
  return res.data;
};

// GET /grades/student/{id}
export const getStudentGrades = async (studentId) => {
  const res = await api.get(`/grades/student/${studentId}`);
  return res.data;
};

// GET /predictions/student/{id}
// Retourne toutes les prédictions pour un étudiant (les 3 modèles)
export const getStudentPredictions = async (studentId) => {
  const res = await api.get(`/predictions/student/${studentId}`);
  return res.data;
};

// POST /predictions/ — Lancer une prédiction manuellement
export const createPrediction = async (data) => {
  const res = await api.post("/predictions/", data);
  return res.data;
};

// POST /predictions/ml/predict — Prédiction ML réelle (réussite 1A/2A)
export const predictML = async (data) => {
  const res = await api.post("/predictions/ml/predict", data);
  return res.data;
};

// POST /predictions/ml/predict-3a — Prédiction ML 3ème année (modules & PFE)
export const predictML3A = async (data) => {
  const res = await api.post("/predictions/ml/predict-3a", data);
  return res.data;
};

// POST /predictions/ml/batch — Prédiction par lot
export const predictMLBatch = async (students) => {
  const res = await api.post("/predictions/ml/batch", { students });
  return res.data;
};

// GET /predictions/ml/metriques — Métriques des modèles ML
export const getModelMetrics = async () => {
  const res = await api.get("/predictions/ml/metriques");
  return res.data;
};

// GET /predictions/dashboard/couleurs — Répartition des couleurs
export const getPredictionColors = async () => {
  const res = await api.get("/predictions/dashboard/couleurs");
  return res.data;
};
