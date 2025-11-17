# 🚀 Enhanced Vehicle Appraisal System

**Version:** 8.1.0  
**Status:** Production Ready ✅

A professional-grade vehicle trade-in management system with AI-powered analysis, smart OCR, and mobile-first design for automotive sales teams.

---

## ✨ Features

### Core Capabilities
- 🎯 **Mobile-First Design** - Optimized for sales personnel on mobile devices
- 🤖 **AI-Powered Analysis** - Google Gemini Vision API for comprehensive vehicle assessment
- 📸 **Photo Guidance System** - Step-by-step visual overlays for optimal photo capture
- 🔍 **Smart OCR System**:
  - VIN Scanner with NHTSA auto-decode
  - License Plate Recognition  
  - Odometer reading extraction with error handling
- 📊 **Professional Manager Dashboard** - Real-time analytics, charts, and performance metrics
- 🔐 **Role-Based Access Control** - Admin, Manager, and Sales user roles
- ☁️ **Firebase Integration** - Authentication, Firestore database, Cloud Storage

### Advanced Features
- Real-time VIN decoding with vehicle history
- Multi-vehicle photo analysis with damage assessment
- Confidence scoring and condition grading (A+ to D)
- Mobile-optimized photo capture with guidance overlays
- Comprehensive error handling with user-friendly messages
- Responsive design across all device sizes

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **UI Library**: React 18 with TypeScript
- **Styling**: Tailwind CSS 3.4
- **Components**: ShadCN/UI (Radix UI primitives)
- **Icons**: Lucide React
- **Fonts**: Geist Sans & Mono

### Backend
- **API Routes**: Next.js serverless functions
- **Database**: Firebase Firestore
- **Authentication**: Firebase Auth
- **Storage**: Firebase Cloud Storage
- **OCR Engine**: Google Cloud Vision API
- **AI Analysis**: Google Gemini 2.0 Flash

### Development
- **Language**: TypeScript 5.6
- **Package Manager**: npm
- **Build Tool**: Next.js compiler
- **Deployment**: Vercel (or any Node.js host)

---

## 📦 Project Structure

```
enhanced-vehicle-system/
├── app/                          # Next.js App Router
│   ├── api/                      # API routes
│   │   ├── admin/               # User management endpoints
│   │   ├── analyze-vehicle-photos/  # Gemini AI analysis
│   │   ├── ocr-*/               # OCR endpoints (VIN, plate, mileage)
│   │   └── vin-decode/          # NHTSA VIN decoder
│   ├── admin/                   # Admin panel page
│   ├── manager-dashboard/       # Manager dashboard page
│   ├── submit/                  # Trade-in form page
│   ├── layout.tsx               # Root layout with navigation
│   └── page.tsx                 # Home/login page
├── components/                   # React components
│   ├── ui/                      # ShadCN UI components
│   ├── EnhancedTradeInForm.tsx  # Main submission form
│   ├── EnhancedManagerDashboard.tsx  # Dashboard component
│   ├── MainNavigation.tsx       # Navigation bar
│   ├── PhotoGuidance.tsx        # Photo capture guidance
│   └── SimpleLoginForm.tsx      # Authentication form
├── lib/                          # Utility libraries
│   ├── firebaseconfig.ts        # Firebase client config
│   ├── firebase-admin.ts        # Firebase Admin SDK
│   ├── auth-utils.ts            # Authentication helpers
│   └── utils/                   # Shared utilities
├── public/                       # Static assets
├── styles/                       # Global styles
└── hooks/                        # Custom React hooks
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Firebase account with project
- Google Cloud account with Vision API and Gemini API enabled

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/PriorityLexusVB/enhanced-vehicle-system.git
   cd enhanced-vehicle-system
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials (see Environment Variables section below)

4. **Run development server**
   ```bash
   npm run dev
   ```
   
   Open [http://localhost:3000](http://localhost:3000)

5. **Build for production**
   ```bash
   npm run build
   npm start
   ```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory with the following variables:

### Firebase Configuration
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### Firebase Admin SDK (Server-side)
```env
FIREBASE_ADMIN_PROJECT_ID=your_project_id
FIREBASE_ADMIN_CLIENT_EMAIL=firebase-adminsdk@your_project.iam.gserviceaccount.com
FIREBASE_ADMIN_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

