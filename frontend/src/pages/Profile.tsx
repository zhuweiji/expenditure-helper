import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { User, Mail, Globe, Calendar, LogOut, Settings } from 'lucide-react';
import { mockUserProfile } from '../lib/mockData';

export function Profile() {
  const navigate = useNavigate();
  const [profile] = useState(mockUserProfile);

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-background">
      <Header title="Profile" />

      <div className="max-w-3xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
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
                  Joined {new Date(profile.joinedDate).toLocaleDateString()}
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
              <input
                type="text"
                defaultValue={profile.name}
                className="input w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-primary mb-2">
                Email
              </label>
              <input
                type="email"
                defaultValue={profile.email}
                className="input w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-primary mb-2">
                Currency
              </label>
              <select className="input w-full">
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="GBP">GBP - British Pound</option>
                <option value="SGD">SGD - Singapore Dollar</option>
              </select>
            </div>
            <button className="btn-primary">Save Changes</button>
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
