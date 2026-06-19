"use client"

import { createContext, useState, useEffect, useCallback } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { auth, googleProvider } from '@/lib/firebase';
import { signInWithPopup, onAuthStateChanged } from 'firebase/auth';

const AuthContext = createContext();

function parseJwt(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

function setAxiosToken(token) {
  if (token) {
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common["Authorization"];
  }
}

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isLoggedIn, setLoggedIn] = useState(false);
    const [authLoading, setAuthLoading] = useState(true);
    const [error, setError] = useState(null);
    const router = useRouter();

    // Helpers
    const applySession = useCallback((token, userProfile) => {
        localStorage.setItem("token", token);
        setAxiosToken(token);
        setUser(userProfile);
        setLoggedIn(true);
    }, []);
 
    const clearSession = useCallback(() => {
        localStorage.removeItem("token");
        setAxiosToken(null);
        setUser(null);
        setLoggedIn(false);
    }, []);

    // Rehydrate session on mount
    useEffect(() => {
        let cancelled = false;
 
        const rehydrate = async () => {
            const token = localStorage.getItem("token");
 
            if (!token) {
                setAuthLoading(false);
                return;
            }
 
            setAxiosToken(token);
 
            try {
                const response = axios.get(`${process.env.NEXT_PUBLIC_API_URL}/users/me`);
                if (!cancelled) {
                    const u = response.data;
                    applySession(token, {
                        user_id: String(u.user_id ?? u.id),
                        uid: String(u.firebase_uid ?? u.user_id ?? u.id),
                        email: u.email,
                        full_name: u.full_name,
                    });
                }
            } catch {
                if (!cancelled) clearSession();
            } finally {
                if (!cancelled) setAuthLoading(false);
            }
        };
 
        rehydrate();
        return () => { cancelled = true; };
    }, []);

    const register = async (full_name, email, password) => {
        try {
            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/auth/`, {
                full_name,
                email,
                password,
            });
            //console.log("Registration successful");
            router.push('/login')
            return response.data;
        } catch (error) {
            console.error("Registration failed:", error);
            throw error;
        }
    };

    // Firebase Google Sign-In 
    const signInWithGoogle = async (e) => {
        e.preventDefault();
        try {
            const result = await signInWithPopup(auth, googleProvider);
            const firebaseUser = result.user;

            const idToken = await firebaseUser.getIdToken();

            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/auth/google`, {
                token: idToken
            });

            const jwtToken = response.data.access_token;
 
            applySession(jwtToken, {
                user_id: String(response.data.user?.user_id ?? response.data.user?.id ?? ""),
                uid: firebaseUser.uid,
                email: firebaseUser.email,
                full_name: firebaseUser.displayName,
            });
    
            router.push("/");
        } catch (err) {
            console.error("Google sign-in error:", err);
            setError(err.message);
        }
    };

    const login = async (email, password) => {
        try {
            const formData = new FormData();
            formData.append("username", email);
            formData.append("password", password);

            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/auth/token`, formData, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });

            const token = response.data.access_token;
 
            // Decode the JWT to get basic identity info without an extra round-trip,
            const payload = parseJwt(token);
            applySession(token, {
                user_id: payload?.id ?? null,
                uid: payload?.id ?? null,      
                email: payload?.sub ?? email,
                full_name: null,               
                });
 
            // Fetch full profile in the background
            axios.get(`${process.env.NEXT_PUBLIC_API_URL}/users/me`).then((res) => {
                const u = res.data;
                setUser((prev) => ({
                ...prev,
                full_name: u.full_name,
                user_id: String(u.user_id ?? u.id),
                }));
            }).catch(() => {});
 
            router.push("/");
        } catch (err) {
            console.error("Login failed:", err);
            const status = err.response?.status;
            if (status === 401) {
                setError("Invalid email or password. Please try again.");
            } else if (status === 422) {
                setError("Please enter a valid email and password.");
            } else {
                setError("Something went wrong. Please try again later.");
            }
        }
    };

    const logout = async () => {
        try {
            if (auth.currentUser) await auth.signOut();
        } catch { /* ignore */ }
            clearSession();
            router.push("/login");
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, register, isLoggedIn, signInWithGoogle, setLoggedIn, authLoading, error, setError }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;