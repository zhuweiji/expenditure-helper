import { Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function FloatingActionButton() {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate('/upload')}
      className="fixed bottom-20 right-6 md:bottom-6 md:right-6 h-14 w-14 bg-accent text-background rounded-full shadow-lg hover:bg-accent/90 transition-all hover:scale-110 flex items-center justify-center z-40"
      aria-label="Upload statement"
    >
      <Plus className="h-6 w-6" />
    </button>
  );
}
