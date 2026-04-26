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

// POST /students/
export const addStudent = async (data) => {
  const res = await api.post("/students/", data);
  return res.data;
};

// PUT /students/{id}
export const updateStudent = async (id, data) => {
  const res = await api.put(`/students/${id}`, data);
  return res.data;
};

// DELETE /students/{id}
export const deleteStudent = async (id) => {
  await api.delete(`/students/${id}`);
};

// POST /import/students/{filiere} — Import Excel
export const importStudents = async (filiere, file) => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post(`/import/students/${filiere}`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

// GET /dashboard/stats
export const getDashboardStats = async () => {
  const res = await api.get("/dashboard/stats");
  return res.data;
};

// GET /predictions/dashboard/couleurs
export const getPredictionColors = async () => {
  const res = await api.get("/predictions/dashboard/couleurs");
  return res.data;
};