### Google Cloud APIs
```env
GOOGLE_CLOUD_PROJECT_ID=your_project_id
GEMINI_API_KEY=your_gemini_api_key
```

**Note:** See `.env.example` for a complete template with comments.

---

## 📱 Key Components

### EnhancedTradeInForm
Mobile-optimized vehicle submission form with:
- Step-by-step photo capture with guidance overlays
- Real-time VIN decoding
- OCR for automatic data extraction
- Progress tracking and validation

### EnhancedManagerDashboard
Professional analytics dashboard featuring:
- Real-time submission statistics
- AI-powered vehicle analysis results
- Interactive charts and metrics
- Submission management interface

### PhotoGuidance System
Intelligent photo capture assistance:
- Visual overlays for 7 photo types (front, rear, interior, etc.)
- Best practice guidance for lighting and angles
- Real-time feedback on photo quality

---

## 🔌 API Endpoints

### Vehicle Analysis
- `POST /api/analyze-vehicle-photos` - Gemini AI analysis
- `POST /api/vin-decode` - NHTSA VIN decoder
- `GET /api/vin-decode/cache-stats` - Decoder cache statistics

### OCR Services
- `POST /api/ocr-vin` - Extract VIN from photo
- `POST /api/ocr-license-plate` - Extract license plate
- `POST /api/ocr-mileage` - Extract odometer reading

### Admin
- `GET /api/admin/users` - List all users
- `POST /api/admin/add-user` - Create new user
- `DELETE /api/admin/delete-user` - Remove user

---

## 🚢 Deployment

### Deploy to Vercel (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

3. **Configure environment variables** in Vercel dashboard

4. **Set up domains** and SSL certificates

### Alternative Deployment Options
- **Firebase Hosting** - with Cloud Functions for API routes
- **AWS Amplify** - with Lambda functions
- **Docker** - containerized deployment

---

## 🔒 Security

### Implemented Security Features
- ✅ Firebase Authentication with secure token handling
- ✅ Role-based access control (RBAC)
- ✅ Environment variable protection (no secrets in code)
- ✅ HTTPS-only in production
- ✅ Firestore security rules (configure in Firebase Console)
- ✅ Input validation and sanitization
- ✅ CORS configuration

### Security Best Practices
1. Never commit `.env` files or service account JSON files
2. Rotate API keys regularly
3. Use Firebase Security Rules to restrict database access
4. Enable Firebase App Check for API protection
5. Implement rate limiting for API endpoints
6. Regular security audits: `npm audit`

---

## 🧪 Testing

Currently using manual testing. Recommended test framework setup:

```bash
# Install testing dependencies (not yet configured)
npm install -D jest @testing-library/react @testing-library/jest-dom
npm install -D playwright @playwright/test
```

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 👥 Contributing

Internal project. For access or questions, contact the development team.

---

## 📞 Support

For technical support or feature requests, please contact:
- **Email**: support@priority-appraisal.com
- **Repository**: [GitHub Issues](https://github.com/PriorityLexusVB/enhanced-vehicle-system/issues)

---

## 📚 Additional Documentation

- `COMPREHENSIVE_APP_DIAGNOSIS.md` - Detailed app analysis and recommendations
- `CLEANUP_PLAN.md` - Repository maintenance guide
- `.env.example` - Environment variable template

---

## 🔄 Version History

- **v8.1.0** (Current) - Security updates, cleanup, documentation overhaul
- **v8.0.0** - Gemini AI integration, enhanced OCR error handling
- **v7.0.0** - Photo guidance system, mobile optimization
- **v6.0.0** - Manager dashboard with analytics
- **v5.0.0** - OCR integration with Google Vision API

---

**Built with ❤️ for Priority Lexus Virginia Beach**