import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import { sendRecommendation } from "../services/recommendationService";

export default function SendRecommendationModal({ student, onClose, onSent }) {
  const { user } = useAuth();
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSend = async () => {
    if (!message.trim()) { setError("Le message est requis"); return; }
    setLoading(true);
    setError("");
    try {
      await sendRecommendation({
        studentId: student.id,
        message: message.trim(),
        expediteurRole: user.role,
      });
      onSent?.();
      onClose();
    } catch {
      setError("Erreur lors de l'envoi. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.95, y: 10 }}
          onClick={e => e.stopPropagation()}
          className="bg-white rounded-2xl p-6 w-full max-w-lg shadow-xl"
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-5">
            <div>
              <h2 className="text-lg font-bold text-gray-800">Envoyer une recommandation</h2>
              <p className="text-sm text-gray-500 mt-1">
                À : <span className="font-medium text-gray-700">{student?.prenom} {student?.nom}</span>
                {student?.filiere && <span className="ml-2 text-xs bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded">{student.filiere}</span>}
              </p>
            </div>
            <button onClick={onClose} className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Sender info */}
          <div className="flex items-center gap-3 mb-4 p-3 bg-gray-50 rounded-xl">
            <div className="w-8 h-8 rounded-full bg-[#1B3A6B] flex items-center justify-center">
              <span className="text-white text-xs font-bold">{user?.prenom?.[0]}{user?.nom?.[0]}</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-800">{user?.prenom} {user?.nom}</p>
              <p className="text-xs text-gray-500">
                {user?.role?.startsWith("chef_departement") ? "Chef de département" : "Chef de filière"}
              </p>
            </div>
          </div>

          {/* Message */}
          <div className="space-y-3">
            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Message</label>
            <textarea
              value={message}
              onChange={e => { setMessage(e.target.value); setError(""); }}
              placeholder="Écrivez votre recommandation, conseil ou feedback pour cet étudiant..."
              rows={5}
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[#1B3A6B]/20 focus:border-[#1B3A6B]/30 transition-all"
            />
            {error && <p className="text-xs text-red-500">{error}</p>}
            <p className="text-xs text-gray-400 text-right">{message.length} caractères</p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-5">
            <button
              onClick={onClose}
              className="flex-1 border border-gray-200 rounded-xl py-2.5 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
            >
              Annuler
            </button>
            <button
              onClick={handleSend}
              disabled={loading || !message.trim()}
              className="flex-1 bg-[#1B3A6B] text-white rounded-xl py-2.5 text-sm font-medium hover:bg-[#152d54] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                  Envoyer
                </>
              )}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}