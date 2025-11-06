import { Menu, Bell } from 'lucide-react';

interface HeaderProps {
  title: string;
  onMenuClick?: () => void;
}

export function Header({ title, onMenuClick }: HeaderProps) {
  return (
    <header className="bg-card/80 backdrop-blur-md border-b border-secondary/10 sticky top-0 z-40">
      <div className="flex items-center justify-between h-16 px-4 md:px-6">
        <div className="flex items-center">
          {onMenuClick && (
            <button
              onClick={onMenuClick}
              className="mr-4 md:hidden text-secondary hover:text-primary"
            >
              <Menu className="h-6 w-6" />
            </button>
          )}
          <h2 className="text-xl font-semibold text-primary">{title}</h2>
        </div>

        <div className="flex items-center space-x-4">
          <button className="relative text-secondary hover:text-primary transition-colors">
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-accent rounded-full"></span>
          </button>
        </div>
      </div>
    </header>
  );
}
