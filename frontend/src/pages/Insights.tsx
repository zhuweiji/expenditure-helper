import { useEffect, useState, useMemo } from 'react';
import { Header } from '../components/layout/Header';
import { FloatingActionButton } from '../components/FloatingActionButton';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';
import { apiClient, getCurrentUserId, shouldUseMockData } from '../lib/api';

interface CategorySpending {
  category: string;
  amount: number;
  percentage: number;
  color: string;
  transaction_count?: number;
  average_transaction?: number;
}

interface MonthlySpending {
  month: string;
  amount: number;
  transaction_count?: number;
  average_transaction?: number;
}

interface SummaryMetrics {
  total_spending: number;
  average_spending_per_transaction: number;
  highest_spending_category: {
    category: string;
    amount: number;
    percentage: number;
  };
  transaction_count: number;
}

const CATEGORY_COLORS: Record<string, string> = {
  'Groceries': '#EAFD60',
  'Dining': '#27C46B',
  'Transportation': '#60A5FA',
  'Shopping': '#F472B6',
  'Utilities': '#A78BFA',
  'Health': '#FB923C',
  'Entertainment': '#EC4899',
  'Other': '#9BA0A5',
};

function getColorForCategory(category: string): string {
  return CATEGORY_COLORS[category] || '#9BA0A5';
}

