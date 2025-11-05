import { ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import type { Transaction } from '../lib/mockData';

interface TransactionCardProps {
  transaction: Transaction;
  onClick?: () => void;
}

export function TransactionCard({ transaction, onClick }: TransactionCardProps) {
  const isCredit = transaction.type === 'credit';
  
  return (
    <div
      onClick={onClick}
      className="card hover:bg-card/80 transition-colors cursor-pointer flex items-center justify-between"
    >
      <div className="flex items-center space-x-4">
        <div
          className={`p-3 rounded-full ${
            isCredit ? 'bg-success/10' : 'bg-error/10'
          }`}
        >
          {isCredit ? (
            <ArrowDownLeft className="h-5 w-5 text-success" />
          ) : (
            <ArrowUpRight className="h-5 w-5 text-error" />
          )}
        </div>
        
        <div>
          <p className="font-medium text-primary">{transaction.description}</p>
          <div className="flex items-center space-x-2 mt-1">
            <span className="text-sm text-secondary">{transaction.category}</span>
            {transaction.merchant && (
              <>
                <span className="text-secondary">•</span>
                <span className="text-sm text-secondary">{transaction.merchant}</span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="text-right">
        <p
          className={`font-semibold ${
            isCredit ? 'text-success' : 'text-error'
          }`}
        >
          {isCredit ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
        </p>
        <p className="text-sm text-secondary mt-1">
          {new Date(transaction.date).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
          })}
        </p>
      </div>
    </div>
  );
}
