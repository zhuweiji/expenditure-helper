import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '../../components/layout/Header'
import { EntryPreview } from '../../components/EntryPreview'
import { StageProgress } from './StageProgress'
import { useUploadFlow } from '../../hooks/useUploadFlow'
import { apiClient, getCurrentUserId, type ApiError } from '../../lib/api'
import type { AccountsByType, PrepareEntriesRequest } from '../../lib/types'
import { AlertCircle } from 'lucide-react'

interface UserAccountsResponse {
  user_id: number
  username: string
  accounts_by_type: AccountsByType
}

export function PreviewStage () {
  const navigate = useNavigate()
  const { state, setPreview, setSelectedAccounts, clearState } = useUploadFlow()
  const [accounts, setAccounts] = useState<AccountsByType>({
    liability: [],
    expense: [],
    asset: []
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const userId = getCurrentUserId()

  // Load accounts on mount and clear stale preview data
  useEffect(() => {
    // Clear any stale preview data when entering this stage
    setPreview(null)

    const currentUserId = getCurrentUserId()

    if (currentUserId) {
      loadAccounts()
    }
  }, [])

  const loadAccounts = async () => {
    try {
      const currentUserId = getCurrentUserId()

      if (!currentUserId) {
        return
      }

      console.time('[loadAccounts] API call')
      const data = await apiClient.getAccountsByUser(currentUserId)
      console.timeEnd('[loadAccounts] API call')

      // Extract accounts_by_type from the response
      let accountsData: AccountsByType
      if (data && typeof data === 'object' && 'accounts_by_type' in data) {
        accountsData = (data as UserAccountsResponse).accounts_by_type
      } else if (Array.isArray(data)) {
        accountsData = { liability: [], expense: [], asset: [] }
      } else {
        accountsData = (data as AccountsByType)
      }

      setAccounts(accountsData)

      console.log('[loadAccounts] Accounts data loaded:', accountsData)
    } catch (err) {
      const apiError = err as ApiError
      console.error('[loadAccounts] Error:', apiError.message)
    }
  }

  if (!state.statementId) {
    return (
      <div className='min-h-screen bg-background'>
        <Header title='Upload Statement' />
        <div className='max-w-4xl mx-auto px-4 py-6 md:px-6 md:py-8'>
          <p className='text-error'>
            No statement ID found. Please start over.
          </p>
          <button
            onClick={() => {
              clearState()
              navigate('/upload')
            }}
            className='mt-4 px-4 py-2 bg-accent text-white rounded hover:bg-accent/90'
          >
            Start Over
          </button>
        </div>
      </div>
    )
  }

  const handleSelectAccounts = async (
    creditCardAccountId: number,
    defaultExpenseAccountId: number,
    bankAccountId?: number | null
  ) => {
    setIsLoading(true)
    setError('')

    try {
      if (!userId) {
        setError('Invalid state - please try uploading again')
        return
      }

      setSelectedAccounts(creditCardAccountId, defaultExpenseAccountId)

      // Get preview (dry run)
      const request: PrepareEntriesRequest = {
        statement_id: state.statementId || 0,
        user_id: userId,
        credit_card_account_id: creditCardAccountId,
        default_expense_account_id: defaultExpenseAccountId,
        bank_account_id: bankAccountId,
      }

      const previewData = await apiClient.prepareEntries(request)
      setPreview(previewData as typeof state.preview)
      console.log('previewdata', previewData)

    } catch (err) {
      const apiError = err as ApiError
      setError(apiError.message || 'Failed to preview entries')
    } finally {
      setIsLoading(false)
    }
  }

  const handleConfirmAndCreateEntries = async () => {
    if (!state.preview || state.preview.transactions.length === 0) {
      setError('No preview data available. Please select accounts again.')
      return
    }

    navigate('/upload/confirmation')
  }

  const handleStartOver = () => {
    clearState()
    navigate('/upload')
  }

  return (
    <div className='min-h-screen bg-background'>
      <Header title='Upload Statement' />

      <div className='max-w-4xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6'>
        <StageProgress currentStage='preview' onStartOver={handleStartOver} />

        {error && (
          <div className='flex items-start gap-3 p-4 bg-error/10 rounded-lg border border-error/20'>
            <AlertCircle className='w-5 h-5 text-error flex-shrink-0 mt-0.5' />
            <p className='text-sm text-error'>{error}</p>
          </div>
        )}

        <EntryPreview
          preview={
            state.preview || {
              statement_id: state.statementId || 0,
              statement_filename: '',
              transactions: [],
              total_transactions: 0,
              total_debits: 0,
              total_credits: 0,
              cc_debit_amount: 0,
              cc_credit_amount: 0,
              is_balanced: false
            }
          }
          accounts={accounts}
          onSelectAccounts={handleSelectAccounts}
          onConfirmAndCreateEntries={handleConfirmAndCreateEntries}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}
