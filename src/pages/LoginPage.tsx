import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Mail, Lock, Eye, EyeOff, Loader2, Film, ArrowLeft } from "lucide-react";
import { Logo } from "../components/layout/Logo";
import { mockLogin } from "../lib/mock-services";
import { Modal } from "../components/ui/Modal";
import { Input } from "../components/ui/Input";

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [emailError, setEmailError] = useState("");
  const [resetSent, setResetSent] = useState(false);
  const [resetOpen, setResetOpen] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [sessionExpired, setSessionExpired] = useState(false);

  React.useEffect(() => {
    const session = localStorage.getItem("narrativ_session");
    if (session) {
      navigate("/dashboard");
    }
    const expired = new URLSearchParams(window.location.hash).get("expired");
    if (expired === "true") {
      setSessionExpired(true);
      localStorage.removeItem("narrativ_session");
    }
  }, [navigate]);

  const validateEmail = (val: string) => {
    if (!val) return "";
    if (!val.includes("@") || !val.includes(".")) return "Please enter a valid email address.";
    return "";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    const emailErr = validateEmail(email);
    if (emailErr) {
      setEmailError(emailErr);
      return;
    }
    setEmailError("");

    setLoading(true);
    const result = await mockLogin(email, password);
    setLoading(false);

    if (result.success) {
      localStorage.setItem("narrativ_session", JSON.stringify({
        email,
        name: "Min Min Ei",
        role: "Owner",
        loginTime: new Date().toISOString(),
      }));
      navigate("/dashboard");
    } else {
      setError(result.error || "Invalid credentials. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: `repeating-linear-gradient(0deg, transparent, transparent 2px, #8B7CFF 2px, #8B7CFF 4px)`,
      }} />
      <div className="absolute top-0 left-0 w-[400px] h-[400px] bg-primary/10 rounded-full blur-[120px]" />
      <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-secondary/10 rounded-full blur-[120px]" />

      <div className="relative w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-3">
            <Logo size={48} />
          </div>
          <div className="text-[10px] font-mono tracking-widest text-text-muted uppercase mb-1">LOGIXA Ecosystem</div>
          <h1 className="text-xl font-bold text-text-main">Narrativ Forge</h1>
          <p className="text-sm text-text-muted mt-1">Burmese Short-Form Video Production Studio</p>
        </div>

        <div className="bg-surface border border-border rounded-xl p-6 shadow-2xl">
          {sessionExpired && (
            <div className="mb-4 p-3 bg-warning/10 border border-warning/30 rounded-md text-xs text-warning">
              Your session has expired. Please sign in again.
            </div>
          )}

          {resetSent && (
            <div className="mb-4 p-3 bg-success/10 border border-success/30 rounded-md text-xs text-success">
              Password reset link sent to your email (simulated).
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-text-sec">Email</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setEmailError(""); }}
                  onFocus={() => setError("")}
                  placeholder="you@narrativ.studio"
                  className={`w-full bg-surface border rounded-md pl-9 pr-3 py-2 text-sm text-text-main placeholder:text-text-muted focus:outline-none focus:ring-1 transition-colors ${emailError ? "border-error focus:ring-error" : "border-border focus:border-primary focus:ring-primary"}`}
                />
              </div>
              {emailError && <p className="text-xs text-error">{emailError}</p>}
            </div>

            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-text-sec">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setError(""); }}
                  onFocus={() => setError("")}
                  placeholder="••••••••"
                  className="w-full bg-surface border border-border rounded-md pl-9 pr-9 py-2 text-sm text-text-main placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-sec"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="w-4 h-4 rounded border-border bg-surface accent-primary"
                />
                <span className="text-xs text-text-sec">Remember me</span>
              </label>
              <button
                type="button"
                onClick={() => setResetOpen(true)}
                className="text-xs text-primary hover:text-primary-dim transition-colors"
              >
                Forgot password?
              </button>
            </div>

            {error && (
              <div className="p-2.5 bg-error/10 border border-error/30 rounded-md text-xs text-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-white font-medium py-2.5 rounded-md hover:bg-primary-dim transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          <div className="mt-5 pt-4 border-t border-border space-y-2">
            <div className="flex items-center gap-2 text-[11px] text-text-muted">
              <div className="w-1.5 h-1.5 rounded-full bg-amber" />
              <span>Private invite-only workspace</span>
            </div>
            <div className="flex items-center gap-2 text-[11px] text-text-muted">
              <div className="w-1.5 h-1.5 rounded-full bg-text-muted" />
              <span>No public registration</span>
            </div>
          </div>
        </div>

        <div className="text-center mt-4 text-[10px] text-text-muted">
          <span>Demo: any valid email and 4+ char password</span>
        </div>
      </div>

      <Modal
        open={resetOpen}
        onClose={() => setResetOpen(false)}
        title="Reset Password"
        description="Enter your email to receive a reset link (simulated)."
        footer={
          <>
            <button onClick={() => setResetOpen(false)} className="btn-ghost text-sm">Cancel</button>
            <button
              onClick={() => {
                setResetSent(true);
                setResetOpen(false);
                setTimeout(() => setResetSent(false), 5000);
              }}
              className="btn-primary text-sm"
            >
              Send Reset Link
            </button>
          </>
        }
      >
        <Input
          label="Email"
          type="email"
          value={resetEmail}
          onChange={(e) => setResetEmail(e.target.value)}
          placeholder="you@narrativ.studio"
        />
      </Modal>
    </div>
  );
}
