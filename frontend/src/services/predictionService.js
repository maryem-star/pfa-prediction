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