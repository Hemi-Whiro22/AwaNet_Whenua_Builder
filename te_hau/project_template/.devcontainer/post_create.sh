#!/bin/bash
set -e

echo "🏔️  Setting up Realm Development Environment..."

# Install realm-specific dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Initialize realm directories
echo "📁 Initializing realm structure..."
mkdir -p kaitiaki/{logs,backups}
mkdir -p mauri/{schemas,archives}
mkdir -p te_po_proxy/{logs,backups}

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env configuration..."
    cp .env.template .env || true
fi

# Install Node dependencies if needed
if [ -f "te_ao/package.json" ]; then
    echo "📦 Installing frontend dependencies..."
    cd te_ao
    npm install
    cd ..
fi

echo "✅ Realm development environment ready!"
echo ""
echo "🚀 Quick start:"
echo "   Backend:  cd te_po_proxy && python main.py"
echo "   Frontend: cd te_ao && npm run dev"
echo "   CLI:      cd te_hau && python cli.py status"
echo ""
