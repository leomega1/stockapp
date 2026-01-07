# S&P 500 Stock Tracker - Frontend

Modern Next.js frontend for the S&P 500 Stock Tracker application.

## Features

- Beautiful, responsive dashboard showing daily winners and losers
- Individual article pages with AI-generated insights
- Dark mode support
- Real-time data fetching with React Query
- Modern UI with TailwindCSS
- TypeScript for type safety

## Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Create environment file:

```bash
cp .env.local.example .env.local
```

3. Edit `.env.local` if needed:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx                # Dashboard page
│   ├── article/[symbol]/       # Article detail pages
│   ├── layout.tsx              # Root layout
│   ├── providers.tsx           # React Query provider
│   └── globals.css             # Global styles
├── components/
│   ├── StockCard.tsx           # Stock card component
│   ├── StockChart.tsx          # Chart component
│   ├── LoadingSpinner.tsx      # Loading state
│   └── ErrorMessage.tsx        # Error state
├── lib/
│   └── api.ts                  # API client
└── package.json
```

## Features Breakdown

### Dashboard (`/`)

- Displays top 5 winners and losers from S&P 500
- Color-coded cards (green for winners, red for losers)
- Shows price, percentage change, and volume
- Click any card to view detailed article

### Article Page (`/article/[symbol]`)

- Full AI-generated article explaining stock movement
- Related news headlines
- Stock performance summary
- Disclaimer about AI-generated content

## Customization

### Colors

Edit `tailwind.config.ts` to customize colors:

```typescript
theme: {
  extend: {
    colors: {
      'winner-green': '#10b981',
      'loser-red': '#ef4444',
    },
  },
}
```

### API Endpoint

Change the API URL in `.env.local`:

```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project in Vercel
3. Add environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy!

### Other Platforms

```bash
npm run build
```

Deploy the `.next` folder to any Node.js hosting platform.

## Troubleshooting

### API Connection Issues

Make sure:
1. Backend is running at the URL specified in `.env.local`
2. CORS is properly configured in the backend
3. No firewall blocking the connection

### Build Errors

```bash
rm -rf .next node_modules
npm install
npm run build
```

## License

MIT

