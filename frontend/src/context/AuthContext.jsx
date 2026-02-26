import { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");
    if (token && savedUser) {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
  // Login de test — à remplacer quand le backend est prêt
  if (email && password) {
    const fakeUser = { name: "Administrateur", email };
    localStorage.setItem("token", "test-token");
    localStorage.setItem("user", JSON.stringify(fakeUser));
    api.defaults.headers.common["Authorization"] = `Bearer test-token`;
    setUser(fakeUser);
    return fakeUser;
  }
  throw new Error("Champs vides");
};

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    delete api.defaults.headers.common["Authorization"];
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);