export function Insights() {
  const [categorySpending, setCategorySpending] = useState<CategorySpending[]>([]);
  const [monthlySpending, setMonthlySpending] = useState<MonthlySpending[]>([]);
  const [summaryMetrics, setSummaryMetrics] = useState<SummaryMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const highestSpendingCategory = useMemo(
    () => summaryMetrics?.highest_spending_category || null,
    [summaryMetrics]
  );

  const totalSpending = useMemo(
    () => summaryMetrics?.total_spending || 0,
    [summaryMetrics]
  );

  const averageTransaction = useMemo(
    () => summaryMetrics?.average_spending_per_transaction || 0,
    [summaryMetrics]
  );

  useEffect(() => {
    const userId = getCurrentUserId();
    const useMockData = shouldUseMockData(userId);

    if (!userId) {
      console.warn('No user id found in localStorage. Set `userId` in localStorage to fetch transactions.');
      setCategorySpending([]);
      setMonthlySpending([]);
      setSummaryMetrics(null);
      return;
    }

    if (useMockData) {
      console.info('Mock data enabled for Insights');
      processMockTransactions();
      return;
    }

    let mounted = true;

    async function fetchAnalytics() {
      setLoading(true);
      setError(null);
      try {
        // Fetch insights summary and top categories
        const insightsResponse = (await apiClient.getInsights(userId as number)) as any;
        
        // Fetch spending by category
        const categoryResponse = (await apiClient.getSpendingByCategory(userId as number)) as any;
        
        // Fetch monthly spending trend
        const monthlyResponse = (await apiClient.getMonthlySpending(userId as number, {
          months: 12,
        })) as any;

        if (mounted) {
          // Process insights summary
          if (insightsResponse?.summary) {
            setSummaryMetrics(insightsResponse.summary);
          }

          // Process category spending with colors
          if (categoryResponse?.categories) {
            const categoryData: CategorySpending[] = categoryResponse.categories.map(
              (cat: any) => ({
                category: cat.category,
                amount: cat.amount,
                percentage: cat.percentage,
                transaction_count: cat.transaction_count,
                average_transaction: cat.average_transaction,
                color: getColorForCategory(cat.category),
              })
            );
            setCategorySpending(categoryData);
          }

          // Process monthly spending
          if (monthlyResponse?.months) {
            const monthlyData: MonthlySpending[] = monthlyResponse.months.map(
              (month: any) => ({
                month: month.month,
                amount: month.amount,
                transaction_count: month.transaction_count,
                average_transaction: month.average_transaction,
              })
            );
            setMonthlySpending(monthlyData);
          }
        }
      } catch (err: any) {
        console.error('Failed to fetch analytics', err);
        if (mounted) setError(err?.message || 'Failed to fetch analytics data');
      } finally {
        if (mounted) setLoading(false);
      }
    }

    fetchAnalytics();

    return () => {
      mounted = false;
    };
  }, []);

  function processMockTransactions() {
    // Mock data processing for demo/testing purposes
    // In production, this would use the actual API endpoints like regular users
    try {
      // For now, we'll simulate the API responses from mock data
      const mockResponse = {
        summary: {
          total_spending: 1500.00,
          average_spending_per_transaction: 75.00,
          highest_spending_category: {
            category: 'Groceries',
            amount: 450.00,
            percentage: 30,
          },
          transaction_count: 20,
        },
        top_categories: [
          { category: 'Groceries', amount: 450.00, percentage: 30 },
          { category: 'Dining', amount: 375.00, percentage: 25 },
          { category: 'Transportation', amount: 300.00, percentage: 20 },
        ],
        monthly_trend: [
          { month: '2025-11', amount: 1500.00 },
        ],
      };

      if (mockResponse?.summary) {
        setSummaryMetrics(mockResponse.summary);
      }

      if (mockResponse?.top_categories) {
        const categoryData: CategorySpending[] = mockResponse.top_categories.map(
          (cat: any) => ({
            category: cat.category,
            amount: cat.amount,
            percentage: cat.percentage,
            transaction_count: cat.transaction_count,
            average_transaction: cat.average_transaction,
            color: getColorForCategory(cat.category),
          })
        );
        setCategorySpending(categoryData);
      }

      if (mockResponse?.monthly_trend) {
        const monthlyData: MonthlySpending[] = mockResponse.monthly_trend.map(
          (month: any) => ({
            month: month.month,
            amount: month.amount,
            transaction_count: month.transaction_count || 0,
            average_transaction: month.average_transaction || 0,
          })
        );
        setMonthlySpending(monthlyData);
      }
    } catch (err) {
      console.error('Error processing mock data', err);
      setError('Failed to process mock data');
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Header title="Insights" />

      <div className="max-w-7xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        {loading && (
          <div className="card text-center py-12">
            <p className="text-secondary">Loading insights...</p>
          </div>
        )}

        {error && (
          <div className="card text-center py-12">
            <p className="text-error">{error}</p>
          </div>
        )}

        {!loading && !error && categorySpending.length === 0 && (
          <div className="card text-center py-12">
            <p className="text-secondary">No transaction data available</p>
          </div>
        )}

        {!loading && !error && categorySpending.length > 0 && (
          <>
            {/* Spending Overview */}
            <div className="card">
              <h3 className="text-lg font-semibold text-primary mb-6">
                Monthly Spending Trend
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={monthlySpending}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2A2C2E" />
                  <XAxis dataKey="month" stroke="#9BA0A5" />
                  <YAxis stroke="#9BA0A5" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1A1C1E',
                      border: '1px solid #2A2C2E',
                      borderRadius: '8px',
                      color: '#FFFFFF',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="amount"
                    stroke="#EAFD60"
                    strokeWidth={2}
                    dot={{ fill: '#EAFD60', r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Category Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Pie Chart */}
              <div className="card">
                <h3 className="text-lg font-semibold text-primary mb-6">
                  Spending by Category
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categorySpending as any}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ category, percentage }: any) =>
                        `${category} ${percentage}%`
                      }
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="amount"
                    >
                      {categorySpending.map((entry: CategorySpending, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1A1C1E',
                        border: '1px solid #2A2C2E',
                        borderRadius: '8px',
                        color: '#FFFFFF',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Bar Chart */}
              <div className="card">
                <h3 className="text-lg font-semibold text-primary mb-6">
                  Category Amounts
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={categorySpending as any}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2A2C2E" />
                    <XAxis dataKey="category" stroke="#9BA0A5" />
                    <YAxis stroke="#9BA0A5" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1A1C1E',
                        border: '1px solid #2A2C2E',
                        borderRadius: '8px',
                        color: '#FFFFFF',
                      }}
                    />
                    <Bar dataKey="amount" radius={[8, 8, 0, 0]}>
                      {categorySpending.map((entry: CategorySpending, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Insights Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="card">
                <h4 className="text-sm font-medium text-secondary mb-2">
                  Highest Spending
                </h4>
                <p className="text-xl font-bold text-primary">
                  {highestSpendingCategory?.category || 'N/A'}
                </p>
                <p className="text-sm text-accent mt-1">
                  ${highestSpendingCategory?.amount.toFixed(2) || '0.00'}
                </p>
              </div>

              <div className="card">
                <h4 className="text-sm font-medium text-secondary mb-2">
                  Average Spending
                </h4>
                <p className="text-xl font-bold text-primary">${averageTransaction.toFixed(2)}</p>
                <p className="text-sm text-secondary mt-1">Per category</p>
              </div>

              <div className="card">
                <h4 className="text-sm font-medium text-secondary mb-2">
                  Total Spending
                </h4>
                <p className="text-xl font-bold text-primary">${totalSpending.toFixed(2)}</p>
                <p className="text-sm text-secondary mt-1">{categorySpending.length} categories</p>
              </div>
            </div>
          </>
        )}
      </div>

      <FloatingActionButton />
    </div>
  );
}
