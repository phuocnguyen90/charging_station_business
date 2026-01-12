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
    login: (token: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    login: () => { },
    logout: () => { },
    isAuthenticated: false,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const router = useRouter();

    useEffect(() => {
        // Check for token on mount
        const token = localStorage.getItem("token");
        if (token) {
            // Ideally we fetch user profile here. For POC we just decode or assume logic.
            // Let's decode or simply set generic user if decoding logic isn't handy on client without lib
            // For security, we should have an endpoint /auth/me. 
            // We'll skip /auth/me for this step and just trust the token exists.
            setUser({ email: "user@example.com", full_name: "User", role: "client" });
        }
    }, []);

    const login = (token: string) => {
        localStorage.setItem("token", token);
        setUser({ email: "user@example.com", full_name: "Current User", role: "client" }); // Placeholder
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
