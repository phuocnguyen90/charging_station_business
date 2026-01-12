import { Button } from "@/components/ui/button";
import { Link } from '@/i18n/navigation';
import { useTranslations } from "next-intl";

export default function Home() {
  const t = useTranslations('Index');

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <main className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <div className="max-w-3xl space-y-6">
          <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl text-primary">
            {t('title')}
          </h1>
          <p className="text-xl text-muted-foreground">
            {t('subtitle')}
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button asChild size="lg">
              <Link href="/dashboard/client/wizard">{t('getStarted')}</Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/auth/login">{t('login')}</Link>
            </Button>
          </div>
        </div>
      </main>

      <footer className="py-6 text-center text-sm text-muted-foreground border-t">
        <p>© 2026 Solar ROI. All rights reserved.</p>
      </footer>
    </div>
  );
}
