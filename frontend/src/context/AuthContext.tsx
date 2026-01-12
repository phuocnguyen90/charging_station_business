"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "@/i18n/navigation";
import { api } from "@/lib/api";

interface User {
    email: string;
    full_name: string;
    role: string;
}

interface AuthContextType {
    user: User | null;
    login: (token: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    login: async () => { },
    logout: () => { },
    isAuthenticated: false,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const router = useRouter();

    useEffect(() => {
        // Check for token on mount
        const loadUser = async () => {
            const token = localStorage.getItem("token");
            if (token) {
                try {
                    const res = await api.get("/auth/me");
                    setUser(res.data);
                } catch (err) {
                    console.error("Failed to load user", err);
                    localStorage.removeItem("token");
                }
            }
        };
        loadUser();
    }, []);

    const login = async (token: string) => {
        localStorage.setItem("token", token);
        try {
            const res = await api.get("/auth/me");
            setUser(res.data);
        } catch {
            // Handle error
        }
    };

    const logout = () => {
        localStorage.removeItem("token");
        setUser(null);
        router.push("/auth/login");
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
