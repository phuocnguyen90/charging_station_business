"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { api } from "@/lib/api";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "@/i18n/navigation";
import { toast } from "sonner";

// --- Schema Definition ---
const step1Schema = z.object({
    monthly_bill: z.coerce.number().min(1, "Bill must be positive"),
    currency: z.string().default("USD"),
});

const step2Schema = z.object({
    roof_area: z.coerce.number().min(5, "Roof area must be at least 5m2"),
    location: z.string().min(2, "Location required"),
    profile: z.string().default("standard"),
});

// Combined schema for final submit
const formSchema = step1Schema.merge(step2Schema);
type FormData = z.infer<typeof formSchema>;

export default function WizardPage() {
    const t = useTranslations("Index"); // Reusing for now
    const { isAuthenticated } = useAuth();
    const router = useRouter();

    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [lastData, setLastData] = useState<FormData | null>(null);

    const { register, handleSubmit, formState: { errors }, trigger, setValue, watch, getValues } = useForm<FormData>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            monthly_bill: 100,
            currency: "USD",
            roof_area: 50,
            location: "Hanoi",
            profile: "standard"
        }
    });

    const nextStep = async () => {
        // Validate current step fields
        let valid = false;
        if (step === 1) valid = await trigger(["monthly_bill", "currency"]);
        if (step === 2) valid = await trigger(["roof_area", "location", "profile"]);

        if (valid) setStep((s) => s + 1);
    };

    const prevStep = () => setStep((s) => s - 1);

    const onSubmit = async (data: FormData) => {
        setLoading(true);
        setLastData(data); // Store for saving later
        try {
            // Map form data to backend SimulationConfig
            const payload = {
                simulation_days: 365,
                num_stations: 1, // Default 1 "system"
                solar_panel_power_kw: 0.4, // 400W panels
                total_panels: Math.ceil((data.monthly_bill / 20)), // Very rough heuristic
                battery_capacity_kwh: 10.0,
                minutes_per_step: 60,
                battery_max_discharge_kw: 5.0,
                inverter_efficiency: 0.95
            };

            const res = await api.post("/simulation/run", payload);
            setResult(res.data);
            setStep(3); // Result step
        } catch (err) {
            console.error(err);
            toast.error("Simulation failed");
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!isAuthenticated) {
            toast.info("Please login to save your estimate");
            // In real app, we'd persist state. 
            router.push("/auth/login");
            return;
        }

        if (!lastData) return;

        setSaving(true);
        try {
            await api.post("/quotes/requests", {
                monthly_bill: lastData.monthly_bill,
                currency: lastData.currency,
                location: lastData.location,
                roof_area: lastData.roof_area,
                usage_profile_type: lastData.profile,
                interaction_source: "wizard"
            });
            toast.success("Quote saved successfully!");
        } catch (err) {
            console.error(err);
            toast.error("Failed to save quote");
        } finally {
            setSaving(false);
        }
    };

    if (result && step === 3) {
        return (
            <div className="space-y-6">
                <h1 className="text-3xl font-bold">Your Estimate</h1>
                <div className="grid gap-4 md:grid-cols-3">
                    <Card>
                        <CardHeader><CardTitle>ROI</CardTitle></CardHeader>
                        <CardContent className="text-2xl font-bold text-green-600">
                            {(result.roi_metrics.roi * 100).toFixed(1)}%
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader><CardTitle>Payback Period</CardTitle></CardHeader>
                        <CardContent className="text-2xl font-bold">
                            {result.roi_metrics.payback_years.toFixed(1)} Years
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader><CardTitle>Annual Savings</CardTitle></CardHeader>
                        <CardContent className="text-2xl font-bold">
                            ${result.roi_metrics.net_profit.toFixed(0)}
                        </CardContent>
                    </Card>
                </div>

                <div className="flex gap-4">
                    <Button onClick={() => { setStep(1); setResult(null); }} variant="outline">Start Over</Button>

                    {isAuthenticated ? (
                        <Button onClick={handleSave} disabled={saving}>
                            {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Save Estimate
                        </Button>
                    ) : (
                        <Button onClick={handleSave} variant="secondary">
                            Login to Save
                        </Button>
                    )}
                </div>
            </div>
        )
    }

    return (
        <div className="max-w-xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Solar Estimator</h1>
                <div className="flex gap-2">
                    <div className={`h-2 flex-1 rounded ${step >= 1 ? 'bg-primary' : 'bg-gray-200'}`} />
                    <div className={`h-2 flex-1 rounded ${step >= 2 ? 'bg-primary' : 'bg-gray-200'}`} />
                    <div className={`h-2 flex-1 rounded ${step >= 3 ? 'bg-primary' : 'bg-gray-200'}`} />
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Step {step}: {step === 1 ? "Usage" : "Property"}</CardTitle>
                    <CardDescription>Tell us about your needs</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">

                        {step === 1 && (
                            <>
                                <div className="space-y-2">
                                    <Label>Monthly Bill Estimate</Label>
                                    <div className="flex gap-2">
                                        <Input type="number" {...register("monthly_bill")} />
                                        <Select onValueChange={v => setValue("currency", v)} defaultValue="USD">
                                            <SelectTrigger className="w-[100px]">
                                                <SelectValue placeholder="Currency" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="USD">USD</SelectItem>
                                                <SelectItem value="VND">VND</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    {errors.monthly_bill && <p className="text-red-500 text-sm">{errors.monthly_bill.message}</p>}
                                </div>
                            </>
                        )}

                        {step === 2 && (
                            <>
                                <div className="space-y-2">
                                    <Label>Roof Area (m2)</Label>
                                    <Input type="number" {...register("roof_area")} />
                                    {errors.roof_area && <p className="text-red-500 text-sm">{errors.roof_area.message}</p>}
                                </div>
                                <div className="space-y-2">
                                    <Label>Location</Label>
                                    <Select onValueChange={v => setValue("location", v)} defaultValue="Hanoi">
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select City" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="Hanoi">Hanoi</SelectItem>
                                            <SelectItem value="HCM">Ho Chi Minh City</SelectItem>
                                            <SelectItem value="Danang">Danang</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2">
                                    <Label>Usage Profile</Label>
                                    <Select onValueChange={v => setValue("profile", v)} defaultValue="standard">
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select Profile" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="standard">Standard Family</SelectItem>
                                            <SelectItem value="working_9_5">Office Worker (9-5)</SelectItem>
                                            <SelectItem value="night_owl">Night Owl</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </>
                        )}

                        <div className="flex justify-between pt-4">
                            {step > 1 && (
                                <Button type="button" variant="outline" onClick={prevStep}>Back</Button>
                            )}

                            {step < 2 ? (
                                <Button type="button" className="ml-auto" onClick={nextStep}>Next</Button>
                            ) : (
                                <Button type="submit" className="ml-auto" disabled={loading}>
                                    {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                    Calculate
                                </Button>
                            )}
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
