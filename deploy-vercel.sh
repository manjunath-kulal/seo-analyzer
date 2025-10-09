#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 SEO Analyzer - Vercel Deployment Script${NC}\n"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI is not installed${NC}"
    echo -e "${YELLOW}Installing Vercel CLI...${NC}"
    npm i -g vercel
fi

echo -e "${BLUE}📦 Step 1: Deploying Backend...${NC}\n"

cd backend

echo -e "${YELLOW}Deploying backend to Vercel...${NC}"
vercel --prod

echo -e "\n${GREEN}✅ Backend deployed!${NC}"
echo -e "${YELLOW}📋 Copy your backend URL from above (e.g., https://seo-analyzer-backend.vercel.app)${NC}\n"

read -p "Paste your backend URL here: " BACKEND_URL

cd ..

echo -e "\n${BLUE}🎨 Step 2: Setting up Frontend Environment...${NC}\n"

cd frontend

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > .env.local

echo -e "${GREEN}✅ Created .env.local with backend URL${NC}\n"

echo -e "${YELLOW}Now, you need to add the environment variable in Vercel:${NC}"
echo -e "1. Go to your Vercel dashboard"
echo -e "2. Create/select your frontend project"
echo -e "3. Go to Settings → Environment Variables"
echo -e "4. Add: NEXT_PUBLIC_API_URL = $BACKEND_URL"
echo -e "5. Select all environments (Production, Preview, Development)\n"

read -p "Press Enter once you've added the environment variable in Vercel dashboard..."

echo -e "\n${BLUE}Deploying frontend to Vercel...${NC}"
vercel --prod

cd ..

echo -e "\n${GREEN}✨ Deployment Complete!${NC}\n"
echo -e "${BLUE}Your SEO Analyzer is now live on Vercel!${NC}"
echo -e "\n📊 Summary:"
echo -e "Backend URL: ${BACKEND_URL}"
echo -e "Frontend URL: Check the output above\n"
echo -e "${YELLOW}📝 See DEPLOYMENT.md for detailed documentation${NC}\n"
