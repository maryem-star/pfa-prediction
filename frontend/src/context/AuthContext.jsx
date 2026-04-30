import { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");
    if (token && storedUser) {
      const parsed = JSON.parse(storedUser);
      setUser(parsed);
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const response = await api.post("/auth/login", { email, password });

    const { access_token } = response.data;

    // Décoder le token JWT pour extraire tous les champs
    const payload = JSON.parse(atob(access_token.split(".")[1]));

    const userData = {
      email: payload.sub,
      role: payload.role,
      id: payload.id,
      nom: payload.nom || null,
      prenom: payload.prenom || null,
      filiere: payload.filiere || null,
      student_id: payload.student_id || null,
    };

    localStorage.setItem("token", access_token);
    localStorage.setItem("user", JSON.stringify(userData));
    api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
    setUser(userData);
    return userData;
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    delete api.defaults.headers.common["Authorization"];
    setUser(null);
  };

  // Redirection selon le rôle après login
  const getHomeRoute = (role) => {
    if (!role) return "/home";
    if (role === "super_admin" || role === "directeur_adjoint") return "/dashboard";
    if (role.startsWith("chef_departement")) return "/dashboard";
    if (role.startsWith("chef_filiere")) return "/dashboard";
    if (role === "etudiant") return "/student-dashboard";
    return "/dashboard";
  };

  // Filières autorisées selon le rôle
  const getAllowedFilieres = () => {
    if (!user) return [];
    const role = user.role;
    if (role === "super_admin" || role === "directeur_adjoint") return null; // toutes
    if (role === "chef_departement_STIN") return ["G2E", "GC", "GI"];
    if (role === "chef_departement_TRI")  return ["ISIC", "2ITE", "CCN"];
    if (role === "chef_filiere_G2E")  return ["G2E"];
    if (role === "chef_filiere_GC")   return ["GC"];
    if (role === "chef_filiere_GI")   return ["GI"];
    if (role === "chef_filiere_ISIC") return ["ISIC"];
    if (role === "chef_filiere_2ITE") return ["2ITE"];
    if (role === "chef_filiere_CCN")  return ["CCN"];
    return [];
  };

  // Helpers rôles
  const isAdmin = () => {
    if (!user) return false;
    return ["super_admin", "directeur_adjoint"].includes(user.role);
  };

  const isSuperAdmin = () => {
    if (!user) return false;
    return user.role === "super_admin";
  };

  const isDirecteurAdjoint = () => {
    if (!user) return false;
    return user.role === "directeur_adjoint";
  };

  const isChefDepartement = () => {
    if (!user) return false;
    return user.role?.startsWith("chef_departement");
  };

  const isChefFiliere = () => {
    if (!user) return false;
    return user.role?.startsWith("chef_filiere");
  };

  const isEtudiant = () => {
    if (!user) return false;
    return user.role === "etudiant";
  };

  const canManageFiliere = (filiere) => {
    const allowed = getAllowedFilieres();
    if (allowed === null) return true;
    return allowed.includes(filiere);
  };

  // Nom affiché avec fallback
  const getDisplayName = () => {
    if (!user) return "";
    if (user.prenom && user.nom) return `${user.prenom} ${user.nom}`;
    return user.email?.split("@")[0] || "Utilisateur";
  };

  // Initiales avec fallback
  const getInitials = () => {
    if (!user) return "?";
    if (user.prenom && user.nom) return `${user.prenom[0]}${user.nom[0]}`;
    return user.email?.[0]?.toUpperCase() || "?";
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      logout,
      getHomeRoute,
      getAllowedFilieres,
      isAdmin,
      isSuperAdmin,
      isDirecteurAdjoint,
      isChefDepartement,
      isChefFiliere,
      isEtudiant,
      canManageFiliere,
      getDisplayName,
      getInitials,
    }}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}