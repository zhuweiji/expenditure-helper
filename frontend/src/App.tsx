import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';
import { Layout } from './components/layout/Layout';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { Home } from './pages/Home';
import { Transactions } from './pages/Transactions';
import { Insights } from './pages/Insights';
import { Profile } from './pages/Profile';
import { UploadStage } from './pages/upload/UploadStage';
import { ProcessingStage } from './pages/upload/ProcessingStage';
import { PreviewStage } from './pages/upload/PreviewStage';
import { ConfirmationStage } from './pages/upload/ConfirmationStage';
import { SuccessStage } from './pages/upload/SuccessStage';

// Simple authentication check
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Auth Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Home />} />
            <Route path="transactions" element={<Transactions />} />
            <Route path="insights" element={<Insights />} />
            <Route path="profile" element={<Profile />} />
            {/* Upload flow routes */}
            <Route path="upload" element={<UploadStage />} />
            <Route path="upload/processing" element={<ProcessingStage />} />
            <Route path="upload/preview" element={<PreviewStage />} />
            <Route path="upload/confirmation" element={<ConfirmationStage />} />
            <Route path="upload/success" element={<SuccessStage />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
