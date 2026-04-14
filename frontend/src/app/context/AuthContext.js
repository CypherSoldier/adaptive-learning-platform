"use client"
// changing to .ts causes problems, why?

import { createContext, useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { auth, googleProvider } from '@/lib/firebase';
import { signInWithPopup } from 'firebase/auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isLoggedIn, setLoggedIn] = useState(false);
    const [jwtLoggedIn, setJWTLogin] = useState(false);
    const [error, setError] = useState(null);
    const router = useRouter();

    const register = async (full_name, email, password) => {
        try {
            const response = await axios.post("http://localhost:8000/auth/", {
                full_name,
                email,
                password,
            });
            console.log("Registration successful", response.data);
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
          await signInWithPopup(auth, googleProvider);
          
          console.log("Signed in with Google")
          setLoggedIn(true);
          router.push("/");
        } catch (err) {
          console.error("Google sign-in error:", err);
          setError(err instanceof Error ? err.message : 'An unknown error occurred');
        }
    };

    const login = async (email, password) => {
        try {
            const formData = new FormData();
            formData.append("username", email);
            formData.append("password", password);

            // call fastapi backend
            const response = await axios.post("http://localhost:8000/auth/token", formData, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });
            axios.defaults.headers.common["Authorization"] = `Bearer ${response.data.access_token}`;
            localStorage.setItem("token", response.data.access_token);
            setUser(response.data);
            setLoggedIn(true);
            setJWTLogin(true);
            router.push("/");
        } catch (error) {
            console.error("Login failed:", error);
        }
    };

    const logout = () => {
        setUser(null);
        delete axios.defaults.headers.common["Authorization"];
        setLoggedIn(false);
        router.push("/login");
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, register, isLoggedIn, signInWithGoogle, jwtLoggedIn }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;