"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { api } from "@/lib/api";
import { Loader2, Plus, Package } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/context/AuthContext";

// Types from Backend
interface ProductModel {
    id: int;
    model_number: string;
    brand: { name: string };
    type: string;
}

interface InventoryListing {
    id: int;
    product: ProductModel;
    base_price: number;
    stock_level: number;
    currency: string;
}

const listingSchema = z.object({
    product_model_id: z.coerce.number().min(1, "Select a product"),
    base_price: z.coerce.number().min(0),
    stock_level: z.coerce.number().min(0),
    currency: z.string().default("USD"),
});

type FormData = z.infer<typeof listingSchema>;

export default function InventoryPage() {
    const { user } = useAuth();
    const [inventory, setInventory] = useState<InventoryListing[]>([]);
    const [catalog, setCatalog] = useState<ProductModel[]>([]);
    const [loading, setLoading] = useState(true);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    // Form
    const { register, handleSubmit, formState: { errors }, reset, setValue } = useForm<FormData>({
        resolver: zodResolver(listingSchema),
        defaultValues: {
            currency: "USD",
            stock_level: 10,
            base_price: 1000
        }
    });

    const fetchData = async () => {
        try {
            const [invRes, catRes] = await Promise.all([
                api.get("/market/inventory/my"),
                api.get("/market/catalog")
            ]);
            setInventory(invRes.data);
            setCatalog(catRes.data);
        } catch (err) {
            console.error(err);
            toast.error("Failed to load inventory data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const onSubmit = async (data: FormData) => {
        setSubmitting(true);
        try {
            await api.post("/market/inventory", data);
            toast.success("Item added to inventory");
            setDialogOpen(false);
            reset();
            fetchData(); // Refresh
        } catch (err: any) {
            console.error(err);
            toast.error(err.response?.data?.detail || "Failed to add item");
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <div>Loading inventory...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Inventory</h1>
                    <p className="text-muted-foreground">Manage your product offerings and pricing.</p>
                </div>

                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" /> Add Item
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[425px]">
                        <DialogHeader>
                            <DialogTitle>Add Inventory Item</DialogTitle>
                            <DialogDescription>
                                Select a product from the global catalog to sell.
                            </DialogDescription>
                        </DialogHeader>
                        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-4">

                            <div className="space-y-2">
                                <Label>Product Model</Label>
                                <Select onValueChange={(v) => setValue("product_model_id", parseInt(v))}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select Product" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {catalog.map((p) => (
                                            <SelectItem key={p.id} value={p.id.toString()}>
                                                {p.brand?.name ? `${p.brand.name} - ` : ""}{p.model_number} ({p.type})
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                {errors.product_model_id && <p className="text-red-500 text-sm">{errors.product_model_id.message}</p>}
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Base Price</Label>
                                    <Input type="number" {...register("base_price")} />
                                    {errors.base_price && <p className="text-red-500 text-sm">{errors.base_price.message}</p>}
                                </div>
                                <div className="space-y-2">
                                    <Label>Currency</Label>
                                    <Select onValueChange={v => setValue("currency", v)} defaultValue="USD">
                                        <SelectTrigger>
                                            <SelectValue placeholder="Currency" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="USD">USD</SelectItem>
                                            <SelectItem value="VND">VND</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label>Stock Level</Label>
                                <Input type="number" {...register("stock_level")} />
                            </div>

                            <DialogFooter>
                                <Button type="submit" disabled={submitting}>
                                    {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                    Add to Inventory
                                </Button>
                            </DialogFooter>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardContent className="p-0">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Product</TableHead>
                                <TableHead>Type</TableHead>
                                <TableHead>Price</TableHead>
                                <TableHead>Stock</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {inventory.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                                        No items in inventory. Add one to get started.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                inventory.map((item) => (
                                    <TableRow key={item.id}>
                                        <TableCell className="font-medium">
                                            <div className="flex items-center">
                                                <Package className="mr-2 h-4 w-4 text-gray-400" />
                                                <div>
                                                    <div className="font-bold">{item.product.brand?.name} {item.product.model_number}</div>
                                                    <div className="text-xs text-gray-500">Global ID: {item.product.id}</div>
                                                </div>
                                            </div>
                                        </TableCell>
                                        <TableCell className="capitalize">{item.product.type.replace('_', ' ')}</TableCell>
                                        <TableCell>{item.base_price.toLocaleString()} {item.currency}</TableCell>
                                        <TableCell>
                                            <span className={`px-2 py-1 rounded-full text-xs ${item.stock_level > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {item.stock_level} units
                                            </span>
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button variant="ghost" size="sm">Edit</Button>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
