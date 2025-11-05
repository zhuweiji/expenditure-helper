import { NavLink } from 'react-router-dom';
import { Home, ArrowLeftRight, TrendingUp, User } from 'lucide-react';

const navigation = [
  { name: 'Home', to: '/', icon: Home },
  { name: 'Transactions', to: '/transactions', icon: ArrowLeftRight },
  { name: 'Insights', to: '/insights', icon: TrendingUp },
  { name: 'Profile', to: '/profile', icon: User },
];

export function BottomNav() {
  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 bg-card border-t border-secondary/10 z-50">
      <div className="flex justify-around items-center h-16">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.to}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center flex-1 h-full transition-colors ${
                isActive ? 'text-accent' : 'text-secondary'
              }`
            }
          >
            <item.icon className="h-6 w-6" />
            <span className="text-xs mt-1">{item.name}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
