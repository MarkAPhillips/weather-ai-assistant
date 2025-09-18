#!/bin/bash

# 🚀 Deploy Angular Frontend to Render
echo "🚀 Deploying Angular Frontend to Render..."
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "client/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Build the Angular app
echo "📦 Building Angular app for production..."
cd client
npm run build --configuration=production

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📁 Build output: client/dist/client/"
    echo ""
    echo "🌐 Next steps:"
    echo "1. Go to https://render.com"
    echo "2. Click 'New +' → 'Static Site'"
    echo "3. Connect your GitHub repository"
    echo "4. Configure:"
    echo "   - Build Command: cd client && npm install && npm run build --configuration=production"
    echo "   - Publish Directory: client/dist/client"
    echo "5. Deploy!"
    echo ""
    echo "📝 Don't forget to update environment.prod.ts with your backend URL!"
else
    echo "❌ Build failed!"
    exit 1
fi
