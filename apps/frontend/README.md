# Frontend Lookbk W25

## Prerequisites
- Node.js (latest LTS version recommended)
- npm or yarn

## Getting Started

1. Install dependencies:
```bash
npm install
# or
yarn
```

If you get errors with React 19 just use

```bash
npm install --legacy-peer-deps
```

or 

```bash
npm install --force
```

2. Run the development server:
```bash
npm run dev
# or
yarn dev
```

## Available Scripts

- `npm run dev` - Start the development server with Turbopack
- `npm run build` - Create a production build
- `npm run start` - Start the production server
- `npm run lint` - Run ESLint for code quality checks

## Tech Stack

- Next.js 15.2.0
- React 19
- TypeScript
- TailwindCSS
- ESLint


When you want to do anything related to db just import 

```
import { prisma } from "@/db"; 
```

then you can just use it find the syntax/docs online