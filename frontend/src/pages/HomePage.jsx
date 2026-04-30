import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";

const STAFF_ROLES = [
  {
    key: "super_admin",
    label: "Super Administrateur",
    desc: "Gestion complète des étudiants et utilisateurs",
    color: "#1e56a0",
  },
  {
    key: "directeur_adjoint",
    label: "Directeur Adjoint",
    desc: "Accès complet en lecture et supervision",
    color: "#0f766e",
  },
  {
    key: "chef_departement",
    label: "Chef de Département",
    desc: "Gestion de son département (STIN ou TRI)",
    color: "#7c3aed",
  },
  {
    key: "chef_filiere",
    label: "Chef de Filière",
    desc: "Gestion de sa filière uniquement",
    color: "#b45309",
  },
];

function HomePage() {
  const navigate = useNavigate();
  const [step, setStep] = useState("home"); // "home" | "staff_choice"

  const handleStaffRoleClick = (roleKey) => {
    // On redirige vers /login en passant le rôle choisi
    navigate("/login", { state: { roleHint: roleKey } });
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-6">

      <AnimatePresence mode="wait">

        {/* STEP 1 — Choix Étudiant ou Staff */}
        {step === "home" && (
          <motion.div
            key="home"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="w-full max-w-3xl"
          >
            <div className="text-center mb-10">
              <h1 className="text-3xl font-bold text-slate-800">
                Bienvenue 👋
              </h1>
              <p className="text-gray-400 mt-2">
                Choisissez votre espace pour continuer
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

              {/* Espace Staff */}
              <motion.div
                whileHover={{ scale: 1.03 }}
                className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm cursor-pointer"
                onClick={() => setStep("staff_choice")}
              >
                <h2 className="text-lg font-semibold mb-2 text-gray-800">
                  Espace Staff
                </h2>
                <p className="text-sm text-gray-400 mb-4">
                  Administrateurs, directeurs, chefs de département et de filière
                </p>
                <button
                  className="px-4 py-2 rounded-lg text-sm font-medium text-white"
                  style={{ background: "#1e56a0" }}
                >
                  Accéder
                </button>
              </motion.div>

              {/* Espace Étudiant */}
              <motion.div
                whileHover={{ scale: 1.03 }}
                className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm cursor-pointer"
                onClick={() => navigate("/student/login")}
              >
                <h2 className="text-lg font-semibold mb-2 text-gray-800">
                  Espace Étudiant
                </h2>
                <p className="text-sm text-gray-400 mb-4">
                  Consultation des résultats et prédictions
                </p>
                <button
                  className="px-4 py-2 rounded-lg text-sm font-medium text-white"
                  style={{ background: "#16a34a" }}
                >
                  Accéder
                </button>
              </motion.div>

            </div>
          </motion.div>
        )}

        {/* STEP 2 — Choix du rôle Staff */}
        {step === "staff_choice" && (
          <motion.div
            key="staff_choice"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="w-full max-w-3xl"
          >
            <div className="text-center mb-8">
              <button
                onClick={() => setStep("home")}
                className="text-sm text-gray-400 hover:text-gray-600 mb-4 flex items-center gap-1 mx-auto"
              >
                ← Retour
              </button>
              <h1 className="text-2xl font-bold text-slate-800">
                Espace Staff
              </h1>
              <p className="text-gray-400 mt-2">
                Sélectionnez votre rôle pour vous connecter
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {STAFF_ROLES.map((role) => (
                <motion.div
                  key={role.key}
                  whileHover={{ scale: 1.03 }}
                  className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm cursor-pointer"
                  onClick={() => handleStaffRoleClick(role.key)}
                >
                  <h2 className="text-base font-semibold mb-1 text-gray-800">
                    {role.label}
                  </h2>
                  <p className="text-sm text-gray-400 mb-4">{role.desc}</p>
                  <button
                    className="px-3 py-1.5 rounded-lg text-sm font-medium text-white"
                    style={{ background: role.color }}
                  >
                    Se connecter
                  </button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
}

export default HomePage;