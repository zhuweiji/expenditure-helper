import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { User, Globe, Calendar, LogOut, Settings, Trash2 } from 'lucide-react';
import { mockUserProfile } from '../lib/mockData';
import { apiClient, getCurrentUserId, shouldUseMockData } from '../lib/api';

interface UserProfile {
  id?: number;
  full_name?: string;
  email?: string;
  username?: string;
  created_at?: string;
  name?: string;
  joinedDate?: string;
  timezone?: string;
  avatar?: string | null;
  currency?: string;
}

export function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [showClearConfirmation, setShowClearConfirmation] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [editedFields, setEditedFields] = useState<{
    email?: string;
    timezone?: string;
    currency?: string;
  }>({});

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const userId = getCurrentUserId();
        if (!userId) {
          navigate('/login');
          return;
        }

        // Use mock data if enabled
        if (shouldUseMockData(userId)) {
          setProfile(mockUserProfile as UserProfile);
        } else {
          // Fetch real user data from API
          const userData = (await apiClient.getProfile(userId)) as Record<string, unknown>;
          setProfile({
            id: userData.id as number | undefined,
            full_name: userData.full_name as string | undefined,
            email: userData.email as string | undefined,
            username: userData.username as string | undefined,
            created_at: userData.created_at as string | undefined,
            // Map API fields to UI fields for compatibility
            name: (userData.full_name as string) || (userData.username as string) || '',
            joinedDate: (userData.created_at as string) || new Date().toISOString(),
            timezone: (userData.timezone as string) || 'UTC',
            currency: (userData.currency as string) || 'USD',
          });
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
        setError('Failed to load profile data');
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('userId');
    navigate('/login');
  };

  const handleClearTransactions = async () => {
    try {
      const userId = getCurrentUserId();
      if (!userId) return;

      setIsClearing(true);
      await apiClient.clearAllTransactions(userId);
      setShowClearConfirmation(false);
      setError(null);
      // Show success message
      alert('All transactions have been cleared successfully.');
    } catch (err) {
      console.error('Failed to clear transactions:', err);
      setError('Failed to clear transactions. Please try again.');
    } finally {
      setIsClearing(false);
    }
  };

  const handleSaveChanges = async () => {
    try {
      const userId = getCurrentUserId();
      if (!userId || !profile) return;

      setIsSaving(true);
      setError(null);
      setSuccess(null);

      // Prepare the update payload with edited fields
      const updateData: Record<string, any> = {};
      if (editedFields.email !== undefined) {
        updateData.email = editedFields.email;
      }
      if (editedFields.timezone !== undefined) {
        updateData.timezone = editedFields.timezone;
      }
      if (editedFields.currency !== undefined) {
        updateData.currency = editedFields.currency;
      }

      // Only call API if there are changes
      if (Object.keys(updateData).length > 0) {
        await apiClient.updateProfile(userId, updateData);
        
        // Update local profile state
        setProfile({
          ...profile,
          email: editedFields.email ?? profile.email,
          timezone: editedFields.timezone ?? profile.timezone,
          currency: editedFields.currency ?? profile.currency,
        });

        // Clear edited fields and show success
        setEditedFields({});
        setSuccess('Profile updated successfully!');
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Failed to save profile:', err);
      setError('Failed to save profile changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleFieldChange = (field: string, value: string) => {
    setEditedFields(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Header title="Profile" />
        <div className="max-w-3xl mx-auto px-4 py-6 md:px-6 md:py-8 flex items-center justify-center">
          <p className="text-secondary">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-background">
        <Header title="Profile" />
        <div className="max-w-3xl mx-auto px-4 py-6 md:px-6 md:py-8 flex items-center justify-center">
          <p className="text-error">{error || 'Failed to load profile'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header title="Profile" />

      <div className="max-w-3xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        {error && (
          <div className="bg-error/10 border border-error/30 text-error px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-accent/10 border border-accent/30 text-accent px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {/* Profile Header */}
        <div className="card">
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-6">
            <div className="h-24 w-24 rounded-full bg-accent/10 flex items-center justify-center">
              <User className="h-12 w-12 text-accent" />
            </div>
            <div className="flex-1 text-center md:text-left">
              <h2 className="text-2xl font-bold text-primary">{profile.name}</h2>
              <p className="text-secondary mt-1">{profile.email}</p>
              <div className="flex flex-wrap justify-center md:justify-start gap-4 mt-4">
                <div className="flex items-center text-sm text-secondary">
                  <Calendar className="h-4 w-4 mr-2" />
                  Joined {profile.joinedDate ? new Date(profile.joinedDate).toLocaleDateString() : 'N/A'}
                </div>
                <div className="flex items-center text-sm text-secondary">
                  <Globe className="h-4 w-4 mr-2" />
                  {profile.timezone}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Account Settings */}
        <div className="card">
          <h3 className="text-lg font-semibold text-primary mb-4">
            Account Settings
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-primary mb-2">
                Name
              </label>
              <div className="input w-full bg-secondary/10 cursor-not-allowed flex items-center">
                <span className="text-primary">{profile.name || ''}</span>
              </div>
              <p className="text-xs text-secondary mt-1">Name cannot be changed</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-primary mb-2">
                Email
              </label>
              <input
                type="email"
                defaultValue={profile.email || ''}
                onChange={(e) => handleFieldChange('email', e.target.value)}
                className="input w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-primary mb-2">
                Timezone
              </label>
              <select 
                className="input w-full" 
                value={editedFields.timezone !== undefined ? editedFields.timezone : (profile.timezone || 'UTC')}
                onChange={(e) => handleFieldChange('timezone', e.target.value)}
              >
                <option value="UTC">UTC</option>
                <option value="EST">EST - Eastern Standard Time</option>
                <option value="CST">CST - Central Standard Time</option>
                <option value="MST">MST - Mountain Standard Time</option>
                <option value="PST">PST - Pacific Standard Time</option>
                <option value="GMT">GMT - Greenwich Mean Time</option>
                <option value="CET">CET - Central European Time</option>
                <option value="IST">IST - Indian Standard Time</option>
                <option value="SGT">SGT - Singapore Time</option>
                <option value="JST">JST - Japan Standard Time</option>
                <option value="AEST">AEST - Australian Eastern Standard Time</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-primary mb-2">
                Currency
              </label>
              <select 
                className="input w-full" 
                value={editedFields.currency !== undefined ? editedFields.currency : (profile.currency || 'USD')}
                onChange={(e) => handleFieldChange('currency', e.target.value)}
              >
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="GBP">GBP - British Pound</option>
                <option value="SGD">SGD - Singapore Dollar</option>
              </select>
            </div>
            <button 
              onClick={handleSaveChanges}
              disabled={isSaving}
              className="btn-primary disabled:opacity-50"
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>

        {/* Preferences */}
        <div className="card">
          <h3 className="text-lg font-semibold text-primary mb-4">
            Preferences
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-primary">Email Notifications</p>
                <p className="text-sm text-secondary">
                  Receive updates about your transactions
                </p>
              </div>
              <label className="relative inline-block w-12 h-6">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-12 h-6 bg-secondary/30 rounded-full peer peer-checked:bg-accent transition-colors"></div>
                <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-6"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-primary">Monthly Reports</p>
                <p className="text-sm text-secondary">
                  Get monthly spending summaries
                </p>
              </div>
              <label className="relative inline-block w-12 h-6">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-12 h-6 bg-secondary/30 rounded-full peer peer-checked:bg-accent transition-colors"></div>
                <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-6"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          <button className="btn-secondary w-full flex items-center justify-center">
            <Settings className="mr-2 h-5 w-5" />
            Advanced Settings
          </button>
          
          {/* Clear Transactions Button */}
          {!showClearConfirmation && (
            <button
              onClick={() => setShowClearConfirmation(true)}
              className="w-full flex items-center justify-center px-6 py-3 text-error border border-error/30 rounded-lg hover:bg-error/10 transition-colors"
            >
              <Trash2 className="mr-2 h-5 w-5" />
              Clear All Transactions
            </button>
          )}

          {/* Clear Transactions Confirmation */}
          {showClearConfirmation && (
            <div className="bg-error/10 border border-error/30 rounded-lg p-4 space-y-3">
              <div>
                <h4 className="font-semibold text-error mb-2">Clear All Transactions?</h4>
                <p className="text-sm text-secondary mb-2">
                  This action will permanently delete all your transactions and entries. This cannot be undone.
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowClearConfirmation(false)}
                  disabled={isClearing}
                  className="flex-1 px-4 py-2 border border-secondary/30 rounded-lg hover:bg-secondary/10 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleClearTransactions}
                  disabled={isClearing}
                  className="flex-1 px-4 py-2 bg-error text-white rounded-lg hover:bg-error/90 transition-colors disabled:opacity-50"
                >
                  {isClearing ? 'Clearing...' : 'Confirm Delete'}
                </button>
              </div>
            </div>
          )}

          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center px-6 py-3 text-error border border-error/30 rounded-lg hover:bg-error/10 transition-colors"
          >
            <LogOut className="mr-2 h-5 w-5" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
