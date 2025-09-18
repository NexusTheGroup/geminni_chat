# NexusKnowledge Frontend

A modern React/TypeScript frontend for the NexusKnowledge advanced knowledge management system.

## Features

- **Modern Architecture**: Built with React 18, TypeScript 5, and Vite
- **Material-UI Components**: Beautiful, accessible UI components
- **State Management**: Redux Toolkit with RTK Query for API state
- **Responsive Design**: Mobile-first approach with full responsiveness
- **Advanced Search**: Multi-faceted search with filtering and suggestions
- **Real-time Analytics**: Interactive charts and correlation analysis
- **Data Management**: Comprehensive data ingestion and processing interface
- **Accessibility**: WCAG 2.1 compliant with keyboard navigation
- **Testing**: Comprehensive test suite with Jest, React Testing Library, and Cypress

## Tech Stack

- **Framework**: React 18 with TypeScript 5
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI) v5
- **State Management**: Redux Toolkit + RTK Query
- **Routing**: React Router v6
- **Charts**: Recharts + MUI X Charts
- **Testing**: Jest, React Testing Library, Cypress
- **Styling**: Material-UI + Styled Components

## Getting Started

### Prerequisites

- Node.js 18+
- npm or pnpm
- Backend API running on port 8000

### Installation

1. Install dependencies:

```bash
npm install
# or
pnpm install
```

2. Copy environment configuration:

```bash
cp env.example .env.local
```

3. Update environment variables in `.env.local`:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=NexusKnowledge
VITE_APP_VERSION=1.0.0
```

### Development

Start the development server:

```bash
npm run dev
# or
pnpm dev
```

The application will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
# or
pnpm build
```

### Testing

Run unit tests:

```bash
npm run test
# or
pnpm test
```

Run tests with coverage:

```bash
npm run test:coverage
# or
pnpm test:coverage
```

Run E2E tests:

```bash
npm run e2e
# or
pnpm e2e
```

### Linting

```bash
npm run lint
# or
pnpm lint
```

Fix linting issues:

```bash
npm run lint:fix
# or
pnpm lint:fix
```

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Layout/        # Layout components (Header, Sidebar, etc.)
│   │   └── __tests__/     # Component tests
│   ├── pages/             # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Search.tsx
│   │   ├── DataManagement.tsx
│   │   ├── Analytics.tsx
│   │   ├── Settings.tsx
│   │   └── __tests__/     # Page tests
│   ├── store/             # Redux store and slices
│   │   ├── api.ts         # RTK Query API
│   │   ├── slices/        # Redux slices
│   │   └── index.ts       # Store configuration
│   ├── theme.ts           # Material-UI theme
│   ├── App.tsx           # Main app component
│   └── main.tsx          # App entry point
├── cypress/               # E2E tests
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

## API Integration

The frontend integrates with 14 backend API endpoints:

### System

- `GET /api/v1/status` - System status and version

### Search

- `GET /api/v1/search` - Hybrid search with query parameters

### Feedback

- `POST /api/v1/feedback` - Submit feedback
- `GET /api/v1/feedback/{id}` - Get feedback status
- `GET /api/v1/feedback` - List feedback items
- `PATCH /api/v1/feedback/{id}` - Update feedback status

### Data Ingestion

- `POST /api/v1/ingest` - Ingest new data
- `GET /api/v1/ingest/{id}` - Get ingestion status

### Analysis

- `POST /api/v1/analysis` - Queue analysis
- `GET /api/v1/analysis/{id}` - Get analysis status

### Correlation

- `POST /api/v1/correlation` - Queue correlation
- `GET /api/v1/correlation/{id}` - Get correlation candidates
- `POST /api/v1/correlation/{id}/fuse` - Fuse correlations

### Export

- `POST /api/v1/export/obsidian` - Export to Obsidian format

## Performance Targets

- **Page Load Time**: < 2 seconds
- **Lighthouse Score**: > 90
- **Bundle Size**: < 500KB gzipped
- **Mobile Responsiveness**: 100%
- **Code Coverage**: > 90%
- **TypeScript Coverage**: 100%
- **Accessibility Score**: > 95%

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style and patterns
2. Write tests for new features
3. Ensure accessibility compliance
4. Update documentation as needed
5. Run linting and tests before committing

## License

This project is part of the NexusKnowledge system. See the main project README for license information.
