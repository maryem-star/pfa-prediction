import api from "./api";

// Étudiant : voir ses recommandations
export const getMyRecommendations = async () => {
  try {
    const res = await api.get("/recommendations/mes-recommendations");
    return res.data;
  } catch {
    return [];
  }
};

// Chefs : envoyer une recommandation à un étudiant
export const sendRecommendation = async ({ studentId, message }) => {
  const res = await api.post("/recommendations/", {
    etudiant_id: studentId,
    message,
  });
  return res.data;
};

// Marquer une recommandation comme lue
export const markAsRead = async (recommendationId) => {
  try {
    const res = await api.patch(`/recommendations/${recommendationId}/lu`);
    return res.data;
  } catch {
    return null;
  }
};

// Chefs : voir les recommandations envoyées
export const getSentRecommendations = async () => {
  try {
    const res = await api.get("/recommendations/sent");
    return res.data;
  } catch {
    return [];
  }
};

// Ancien alias gardé pour compatibilité
export const getStudentRecommendations = getMyRecommendations;