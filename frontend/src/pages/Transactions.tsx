import { useState } from 'react';
import { Header } from '../components/layout/Header';
import { TransactionCard } from '../components/TransactionCard';
import { FloatingActionButton } from '../components/FloatingActionButton';
import { Filter, Search } from 'lucide-react';
import { mockTransactions } from '../lib/mockData';

export function Transactions() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = ['all', ...new Set(mockTransactions.map((t) => t.category))];

  const filteredTransactions = mockTransactions.filter((transaction) => {
    const matchesSearch =
      transaction.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      transaction.merchant?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory =
      selectedCategory === 'all' || transaction.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-background">
      <Header title="Transactions" />

      <div className="max-w-7xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search transactions..."
              className="input w-full pl-12"
            />
          </div>

          <div className="relative">
            <Filter className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input pl-12 pr-4 appearance-none cursor-pointer"
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Transaction Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card">
            <p className="text-sm text-secondary mb-1">Total</p>
            <p className="text-xl font-bold text-primary">
              {filteredTransactions.length}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-secondary mb-1">Income</p>
            <p className="text-xl font-bold text-success">
              {filteredTransactions.filter((t) => t.type === 'credit').length}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-secondary mb-1">Expenses</p>
            <p className="text-xl font-bold text-error">
              {filteredTransactions.filter((t) => t.type === 'debit').length}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-secondary mb-1">This Month</p>
            <p className="text-xl font-bold text-primary">
              {
                filteredTransactions.filter((t) =>
                  t.date.startsWith('2025-11')
                ).length
              }
            </p>
          </div>
        </div>

        {/* Transactions List */}
        <div className="space-y-3">
          {filteredTransactions.length > 0 ? (
            filteredTransactions.map((transaction) => (
              <TransactionCard key={transaction.id} transaction={transaction} />
            ))
          ) : (
            <div className="card text-center py-12">
              <p className="text-secondary">No transactions found</p>
            </div>
          )}
        </div>
      </div>

      <FloatingActionButton />
    </div>
  );
}
