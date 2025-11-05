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
import {
  mockCategorySpending,
  mockMonthlySpending,
} from '../lib/mockData';

export function Insights() {
  return (
    <div className="min-h-screen bg-background">
      <Header title="Insights" />

      <div className="max-w-7xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        {/* Spending Overview */}
        <div className="card">
          <h3 className="text-lg font-semibold text-primary mb-6">
            Monthly Spending Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockMonthlySpending}>
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
                  data={mockCategorySpending}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ category, percentage }) =>
                    `${category} ${percentage}%`
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="amount"
                >
                  {mockCategorySpending.map((entry, index) => (
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
              <BarChart data={mockCategorySpending}>
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
                  {mockCategorySpending.map((entry, index) => (
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
              {mockCategorySpending[0].category}
            </p>
            <p className="text-sm text-accent mt-1">
              ${mockCategorySpending[0].amount.toFixed(2)}
            </p>
          </div>

          <div className="card">
            <h4 className="text-sm font-medium text-secondary mb-2">
              Average Transaction
            </h4>
            <p className="text-xl font-bold text-primary">$67.52</p>
            <p className="text-sm text-success mt-1">↓ 12% from last month</p>
          </div>

          <div className="card">
            <h4 className="text-sm font-medium text-secondary mb-2">
              Budget Status
            </h4>
            <p className="text-xl font-bold text-primary">68%</p>
            <p className="text-sm text-secondary mt-1">$680 of $1000 used</p>
          </div>
        </div>
      </div>

      <FloatingActionButton />
    </div>
  );
}
