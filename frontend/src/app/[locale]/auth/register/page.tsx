"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Link, useRouter } from "@/i18n/navigation";
import { toast } from "sonner";

const registerSchema = z.object({
    email: z.string().email("Invalid email"),
    full_name: z.string().min(2, "Name required"),
    password: z.string().min(6, "Password must be at least 6 characters"),
    confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
});

type FormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);

    const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data: FormData) => {
        setLoading(true);
        try {
            await api.post("/auth/register", {
                email: data.email,
                full_name: data.full_name,
                password: data.password,
                role: "client" // Hardcoded for now
            });

            toast.success("Account created! Please login.");
            router.push("/auth/login");
        } catch (err: any) {
            console.error(err);
            toast.error(err.response?.data?.detail || "Registration failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Create Account</CardTitle>
                <CardDescription>Get started with Solar ROI</CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <div className="space-y-2">
                        <Label>Full Name</Label>
                        <Input {...register("full_name")} placeholder="John Doe" />
                        {errors.full_name && <p className="text-red-500 text-sm">{errors.full_name.message}</p>}
                    </div>
                    <div className="space-y-2">
                        <Label>Email</Label>
                        <Input {...register("email")} placeholder="name@example.com" />
                        {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
                    </div>
                    <div className="space-y-2">
                        <Label>Password</Label>
                        <Input type="password" {...register("password")} />
                        {errors.password && <p className="text-red-500 text-sm">{errors.password.message}</p>}
                    </div>
                    <div className="space-y-2">
                        <Label>Confirm Password</Label>
                        <Input type="password" {...register("confirmPassword")} />
                        {errors.confirmPassword && <p className="text-red-500 text-sm">{errors.confirmPassword.message}</p>}
                    </div>
                    <Button type="submit" className="w-full" disabled={loading}>
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Register
                    </Button>
                </form>
            </CardContent>
            <CardFooter className="justify-center">
                <p className="text-sm text-gray-500">
                    Already have an account? <Link href="/auth/login" className="underline text-primary">Login</Link>
                </p>
            </CardFooter>
        </Card>
    );
}
