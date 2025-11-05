import { NavLink } from 'react-router-dom';
import { Home, ArrowLeftRight, TrendingUp, User, Upload } from 'lucide-react';

const navigation = [
  { name: 'Home', to: '/', icon: Home },
  { name: 'Transactions', to: '/transactions', icon: ArrowLeftRight },
  { name: 'Insights', to: '/insights', icon: TrendingUp },
  { name: 'Profile', to: '/profile', icon: User },
];

export function Sidebar() {
  return (
    <aside className="hidden md:flex md:flex-col md:w-64 md:fixed md:inset-y-0 bg-card border-r border-secondary/10">
      <div className="flex flex-col flex-1 min-h-0">
        {/* Logo */}
        <div className="flex items-center h-16 flex-shrink-0 px-6 border-b border-secondary/10">
          <h1 className="text-xl font-bold text-accent">Expenditure Helper</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? 'bg-accent text-background'
                    : 'text-secondary hover:bg-background hover:text-primary'
                }`
              }
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>

        {/* Upload Button */}
        <div className="flex-shrink-0 p-4 border-t border-secondary/10">
          <NavLink
            to="/upload"
            className="flex items-center justify-center w-full px-4 py-3 text-sm font-semibold text-background bg-accent rounded-lg hover:bg-accent/90 transition-colors"
          >
            <Upload className="mr-2 h-5 w-5" />
            Upload Statement
          </NavLink>
        </div>
      </div>
    </aside>
  );
}
