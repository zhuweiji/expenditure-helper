import { useEffect, useState, useMemo, useRef } from 'react';
import { Header } from '../components/layout/Header';
import { TransactionCard } from '../components/TransactionCard';
import { FloatingActionButton } from '../components/FloatingActionButton';
import { Filter, Search, ArrowUpDown, ChevronLeft, ChevronRight } from 'lucide-react';
import { mockTransactions } from '../lib/mockData';
import { apiClient, getCurrentUserId, shouldUseMockData } from '../lib/api';

export function Transactions() {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'date' | 'amount'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 1000;
  const searchTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Debounce search query - update debouncedSearchQuery 300ms after user stops typing
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    searchTimeoutRef.current = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
      setCurrentPage(1);
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery]);

  const getTransactionAmount = (transaction: any) => {
    if (!transaction.detailed_entries || transaction.detailed_entries.length === 0) {
      return 0;
    }
    
    // Sum all debits
    const debitSum = transaction.detailed_entries
      .filter((e: any) => e.entry_type === 'debit')
      .reduce((sum: number, e: any) => sum + Math.abs(e.amount), 0);
    
    // Sum all credits as fallback
    const creditSum = transaction.detailed_entries
      .filter((e: any) => e.entry_type === 'credit')
      .reduce((sum: number, e: any) => sum + Math.abs(e.amount), 0);
    
    return debitSum > 0 ? debitSum : creditSum;
  };

  const categories = useMemo(() => ['all', ...new Set(transactions.flatMap((t) => 
    t.entries.map((e: any) => e.account_name)
  ))], [transactions]);

  const filteredTransactions = useMemo(() => 
    transactions
      .filter((transaction) => {
        const matchesSearch = transaction.description.toLowerCase().includes(debouncedSearchQuery.toLowerCase());
        const matchesCategory =
          selectedCategory === 'all' || 
          transaction.entries.some((e: any) => e.account_name === selectedCategory);
        return matchesSearch && matchesCategory;
      })
      .sort((a, b) => {
        let compareValue = 0;
        
        if (sortBy === 'date') {
          compareValue = new Date(a.transaction_date).getTime() - new Date(b.transaction_date).getTime();
        } else if (sortBy === 'amount') {
          const aAmount = getTransactionAmount(a);
          const bAmount = getTransactionAmount(b);
          compareValue = aAmount - bAmount;
        }
        
        return sortOrder === 'asc' ? compareValue : -compareValue;
      }),
    [transactions, debouncedSearchQuery, selectedCategory, sortBy, sortOrder]
  );

  useEffect(() => {
    const userId = getCurrentUserId();
    const useMockData = shouldUseMockData(userId);

    if (!userId) {
      // No user set - initialize with empty state
      console.warn('No user id found in localStorage. Set `userId` in localStorage to fetch transactions.');
      setTransactions([]);
      return;
    }

    if (useMockData) {
      // Mock data is enabled for this user
      console.info('Mock data enabled for user ID:', userId);
      setTransactions(mockTransactions);
      return;
    }

    let mounted = true;

    async function fetchTransactions() {
      setLoading(true);
      setError(null);
      try {
        // Convert date strings to ISO format for API
        const params: any = {
          page: currentPage,
          pageSize,
        };
        if (startDate) params.startDate = new Date(startDate).toISOString();
        if (endDate) params.endDate = new Date(endDate).toISOString();

        const response = (await apiClient.getTransactions(userId as number, params)) as any;

        console.log(response);

        // Handle paginated response
        const data = response.transactions || response;
        const isPaginated = response.transactions !== undefined;

        // Map backend transaction shape to match Transaction interface
        const mapped = (data || []).map((tx: any) => ({
          id: tx.id,
          description: tx.description,
          transaction_date: tx.transaction_date,
          reference: tx.reference,
          entries: tx.entries || [],
          detailed_entries: tx.detailed_entries || [],
        }));

        if (mounted) {
          setTransactions(mapped.length ? mapped : []);
          if (isPaginated) {
            setTotalCount(response.total_count);
            setTotalPages(response.total_pages);
          }
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
  }, [currentPage, startDate, endDate]);

  return (
    <div className="min-h-screen bg-background">
      <Header title="Transactions" />

      <div className="max-w-7xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        {/* Date Range Filter */}
        <div className="card p-4">
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1">
              <label className="text-sm text-secondary mb-2 block">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => {
                  setStartDate(e.target.value);
                  setCurrentPage(1);
                }}
                className="input w-full"
              />
            </div>
            <div className="flex-1">
              <label className="text-sm text-secondary mb-2 block">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => {
                  setEndDate(e.target.value);
                  setCurrentPage(1);
                }}
                className="input w-full"
              />
            </div>
            <button
              onClick={() => {
                setStartDate('');
                setEndDate('');
                setCurrentPage(1);
              }}
              className="input px-4 py-2 hover:bg-opacity-80 transition-all whitespace-nowrap"
            >
              Clear Dates
            </button>
          </div>
        </div>

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

          <div className="relative">
            <ArrowUpDown className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'amount')}
              className="input pl-12 pr-4 appearance-none cursor-pointer"
            >
              <option value="date">Sort by Date</option>
              <option value="amount">Sort by Amount</option>
            </select>
          </div>

          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="input px-4 py-2 hover:bg-opacity-80 transition-all"
            title={`Currently sorted ${sortOrder === 'asc' ? 'ascending' : 'descending'}`}
          >
            {sortOrder === 'asc' ? '↑ ASC' : '↓ DESC'}
          </button>
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
              {filteredTransactions.filter((t) => t.detailed_entries?.some((e: any) => e.entry_type === 'credit')).length}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-secondary mb-1">Expenses</p>
            <p className="text-xl font-bold text-error">
              {filteredTransactions.filter((t) => !t.detailed_entries?.some((e: any) => e.entry_type === 'credit')).length}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-secondary mb-1">This Month</p>
            <p className="text-xl font-bold text-primary">
              {
                filteredTransactions.filter((t) =>
                  t.transaction_date.startsWith('2025-11')
                ).length
              }
            </p>
          </div>
        </div>

        {/* Transactions List */}
        <div className="space-y-3">
          {loading ? (
            <div className="card text-center py-12">
              <p className="text-secondary">Loading transactions...</p>
            </div>
          ) : error ? (
            <div className="card text-center py-12">
              <p className="text-error">{error}</p>
            </div>
          ) : filteredTransactions.length > 0 ? (
            filteredTransactions.map((transaction) => (
              <TransactionCard key={transaction.id} transaction={transaction} />
            ))
          ) : (
            <div className="card text-center py-12">
              <p className="text-secondary">No transactions found</p>
            </div>
          )}
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="card p-4">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="text-sm text-secondary">
                Page <span className="font-semibold text-primary">{currentPage}</span> of{' '}
                <span className="font-semibold text-primary">{totalPages}</span> (
                <span className="font-semibold text-primary">{totalCount}</span> total)
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="input px-4 py-2 hover:bg-opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <ChevronLeft size={18} />
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="input px-4 py-2 hover:bg-opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  Next
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <FloatingActionButton />
    </div>
  );
}
