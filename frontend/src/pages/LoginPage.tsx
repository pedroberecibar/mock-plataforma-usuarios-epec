import { useState } from "react";
import { postLogin } from "../api/auth";
import type { AuthState } from "../hooks/auth";
import {
  bg, border, brand, color, fg,
  font, fontSize, fontWeight, radius, shadow, space,
} from "../design-tokens";

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
      onLogin({ token: res.token, suministroId: res.suministro_id });
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
      flexDirection:  "column",
      alignItems:     "center",
      justifyContent: "center",
      background:     bg.page,
      fontFamily:     font.sans,
      padding:        `${space[6]}px ${space[4]}px`,
    }}>

      {/* Brand header strip */}
      <div style={{
        background:     brand.primary,
        width:          "100%",
        position:       "fixed",
        top:            0,
        left:           0,
        height:         56,
        display:        "flex",
        alignItems:     "center",
        padding:        `0 ${space[6]}px`,
        gap:            space[3],
        zIndex:         10,
      }}>
        <img src="/epec-logo-white.png" alt="EPEC" height={32} />
        <span style={{ color: color.green200, fontSize: fontSize.xs, fontWeight: fontWeight.medium, letterSpacing: "0.03em" }}>
          Plataforma de Clientes
        </span>
      </div>

      {/* Login card */}
      <div style={{
        background:   bg.surface,
        border:       `1px solid ${border.default}`,
        borderRadius: radius.lg,
        boxShadow:    shadow.lg,
        padding:      `${space[10]}px ${space[8]}px`,
        width:        "100%",
        maxWidth:     400,
      }}>

        {/* Tagline */}
        <p style={{
          fontFamily:  font.sans,
          fontSize:    fontSize.xs,
          color:       fg.secondary,
          margin:      0,
          marginBottom: space[8],
          textAlign:   "center",
          letterSpacing: "0.01em",
        }}>
          Su consumo eléctrico, claro y en kWh
        </p>

        <h1 style={{
          fontFamily:   font.sans,
          fontSize:     fontSize.xl,
          fontWeight:   fontWeight.semibold,
          color:        fg.primary,
          margin:       0,
          marginBottom: space[6],
          textAlign:    "center",
        }}>
          Iniciar sesión
        </h1>

        <form onSubmit={handleSubmit} noValidate>
          {/* Usuario */}
          <div style={{ marginBottom: space[4] }}>
            <label htmlFor="usuario" style={labelStyle}>Usuario</label>
            <input
              id="usuario"
              type="text"
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
              autoComplete="username"
              required
              disabled={loading}
              style={inputStyle}
            />
          </div>

          {/* Contraseña */}
          <div style={{ marginBottom: space[6] }}>
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
              color:        color.error,
              background:   color.errorLight,
              border:       `1px solid ${color.error}`,
              borderRadius: radius.sm,
              padding:      `${space[2]}px ${space[3]}px`,
              margin:       0,
              marginBottom: space[4],
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
              background:   loading ? color.green400 : brand.primary,
              color:        color.white,
              border:       "none",
              borderRadius: radius.md,
              padding:      `${space[3]}px`,
              fontSize:     fontSize.base,
              fontWeight:   fontWeight.semibold,
              fontFamily:   font.sans,
              cursor:       loading || !usuario || !password ? "not-allowed" : "pointer",
              opacity:      loading || !usuario || !password ? 0.7 : 1,
              transition:   "background 0.15s",
            }}
          >
            {loading ? "Ingresando…" : "Ingresar"}
          </button>
        </form>
      </div>
    </div>
  );
}

const labelStyle: React.CSSProperties = {
  display:      "block",
  fontFamily:   font.sans,
  fontSize:     fontSize.sm,
  fontWeight:   fontWeight.medium,
  color:        fg.secondary,
  marginBottom: space[1],
};

const inputStyle: React.CSSProperties = {
  display:      "block",
  width:        "100%",
  boxSizing:    "border-box",
  fontFamily:   font.sans,
  fontSize:     fontSize.base,
  color:        fg.primary,
  background:   bg.surface,
  border:       `1px solid ${border.default}`,
  borderRadius: radius.md,
  padding:      `${space[3]}px ${space[4]}px`,
  outline:      "none",
};

import type React from "react";
