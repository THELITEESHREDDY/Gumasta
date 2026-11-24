# Gumasta Mobile

# project structure
GumastaMobile/
│
├── assets/
│   ├── images/
│   ├── icons/
│   └── fonts/
│
├── src/
│   │
│   ├── app/                       # Expo Router
│   │   ├── _layout.tsx            # Root layout
│   │   ├── index.tsx              # Initial redirect
│   │   │
│   │   ├── (auth)/
│   │   │   ├── _layout.tsx
│   │   │   ├── login.tsx
│   │   │   └── register.tsx
│   │   │
│   │   └── (tabs)/
│   │       ├── _layout.tsx        # Bottom navigation
│   │       │
│   │       ├── dashboard/
│   │       │   ├── _layout.tsx
│   │       │   ├── index.tsx
│   │       │   ├── orders/
│   │       │   │   ├── index.tsx
│   │       │   │   └── [direction].tsx
│   │       │   └── transactions/
│   │       │       ├── index.tsx
│   │       │       └── [direction].tsx
│   │       │
│   │       ├── analysis/
│   │       │   ├── _layout.tsx
│   │       │   ├── index.tsx
│   │       │   ├── item-analysis.tsx
│   │       │   ├── sales-analysis.tsx
│   │       │   ├── customers.tsx
│   │       │   ├── traders.tsx
│   │       │   └── inventory.tsx
│   │       │
│   │       └── profile/
│   │           ├── _layout.tsx
│   │           ├── index.tsx
│   │           ├── owner.tsx
│   │           └── shop.tsx
│   │
│   ├── components/                # Shared components
│   │   ├── ui/
│   │   ├── navigation/
│   │   ├── charts/
│   │   └── forms/
│   │
│   ├── features/                  # Feature-specific logic
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── orders/
│   │   ├── transactions/
│   │   ├── analytics/
│   │   ├── customers/
│   │   ├── traders/
│   │   ├── inventory/
│   │   └── profile/
│   │
│   ├── services/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── auth.api.ts
│   │   │   ├── dashboard.api.ts
│   │   │   ├── orders.api.ts
│   │   │   └── ...
│   │
│   ├── store/
│   ├── hooks/
│   ├── types/
│   ├── constants/
│   ├── utils/
│   └── theme/
│
├── app.json
├── package.json
└── tsconfig.json