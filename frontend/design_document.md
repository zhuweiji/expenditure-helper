# Design Document 

### Version 1.0

**Purpose:** Design a responsive, dark-mode-first and mobile friendly personal finance web app with features.

---

## 🎨 Visual & Interaction Design

**Design Principles**

- Minimalist and data-first interface
- Emphasis on typography and clarity
- Smooth animations and transitions
- Mobile-first responsive layout
- Consistent dark mode aesthetic with soft highlights (accent color: neon yellow or teal)

**Aesthetic References**

- Fintech dashboards (e.g., Revolut, Robinhood)
- Productivity AI assistants (like the second uploaded image)
- Rounded cards, consistent grid spacing, monochrome color palette

**Color Palette**

| Element         | Color                   |
| --------------- | ----------------------- |
| Background      | `#111315`               |
| Card Background | `#1A1C1E`               |
| Primary Text    | `#FFFFFF`               |
| Secondary Text  | `#9BA0A5`               |
| Accent          | `#EAFD60` (neon yellow) |
| Success         | `#27C46B`               |
| Error           | `#FF4D4D`               |

---

## 🧩 Core Modules

### 1. Statement Ingestion & Insights

**Purpose:** Allow users to upload their credit card statements (PDF/CSV) for parsing and analysis.

**Flow:**

1. User uploads file (drag & drop or file picker)
2. Server processes file (OCR + statement parser)
3. Transactions are normalized and stored in database
4. User can view analytics and insights

**UI Components:**

- **Upload Card:** floating action button (FAB) → “Upload Statement”
- **Progress State:** animated loader with parsing progress
- **Transaction Feed:** list view with icons, merchant, category, date, and amount

- **Analytics Dashboard:**

  - Monthly spend graph
  - Category pie chart
  - Recurring payment detection
  - Spending trends over time
  - Categorization by merchant and description matching
  - Recurring expense detection

---

## ⚙️ Technical Architecture

**Frontend:**

- Framework: React + Tailwind CSS
- Charting: Recharts / D3.js
- File Upload: Uppy / Dropzone
- React Query


---

## 🧱 Information Architecture (IA)

**Primary Navigation Tabs**

1. **Home** — dashboard of total balance, spending trends
1. **Transactions** — detailed transaction view
1. **Insights** — smart recommendations, trends, and financial tips
1. **Profile** — account management, preferences

**Secondary Components**

- Floating “+” button for quick add (expense, group, upload)
- Notifications panel (e.g., “Statement processed successfully”)
- Search and filter bar

---

## 📱 Responsiveness

**Mobile Layout:**

- Bottom navigation bar with icons (Home, Transactions, Groups, Insights, Profile)
- Cards with swipe gestures for edit/delete
- Optimized touch targets

**Desktop Layout:**

- Left sidebar navigation
- Dashboard grid (2–3 columns)
- Expandable cards with hover animations

