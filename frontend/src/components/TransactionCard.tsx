import { ArrowUpRight, ArrowDownLeft, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import type { Transaction } from '../lib/types';

interface TransactionCardProps {
  transaction: Transaction;
  onClick?: () => void;
}

export function TransactionCard({ transaction, onClick }: TransactionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Calculate amount from detailed entries
  const calculateAmount = () => {
    if (!transaction.detailed_entries || transaction.detailed_entries.length === 0) {
      return 0;
    }
    
    // Sum all credits
    const creditSum = transaction.detailed_entries
      .filter(e => e.entry_type === 'credit')
      .reduce((sum, e) => sum + Math.abs(e.amount), 0);
    
    // Sum all debits
    const debitSum = transaction.detailed_entries
      .filter(e => e.entry_type === 'debit')
      .reduce((sum, e) => sum + Math.abs(e.amount), 0);
    
    // Return non-zero value (prefer debit if both exist, as it represents the transaction amount)
    return debitSum > 0 ? debitSum : creditSum;
  };
  
  const displayAmount = calculateAmount();
  
  return (
    <div className="card hover:bg-card/80 transition-colors">
      <div 
        onClick={() => {
          onClick?.();
          setIsExpanded(!isExpanded);
        }}
        className="cursor-pointer flex items-center justify-between gap-4"
      >
        <div className="flex items-center gap-1 md:gap-4 min-w-0">
          <div
            className={`p-1 md:p-3 rounded-full flex-shrink-0 ${
              transaction.detailed_entries?.some(e => e.entry_type === 'credit') ? 'bg-success/10' : 'bg-error/10'
            }`}
          >
            {transaction.detailed_entries?.some(e => e.entry_type === 'credit') ? (
              <ArrowDownLeft className="h-5 w-5 text-success" />
            ) : (
              <ArrowUpRight className="h-5 w-5 text-error" />
            )}
          </div>
          
          <div className="min-w-0">
            <p className="font-medium text-primary truncate">{transaction.description}</p>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-sm text-secondary truncate">
                {transaction.reference || 'Uncategorised'}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p
              className={`font-semibold ${
                transaction.detailed_entries?.some(e => e.entry_type === 'credit') ? 'text-success' : 'text-error'
              }`}
            >
              ${displayAmount.toFixed(2)}
            </p>
            <p className="text-sm text-secondary mt-1">
              {new Date(transaction.transaction_date).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
              })}
            </p>
          </div>
          
          {isExpanded ? (
            <ChevronUp className="h-5 w-5 text-secondary" />
          ) : (
            <ChevronDown className="h-5 w-5 text-secondary" />
          )}
        </div>
      </div>

      {isExpanded && (
        <div className="mt-4 border-t pt-4">
          <p className="font-medium text-sm text-secondary mb-2">{transaction.description}</p>
          <p className="font-medium text-sm text-secondary mb-2 pt-1">Entries</p>
          <div className="space-y-2">
            {transaction.detailed_entries.map((entry, index) => (
              <div key={index} className="flex justify-between text-sm">
                <div>
                  <span className="font-medium">{entry.account_name}</span>
                  <span className="text-secondary ml-2">({entry.entry_type})</span>
                </div>
                <span className={entry.entry_type === 'credit' ? 'text-success' : 'text-error'}>
                  ${entry.amount.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
