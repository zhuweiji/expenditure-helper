import { Header } from '../components/layout/Header';
import { TransactionCard } from '../components/TransactionCard';
import { FloatingActionButton } from '../components/FloatingActionButton';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { mockTransactions, mockCategorySpending } from '../lib/mockData';

export function Home() {
  const recentTransactions = mockTransactions.slice(0, 5);
  const totalIncome = mockTransactions
    .filter((t) => t.type === 'credit')
    .reduce((sum, t) => sum + t.amount, 0);
  const totalExpenses = Math.abs(
    mockTransactions
      .filter((t) => t.type === 'debit')
      .reduce((sum, t) => sum + t.amount, 0)
  );
  const netBalance = totalIncome - totalExpenses;

  return (
    <div className="min-h-screen bg-background">
      <Header title="Dashboard" />

      <div className="max-w-7xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        {/* Balance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary mb-1">Total Balance</p>
                <p className="text-2xl font-bold text-primary">
                  ${netBalance.toFixed(2)}
                </p>
              </div>
              <div className="p-3 bg-accent/10 rounded-full">
                <DollarSign className="h-6 w-6 text-accent" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary mb-1">Income</p>
                <p className="text-2xl font-bold text-success">
                  ${totalIncome.toFixed(2)}
                </p>
              </div>
              <div className="p-3 bg-success/10 rounded-full">
                <TrendingUp className="h-6 w-6 text-success" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary mb-1">Expenses</p>
                <p className="text-2xl font-bold text-error">
                  ${totalExpenses.toFixed(2)}
                </p>
              </div>
              <div className="p-3 bg-error/10 rounded-full">
                <TrendingDown className="h-6 w-6 text-error" />
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
            {mockCategorySpending.slice(0, 4).map((category) => (
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
            ))}
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
            {recentTransactions.map((transaction) => (
              <TransactionCard key={transaction.id} transaction={transaction} />
            ))}
          </div>
        </div>
      </div>

      <FloatingActionButton />
    </div>
  );
}
