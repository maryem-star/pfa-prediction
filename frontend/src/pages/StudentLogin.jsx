import { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const StudentLogin = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const userData = await login(email, password);
      if (userData.role !== "etudiant") {
        setError("Ce compte n'est pas un compte étudiant.");
        return;
      }
      navigate("/student-dashboard", { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || "Email ou mot de passe incorrect.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="bg-white border border-gray-200 rounded-xl shadow-sm w-full max-w-md p-8"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: "#1e56a0" }}>
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24"
              stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M12 14l9-5-9-5-9 5 9 5zM12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-bold" style={{ color: "#1e293b" }}>PrédiSuccess</p>
            <p className="text-xs text-gray-400">Plateforme de prédiction académique</p>
          </div>
        </div>

        <div className="border-t border-gray-100 mb-6" />

        {/* Badge */}
        <div className="inline-flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-lg border mb-4"
          style={{ background: "#f0fdf4", borderColor: "#bbf7d0", color: "#16a34a" }}>
          <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          Espace Étudiant
        </div>

        <h1 className="text-lg font-bold mb-1" style={{ color: "#1e293b" }}>Connexion</h1>
        <p className="text-xs text-gray-400 mb-5">Entrez votre email et mot de passe</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="etudiant@ensa-eljadida.ac.ma"
              required
              className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm bg-gray-50
                         text-gray-800 outline-none focus:border-blue-500 focus:bg-white transition-colors"
            />
          </div>

          {/* Mot de passe */}
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
              Mot de passe
            </label>
            <div className="relative">
              <input
                type={showPass ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm bg-gray-50
                           text-gray-800 outline-none focus:border-blue-500 focus:bg-white transition-colors pr-10"
              />
              <button type="button" onClick={() => setShowPass(!showPass)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showPass ? (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* Erreur */}
          {error && (
            <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="text-xs text-red-500 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
              {error}
            </motion.p>
          )}

          {/* Submit */}
          <button type="submit" disabled={loading}
            className="w-full py-2.5 rounded-xl text-sm font-semibold text-white transition-colors"
            style={{ background: loading ? "#93b4d4" : "#1e56a0" }}>
            {loading ? "Connexion en cours..." : "Se connecter"}
          </button>
        </form>

        {/* Retour */}
        <div className="text-center mt-4">
          <button onClick={() => navigate("/")}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors">
            ← Retour à l'accueil
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default StudentLogin;