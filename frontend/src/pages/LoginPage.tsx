import { useState } from "react";
import { postLogin } from "../api/auth";
import type { AuthState } from "../hooks/auth";
import {
  bg, border, brand, color, fg,
  font, fontSize, fontWeight, radius, space,
} from "../design-tokens";
import type React from "react";

interface Props {
  onLogin: (auth: AuthState) => void;
}

const IconEye = ({ off }: { off: boolean }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {off ? (
      <>
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
        <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
        <line x1="1" y1="1" x2="23" y2="23" />
      </>
    ) : (
      <>
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
        <circle cx="12" cy="12" r="3" />
      </>
    )}
  </svg>
);

export function LoginPage({ onLogin }: Props) {
  const [usuario, setUsuario] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await postLogin(usuario, password);
      onLogin({
        token: res.token,
        suministroId: res.suministro_id,
        nombre: res.nombre,
        nroSuministro: res.nro_suministro,
      });
    } catch {
      setError("Usuario o contraseña incorrectos.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight:      "100vh",
      display:        "flex",
      alignItems:     "center",
      justifyContent: "center",
      background:     bg.page,
      fontFamily:     font.sans,
      padding:        `${space[4]}px`,
    }}>
      {/* Login card — split layout (Stitch: decorative left + form right) */}
      <div style={{
        display:      "flex",
        width:        "100%",
        maxWidth:     880,
        background:   bg.surfaceFeat,
        borderRadius: `${radius["2xl"]}px`,
        boxShadow:    "0 8px 32px rgba(180,140,80,0.12), 0 2px 8px rgba(100,80,60,0.08)",
        border:       "none",
        overflow:     "hidden",
      }}>

        {/* Left panel — decorative (hidden on mobile via CSS class) */}
        <div
          className="login-panel-left"
          style={{
            width:          "50%",
            background:     brand.primary,
            padding:        space[16],
            flexDirection:  "column",
            justifyContent: "space-between",
            color:          color.white,
          }}
        >
          {/* Top: logo + tagline */}
          <div style={{ display: "flex", flexDirection: "column", gap: space[6] }}>
            <img
              src="/epec-logo-transparent.png"
              alt="EPEC"
              style={{ height: 52, width: "auto", objectFit: "contain" }}
            />
            <div style={{ marginTop: space[10] }}>
              <h2 style={{
                fontFamily:   font.sans,
                fontSize:     fontSize["2xl"],
                fontWeight:   fontWeight.semibold,
                lineHeight:   1.25,
                margin:       0,
                marginBottom: space[3],
                letterSpacing: "-0.01em",
              }}>
                Su consumo eléctrico, claro y en kWh
              </h2>
              <p style={{
                fontFamily: font.sans,
                fontSize:   fontSize.md,
                fontWeight: fontWeight.regular,
                margin:     0,
                opacity:    0.8,
                lineHeight: 1.5,
              }}>
                Acceda a su oficina virtual para gestionar sus facturas y monitorear su suministro.
              </p>
            </div>
          </div>
          {/* Bottom: brand label */}
          <div style={{ display: "flex", alignItems: "center", gap: space[1], color: color.green400 }}>
            <span style={{ fontSize: fontSize.xs, fontFamily: font.mono, letterSpacing: "0.1em", textTransform: "uppercase" as const }}>
              Energía de Córdoba
            </span>
          </div>
        </div>

        {/* Right panel — form */}
        <div
          className="login-panel-right"
          style={{
            padding:        `${space[10]}px ${space[16]}px`,
            display:        "flex",
            flexDirection:  "column",
            justifyContent: "center",
          }}
        >
          <div style={{ maxWidth: 360, width: "100%" }}>

            <header style={{ marginBottom: space[10] }}>
              <img
                src="/epec-logo-primary.png"
                alt="EPEC"
                style={{ height: 40, width: "auto", objectFit: "contain", marginBottom: space[4], display: "block" }}
              />
              <p style={{
                fontFamily:  font.sans,
                fontSize:    fontSize.base,
                color:       fg.secondary,
                margin:      0,
              }}>
                Inicie sesión para continuar
              </p>
            </header>

            <form onSubmit={handleSubmit} noValidate style={{ display: "flex", flexDirection: "column", gap: space[6] }}>

              {/* Usuario */}
              <div style={{ display: "flex", flexDirection: "column", gap: space[1] }}>
                <label htmlFor="usuario" style={labelStyle}>Número de Suministro</label>
                <input
                  id="usuario"
                  type="text"
                  value={usuario}
                  onChange={(e) => setUsuario(e.target.value)}
                  placeholder="ej. 3037481"
                  autoComplete="username"
                  required
                  disabled={loading}
                  style={inputStyle}
                />
              </div>

              {/* Contraseña */}
              <div style={{ display: "flex", flexDirection: "column", gap: space[1] }}>
                <label htmlFor="password" style={labelStyle}>Contraseña</label>
                <div style={{ position: "relative" }}>
                  <input
                    id="password"
                    type={showPass ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
                    required
                    disabled={loading}
                    style={{ ...inputStyle, paddingRight: 44 }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass((v) => !v)}
                    aria-label={showPass ? "Ocultar contraseña" : "Mostrar contraseña"}
                    style={{
                      position:   "absolute",
                      right:      12,
                      top:        "50%",
                      transform:  "translateY(-50%)",
                      background: "none",
                      border:     "none",
                      cursor:     "pointer",
                      color:      fg.muted,
                      padding:    0,
                      display:    "flex",
                      alignItems: "center",
                    }}
                  >
                    <IconEye off={showPass} />
                  </button>
                </div>
              </div>

              {/* Error */}
              {error && (
                <p role="alert" style={{
                  fontFamily:   font.sans,
                  fontSize:     fontSize.sm,
                  color:        color.errorDark,
                  background:   color.errorLight,
                  border:       `1px solid ${color.error}`,
                  borderRadius: radius.md,
                  padding:      `${space[2]}px ${space[3]}px`,
                  margin:       0,
                }}>
                  {error}
                </p>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={loading || !usuario || !password}
                style={{
                  width:        "100%",
                  height:       48,
                  background:   loading ? color.green400 : brand.primary,
                  color:        color.white,
                  border:       "none",
                  borderRadius: `${radius.md}px`,
                  fontSize:     fontSize.base,
                  fontWeight:   fontWeight.semibold,
                  fontFamily:   font.sans,
                  cursor:       loading || !usuario || !password ? "not-allowed" : "pointer",
                  opacity:      loading || !usuario || !password ? 0.7 : 1,
                  transition:   "background 0.15s, opacity 0.15s",
                  display:      "flex",
                  alignItems:   "center",
                  justifyContent: "center",
                  gap:          space[2],
                }}
              >
                {loading ? "Ingresando…" : "Ingresar"}
              </button>
            </form>
          </div>
        </div>

      </div>
    </div>
  );
}

const labelStyle: React.CSSProperties = {
  display:       "block",
  fontFamily:    font.sans,
  fontSize:      fontSize.xs,
  fontWeight:    fontWeight.medium,
  color:         fg.secondary,
  letterSpacing: "0.05em",
};

const inputStyle: React.CSSProperties = {
  display:      "block",
  width:        "100%",
  boxSizing:    "border-box",
  height:       48,
  fontFamily:   font.sans,
  fontSize:     fontSize.base,
  color:        fg.primary,
  background:   bg.surface,
  border:       `1px solid ${border.default}`,
  borderRadius: `${radius.md}px`,
  padding:      `0 ${space[3]}px`,
  outline:      "none",
  transition:   "border-color 150ms ease",
};
