import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState
} from "react";

import api, { TOKEN_KEY } from "../api/client";
import {
  getCurrentUser,
  loginUser
} from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    sessionStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }, []);

  const login = useCallback(async (credentials) => {
    const result = await loginUser(credentials);

    if (!result.access_token) {
      throw new Error("The login response did not contain an access token.");
    }

    sessionStorage.setItem(TOKEN_KEY, result.access_token);

    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      return currentUser;
    } catch (error) {
      sessionStorage.removeItem(TOKEN_KEY);
      setUser(null);
      throw error;
    }
  }, []);

  useEffect(() => {
    let active = true;

    async function restoreSession() {
      const token = sessionStorage.getItem(TOKEN_KEY);

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();

        if (active) {
          setUser(currentUser);
        }
      } catch {
        sessionStorage.removeItem(TOKEN_KEY);

        if (active) {
          setUser(null);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    restoreSession();

    const handleUnauthorized = () => {
      if (active) {
        setUser(null);
        setLoading(false);
      }
    };

    window.addEventListener(
      "auth:unauthorized",
      handleUnauthorized
    );

    return () => {
      active = false;
      window.removeEventListener(
        "auth:unauthorized",
        handleUnauthorized
      );
    };
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      logout
    }),
    [user, loading, login, logout]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside an AuthProvider"
    );
  }

  return context;
}
