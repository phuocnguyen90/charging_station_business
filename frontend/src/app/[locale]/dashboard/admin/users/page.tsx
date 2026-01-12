"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { api } from "@/lib/api";
import { Loader2, Shield } from "lucide-react";
import { toast } from "sonner";

interface User {
    id: number;
    email: string;
    full_name: string;
    role: string;
}

export default function AdminUsersPage() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState<number | null>(null);

    const fetchUsers = async () => {
        try {
            const res = await api.get("/admin/users");
            setUsers(res.data);
        } catch (err: any) {
            console.error(err);
            toast.error(err.response?.data?.detail || "Failed to load users");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleRoleChange = async (userId: number, newRole: string) => {
        setUpdating(userId);
        try {
            await api.put(`/admin/users/${userId}/role?role=${newRole}`);
            toast.success("User role updated");
            setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
        } catch (err: any) {
            console.error(err);
            toast.error("Failed to update role");
        } finally {
            setUpdating(null);
        }
    };

    if (loading) return <div>Loading users...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">User Management</h1>
                    <p className="text-muted-foreground">Manage system users and access roles.</p>
                </div>
            </div>

            <Card>
                <CardContent className="p-0">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>ID</TableHead>
                                <TableHead>User</TableHead>
                                <TableHead>Role</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {users.map((user) => (
                                <TableRow key={user.id}>
                                    <TableCell>{user.id}</TableCell>
                                    <TableCell>
                                        <div className="font-medium">{user.full_name}</div>
                                        <div className="text-sm text-gray-500">{user.email}</div>
                                    </TableCell>
                                    <TableCell>
                                        <Select
                                            disabled={updating === user.id}
                                            onValueChange={(v) => handleRoleChange(user.id, v)}
                                            value={user.role}
                                        >
                                            <SelectTrigger className="w-[130px]">
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="client">Client</SelectItem>
                                                <SelectItem value="installer">Installer</SelectItem>
                                                <SelectItem value="admin">Admin</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        {updating === user.id && <Loader2 className="h-4 w-4 animate-spin ml-auto" />}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
