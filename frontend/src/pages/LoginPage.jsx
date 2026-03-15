import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../context/AuthContext";

const ParticleCanvas = () => {
  const canvasRef = useRef(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    let animId;
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; };
    resize();
    window.addEventListener("resize", resize);
    const nodes = Array.from({ length: 35 }, () => ({
      x: Math.random() * canvas.width, y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.35, vy: (Math.random() - 0.5) * 0.35,
      r: Math.random() * 2 + 1, pulse: Math.random() * Math.PI * 2,
    }));
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      nodes.forEach((a, i) => {
        nodes.slice(i + 1).forEach((b) => {
          const dist = Math.hypot(a.x - b.x, a.y - b.y);
          if (dist < 140) {
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
            ctx.strokeStyle = `rgba(30, 86, 160, ${0.1 * (1 - dist / 140)})`;
            ctx.lineWidth = 0.6; ctx.stroke();
          }
        });
      });
      nodes.forEach((n) => {
        n.pulse += 0.02;
        const glow = Math.sin(n.pulse) * 0.5 + 0.5;
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r + glow * 0.8, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(30, 86, 160, ${0.2 + glow * 0.25})`; ctx.fill();
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > canvas.width) n.vx *= -1;
        if (n.y < 0 || n.y > canvas.height) n.vy *= -1;
      });
      animId = requestAnimationFrame(draw);
    };
    draw();
    return () => { cancelAnimationFrame(animId); window.removeEventListener("resize", resize); };
  }, []);
  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />;
};

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [focusedField, setFocusedField] = useState(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.message || "Identifiants incorrects. Réessayez.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden flex items-center justify-center"
      style={{ background: "linear-gradient(135deg, #f0f4f8 0%, #e8eef5 60%, #fdf0e8 100%)" }}>
      <ParticleCanvas />

      {/* Decorative blobs */}
      <div className="absolute top-[-100px] right-[-100px] w-96 h-96 rounded-full pointer-events-none opacity-20"
        style={{ background: "radial-gradient(circle, #e87722, transparent 70%)" }} />
      <div className="absolute bottom-[-80px] left-[-80px] w-72 h-72 rounded-full pointer-events-none opacity-15"
        style={{ background: "radial-gradient(circle, #1e56a0, transparent 70%)" }} />

      <motion.div
        initial={{ opacity: 0, y: 28, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-md mx-4"
      >
        <div className="relative bg-white/85 backdrop-blur-xl border border-white/70 rounded-2xl p-8 shadow-[0_20px_60px_rgba(0,0,0,0.1)]">
          {/* Top gradient bar */}
          <div className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl"
            style={{ background: "linear-gradient(90deg, #1e56a0 0%, #e87722 100%)" }} />

          {/* ENSA Logo */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center mb-6"
          >
            <div className="flex justify-center mb-3">
              <img src="/ensa-logo.png" alt="ENSA El Jadida"
                className="h-20 w-auto object-contain drop-shadow-sm" />
            </div>
            <div className="h-px w-20 mx-auto mb-3"
              style={{ background: "linear-gradient(90deg, transparent, #1e56a0, transparent)" }} />
            <h1 className="text-base font-bold" style={{ color: "#1e56a0" }}>
              Système de Prédiction de Réussite
            </h1>
            <p className="text-xs text-gray-400 mt-0.5">Connectez-vous pour accéder à votre espace</p>
          </motion.div>

          {/* Form */}
          <motion.form onSubmit={handleSubmit} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ delay: 0.35 }} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wider">Email</label>
              <div className={`relative rounded-xl border-2 transition-all duration-200 ${
                focusedField === "email"
                  ? "border-blue-400 bg-white shadow-[0_0_0_3px_rgba(30,86,160,0.08)]"
                  : "border-gray-200 bg-gray-50"}`}>
                <div className="absolute left-3.5 top-1/2 -translate-y-1/2">
                  <svg className={`w-4 h-4 transition-colors ${focusedField === "email" ? "text-blue-500" : "text-gray-400"}`}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  onFocus={() => setFocusedField("email")} onBlur={() => setFocusedField(null)}
                  placeholder="admin@ensa-eljadida.ac.ma" required
                  className="w-full bg-transparent text-gray-800 placeholder-gray-300 text-sm pl-10 pr-4 py-3 rounded-xl outline-none" />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wider">Mot de passe</label>
              <div className={`relative rounded-xl border-2 transition-all duration-200 ${
                focusedField === "password"
                  ? "border-blue-400 bg-white shadow-[0_0_0_3px_rgba(30,86,160,0.08)]"
                  : "border-gray-200 bg-gray-50"}`}>
                <div className="absolute left-3.5 top-1/2 -translate-y-1/2">
                  <svg className={`w-4 h-4 transition-colors ${focusedField === "password" ? "text-blue-500" : "text-gray-400"}`}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input type={showPassword ? "text" : "password"} value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onFocus={() => setFocusedField("password")} onBlur={() => setFocusedField(null)}
                  placeholder="••••••••" required
                  className="w-full bg-transparent text-gray-800 placeholder-gray-300 text-sm pl-10 pr-12 py-3 rounded-xl outline-none" />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-500 transition-colors">
                  {showPassword
                    ? <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                    : <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                  }
                </button>
              </div>
            </div>

            <div className="flex justify-end">
              <button type="button" className="text-xs font-semibold hover:underline transition-colors"
                style={{ color: "#e87722" }}>Mot de passe oublié ?</button>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-xl px-3 py-2.5">
                  <svg className="w-4 h-4 text-red-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-red-500 text-xs">{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            <motion.button type="submit" disabled={loading} whileTap={{ scale: 0.98 }}
              className="relative w-full py-3 rounded-xl text-sm font-bold text-white overflow-hidden shadow-lg transition-all"
              style={{ background: "linear-gradient(135deg, #1e56a0, #2568b5)" }}>
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  Connexion...
                </span>
              ) : "Se connecter"}
            </motion.button>
          </motion.form>

          <p className="text-center text-xs text-gray-300 mt-5">
            Accès réservé aux administrateurs et enseignants
          </p>
        </div>
        <p className="text-center text-xs text-gray-400 mt-3">ENSA El Jadida — PFA 2024/2025</p>
      </motion.div>
    </div>
  );
};

export default LoginPage;