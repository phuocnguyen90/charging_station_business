import { Link } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const t = useTranslations('Dashboard');

    return (
        <div className="flex min-h-screen">
            {/* Sidebar - Simple implementation for now */}
            <aside className="w-64 bg-slate-900 text-white p-6 hidden md:block">
                <div className="text-xl font-bold mb-8">Solar ROI</div>
                <nav className="space-y-4">
                    <Link href="/dashboard/client/wizard" className="block hover:text-blue-400">
                        {t('client')}
                    </Link>
                    <Link href="/dashboard/installer" className="block hover:text-blue-400 text-gray-400">
                        {t('installer')} (WIP)
                    </Link>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 bg-gray-50 p-8">
                {children}
            </main>
        </div>
    );
}
