import { useEffect, useState } from 'react';
import { Header } from '../components/layout/Header';
import { TransactionCard } from '../components/TransactionCard';
import { FloatingActionButton } from '../components/FloatingActionButton';
import { TrendingDown, DollarSign } from 'lucide-react';
import { mockTransactions, mockCategorySpending } from '../lib/mockData';
import { apiClient, getCurrentUserId, shouldUseMockData } from '../lib/api';

export function Home() {
  const [recentTransactions, setRecentTransactions] = useState<any[]>([]);
  const [categorySpending, setCategorySpending] = useState<typeof mockCategorySpending>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const userId = getCurrentUserId();
    const useMockData = shouldUseMockData(userId);

    if (!userId) {
      // This should not happen as ProtectedRoute prevents unauthenticated access
      console.warn('No user id found in localStorage.');
      setRecentTransactions([]);
      setCategorySpending([]);
      return;
    }

    if (useMockData) {
      // Use mock data
      setRecentTransactions(mockTransactions.slice(0, 20));
      setCategorySpending(mockCategorySpending.slice(0, 4));
      return;
    }

    let mounted = true;

    async function fetchTransactions() {
      setLoading(true);
      setError(null);
      try {
        // Calculate date range for current and last month
        const today = new Date();
        const firstDayOfLastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
        const startDate = firstDayOfLastMonth.toISOString().split('T')[0];
        const endDate = today.toISOString().split('T')[0];

        const response = (await apiClient.getTransactions(userId as number, {
          startDate,
          endDate,
          page: 1,
          pageSize: 20,
        })) as any;

        console.log('Home transactions response:', response);

        // Handle paginated response
        const data = response.transactions || response;

        // Map backend transaction shape to match Transaction interface
        const mapped = (data || []).map((tx: any) => ({
          id: tx.id,
          description: tx.description,
          transaction_date: tx.transaction_date,
          reference: tx.reference,
          amount: Number(tx.amount),
          entries: tx.entries || [],
          detailed_entries: tx.detailed_entries || [],
        }));

        if (mounted) {
          setRecentTransactions(mapped.length ? mapped : []);
          // For category spending on home page, aggregate from transactions
          const categoryMap = new Map<string, number>();
          mapped.forEach((tx: any) => {
            tx.entries?.forEach((entry: any) => {
              const name = entry.account_name || 'Other';
              categoryMap.set(name, (categoryMap.get(name) || 0) + Math.abs(Number(tx.amount)));
            });
          });
          
          // Convert to array and sort by amount
          const categories = Array.from(categoryMap.entries())
            .map(([category, amount]) => ({
              category,
              amount,
              percentage: 0,
              color: '#3b82f6',
            }))
            .sort((a, b) => b.amount - a.amount)
            .slice(0, 4);

          // Calculate percentages
          const maxAmount = Math.max(...categories.map(c => c.amount), 1);
          categories.forEach(c => {
            c.percentage = (c.amount / maxAmount) * 100;
          });

          setCategorySpending(categories);
        }
      } catch (err: any) {
        console.error('Failed to fetch transactions', err);
        if (mounted) setError(err?.message || 'Failed to fetch transactions');
      } finally {
        if (mounted) setLoading(false);
      }
    }

    fetchTransactions();

    return () => {
      mounted = false;
    };
  }, []);

  const totalSpendingThisMonth = Math.abs(
    recentTransactions
      .filter((t) => t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0)
  );



  const topTenTransactions = recentTransactions
    .sort((a, b) => Math.abs(b.amount) - Math.abs(a.amount))
    .slice(0, 10);
  const sumTopTenTransactions = topTenTransactions
    .reduce((sum, t) => sum + Math.abs(t.amount), 0);

  return (
    <div className="min-h-screen bg-background">
      <Header title="Dashboard" />

      <div className="max-w-7xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary mb-1">Total Spending This Month</p>
                <p className="text-2xl font-bold text-error">
                  ${totalSpendingThisMonth.toFixed(2)}
                </p>
              </div>
              <div className="p-3 bg-error/10 rounded-full">
                <TrendingDown className="h-6 w-6 text-error" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary mb-1">Top 10 Transactions Sum</p>
                <p className="text-2xl font-bold text-accent">
                  ${sumTopTenTransactions.toFixed(2)}
                </p>
              </div>
              <div className="p-3 bg-accent/10 rounded-full">
                <DollarSign className="h-6 w-6 text-accent" />
              </div>
            </div>
          </div>
        </div>

        {/* Top Spending Categories */}
        <div className="card">
          <h3 className="text-lg font-semibold text-primary mb-4">
            Top Spending Categories
          </h3>
          <div className="space-y-4">
            {categorySpending.length > 0 ? (
              categorySpending.map((category) => (
                <div key={category.category}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-primary">
                      {category.category}
                    </span>
                    <span className="text-sm font-semibold text-primary">
                      ${category.amount.toFixed(2)}
                    </span>
                  </div>
                  <div className="w-full bg-background rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all"
                      style={{
                        width: `${category.percentage}%`,
                        backgroundColor: category.color,
                      }}
                    ></div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-secondary text-sm">No spending data available</p>
            )}
          </div>
        </div>

        {/* Recent Transactions */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-primary">
              Recent Transactions
            </h3>
            <a href="/transactions" className="text-sm text-accent hover:underline">
              View all
            </a>
          </div>
          <div className="space-y-3">
            {loading ? (
              <div className="card text-center py-8">
                <p className="text-secondary">Loading transactions...</p>
              </div>
            ) : error ? (
              <div className="card text-center py-8">
                <p className="text-error">{error}</p>
              </div>
            ) : recentTransactions.length > 0 ? (
              recentTransactions.map((transaction) => (
                <TransactionCard key={transaction.id} transaction={transaction} />
              ))
            ) : (
              <div className="card text-center py-8">
                <p className="text-secondary">No transactions found</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <FloatingActionButton />
    </div>
  );
}
