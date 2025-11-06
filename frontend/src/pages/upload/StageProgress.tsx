import { ArrowLeft } from 'lucide-react';
import type { FlowStage } from '../../hooks/useUploadFlow';

interface StageProgressProps {
  currentStage: FlowStage;
  onStartOver: () => void;
}

export function StageProgress({ currentStage, onStartOver }: StageProgressProps) {
  const stages: { stage: FlowStage; label: string }[] = [
    { stage: 'upload', label: 'Upload' },
    { stage: 'processing', label: 'Processing' },
    { stage: 'preview', label: 'Review' },
    { stage: 'confirmation', label: 'Confirm' },
    { stage: 'creating', label: 'Creating' },
    { stage: 'success', label: 'Done' },
  ];

  const stageOrder: FlowStage[] = [
    'upload',
    'processing',
    'preview',
    'confirmation',
    'creating',
    'success',
  ];
  const currentIndex = stageOrder.indexOf(currentStage);

  return (
    <div className="space-y-6">
      {currentStage !== 'upload' && currentStage !== 'success' && (
        <button
          onClick={onStartOver}
          className="flex items-center text-secondary hover:text-primary transition-colors"
        >
          <ArrowLeft className="mr-2 h-5 w-5" />
          Start Over
        </button>
      )}

      {currentStage !== 'upload' && (
        <div className="flex justify-between items-center mb-8">
          {stages.map((s, idx) => (
            <div key={s.stage} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm ${
                  idx < currentIndex
                    ? 'bg-success text-white'
                    : idx === currentIndex
                      ? 'bg-accent text-white'
                      : 'bg-secondary/20 text-secondary'
                }`}
              >
                {idx < currentIndex ? '✓' : idx + 1}
              </div>
              <p
                className={`ml-2 text-sm font-medium ${
                  idx <= currentIndex ? 'text-primary' : 'text-secondary'
                }`}
              >
                {s.label}
              </p>
              {idx < stages.length - 1 && (
                <div
                  className={`w-12 h-0.5 ml-4 ${
                    idx < currentIndex ? 'bg-success' : 'bg-secondary/20'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
