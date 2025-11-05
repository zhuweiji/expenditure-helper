# Expenditure Helper - Frontend

A modern, dark-mode-first personal finance web application built with React, TypeScript, and Vite.

## Features

- 🌙 **Dark Mode First** - Beautiful dark theme optimized for extended use
- 📱 **Fully Responsive** - Desktop sidebar + mobile bottom navigation
- 📊 **Interactive Charts** - Visualize spending patterns with Recharts
- 📤 **File Upload** - Drag & drop credit card statement uploads
- 🔐 **Authentication** - Login and signup pages with protected routes
- ⚡ **Fast Performance** - Built with Vite for lightning-fast development
- 🎨 **Tailwind CSS** - Utility-first CSS with custom design system

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router DOM** - Client-side routing
- **TanStack React Query** - Data fetching and caching
- **Recharts** - Chart visualization
- **React Dropzone** - File upload
- **Lucide React** - Icon library
- **Tailwind CSS** - Styling

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── layout/          # Layout components (Sidebar, BottomNav, Header)
│   │   ├── FloatingActionButton.tsx
│   │   ├── TransactionCard.tsx
│   │   └── UploadZone.tsx
│   ├── pages/               # Page components
│   │   ├── Home.tsx         # Dashboard with overview
│   │   ├── Transactions.tsx # Transaction list with filters
│   │   ├── Insights.tsx     # Analytics and charts
│   │   ├── Profile.tsx      # User profile and settings
│   │   ├── Upload.tsx       # File upload page
│   │   ├── Login.tsx        # Login page
│   │   └── Signup.tsx       # Signup page
│   ├── lib/                 # Utilities and configuration
│   │   ├── api.ts           # API client
│   │   ├── mockData.ts      # Mock data for development
│   │   └── queryClient.ts   # React Query configuration
│   ├── App.tsx              # Main app with routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles with Tailwind
├── public/                  # Static assets
├── .env                     # Environment variables
└── package.json             # Dependencies

```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

4. Update the API URL in `.env` if needed:
```
VITE_API_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Design System

### Color Palette

- **Background**: `#111315` - Main background
- **Card**: `#1A1C1E` - Card/surface background
- **Primary**: `#FFFFFF` - Primary text
- **Secondary**: `#9BA0A5` - Secondary text
- **Accent**: `#EAFD60` - Brand accent color
- **Success**: `#27C46B` - Success/positive states
- **Error**: `#FF4D4D` - Error/negative states

### Custom CSS Classes

Defined in `src/index.css`:

- `.btn-primary` - Primary button style
- `.btn-secondary` - Secondary button style
- `.card` - Card container style
- `.input` - Input field style

## Pages

### 1. Login (`/login`)
- Email and password authentication
- Link to signup page
- Mock authentication (localStorage)

### 2. Signup (`/signup`)
- User registration form
- Name, email, and password fields
- Password confirmation

### 3. Home (`/`)
- Dashboard overview
- Balance cards (Total, Income, Expenses)
- Top spending categories with progress bars
- Recent transactions list
- Floating action button for upload

### 4. Transactions (`/transactions`)
- Complete transaction list
- Search functionality
- Category filter
- Transaction statistics
- Transaction cards with merchant info

### 5. Insights (`/insights`)
- Monthly spending trend (Line chart)
- Spending by category (Pie chart)
- Category amounts (Bar chart)
- Key insights cards

### 6. Profile (`/profile`)
- User profile information
- Account settings
- Preferences (notifications, reports)
- Logout functionality

### 7. Upload (`/upload`)
- Drag & drop file upload
- Support for PDF, CSV, XLS, XLSX
- Upload progress indicator
- Success/error states

## API Integration

The app is designed to integrate with the FastAPI backend. The API client is located in `src/lib/api.ts`.

### Current Status
- Mock data is used for development/demonstration
- API endpoints are defined and ready to connect
- Switch from mock data to real API by uncommenting API calls in components

### Available API Methods

```typescript
// Authentication
apiClient.login(email, password)
apiClient.signup(email, password, name)

// Transactions
apiClient.getTransactions(params)
apiClient.getTransaction(id)
apiClient.createTransaction(data)

// Statement Upload
apiClient.uploadStatement(file)

// Analytics
apiClient.getAnalytics(params)

// Profile
apiClient.getProfile()
apiClient.updateProfile(data)
```

## Authentication

Simple localStorage-based authentication for development:
- Login/Signup sets `localStorage.setItem('isAuthenticated', 'true')`
- Protected routes check this value
- Logout removes the item

**For production**: Replace with proper JWT/session-based authentication.

## Responsive Design

### Desktop (≥768px)
- Fixed sidebar navigation on the left
- Content area adjusted with padding
- Larger cards and better spacing

### Mobile (<768px)
- Bottom navigation bar (fixed)
- Full-width layout
- Touch-optimized components
- Floating action button positioned above nav

## Development Tips

### Mock Data
All mock data is in `src/lib/mockData.ts`:
- `mockTransactions` - Sample transactions
- `mockCategorySpending` - Category breakdown
- `mockMonthlySpending` - Monthly trend data
- `mockUserProfile` - User profile data

### Adding New Pages
1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation link in `Sidebar.tsx` and `BottomNav.tsx`

### Customizing Styles
- Update colors in `tailwind.config.js`
- Modify global styles in `src/index.css`
- Use Tailwind utility classes in components

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Future Enhancements

- [ ] Real-time data synchronization
- [ ] Budget setting and tracking
- [ ] Recurring transaction detection
- [ ] Export data functionality
- [ ] Multi-currency support
- [ ] Dark/Light theme toggle
- [ ] Advanced filtering and sorting
- [ ] Transaction categories management
- [ ] Receipt attachment support

## Contributing

When contributing to the frontend:

1. Follow the existing code style
2. Use TypeScript for type safety
3. Keep components modular and reusable
4. Test responsive design on multiple screen sizes
5. Ensure accessibility (ARIA labels, keyboard navigation)

## License

This project is part of the Expenditure Helper application.
