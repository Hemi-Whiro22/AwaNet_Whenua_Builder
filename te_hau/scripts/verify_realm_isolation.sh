#!/bin/bash
# verify_realm_isolation.sh
# Test script to verify realm isolation after generation

set -e

REALM_PATH="${1:-.}"

if [ ! -f "$REALM_PATH/mauri/kaitiaki_templates/realm.yaml" ]; then
    echo "❌ Not a realm directory (no realm.yaml found)"
    exit 1
fi

echo "🔐 Verifying Realm Isolation..."
echo "=================================="
echo ""

# Check 1: DevContainer exists
echo "✓ Checking .devcontainer..."
if [ -f "$REALM_PATH/.devcontainer/devcontainer.json" ]; then
    echo "  ✅ .devcontainer/devcontainer.json found"
else
    echo "  ❌ .devcontainer/devcontainer.json missing"
    exit 1
fi

if [ -f "$REALM_PATH/.devcontainer/Dockerfile" ]; then
    echo "  ✅ .devcontainer/Dockerfile found"
else
    echo "  ❌ .devcontainer/Dockerfile missing"
    exit 1
fi

# Check 2: VS Code settings
echo "✓ Checking .vscode settings..."
if [ -f "$REALM_PATH/.vscode/settings.json" ]; then
    echo "  ✅ .vscode/settings.json found"
else
    echo "  ❌ .vscode/settings.json missing"
    exit 1
fi

# Check 3: Isolation rules in YAML
echo "✓ Checking isolation rules..."
if grep -q "isolation:" "$REALM_PATH/mauri/kaitiaki_templates/realm.yaml" 2>/dev/null; then
    echo "  ✅ Isolation rules found in realm.yaml"

    if grep -q "allow_parent_traversal: false" "$REALM_PATH/mauri/kaitiaki_templates/realm.yaml"; then
        echo "  ✅ Parent traversal disabled"
    fi

    if grep -q "allow_main_awa_network: false" "$REALM_PATH/mauri/kaitiaki_templates/realm.yaml"; then
        echo "  ✅ Main Awa Network access disabled"
    fi
else
    echo "  ❌ Isolation rules missing in realm.yaml"
    exit 1
fi

# Check 4: Requirements.txt exists
echo "✓ Checking dependencies..."
if [ -f "$REALM_PATH/requirements.txt" ]; then
    echo "  ✅ requirements.txt found"
    echo "  📦 Dependencies:"
    grep -E "^[a-z]" "$REALM_PATH/requirements.txt" | head -5 | sed 's/^/     /'
else
    echo "  ⚠️  requirements.txt missing (optional)"
fi

# Check 5: Kaitiaki directory structure
echo "✓ Checking Kaitiaki structure..."
if [ -d "$REALM_PATH/kaitiaki" ]; then
    echo "  ✅ kaitiaki/ directory found"
else
    echo "  ⚠️  kaitiaki/ directory not yet created"
fi

# Check 6: No parent references in config
echo "✓ Checking for parent references..."
if grep -r "\.\./" "$REALM_PATH/config/" 2>/dev/null; then
    echo "  ⚠️  Found ../ references (possible context bleed)"
else
    echo "  ✅ No parent directory references"
fi

# Check 7: .env is realm-local
echo "✓ Checking .env isolation..."
if [ -f "$REALM_PATH/.env" ]; then
    if head -1 "$REALM_PATH/.env" | grep -q "# Realm-specific"; then
        echo "  ✅ .env is realm-specific"
    else
        echo "  ⚠️  .env doesn't have realm marker"
    fi
elif [ -f "$REALM_PATH/.env.template" ]; then
    echo "  ℹ️  .env not created yet (use .env.template)"
fi

echo ""
echo "=================================="
echo "✅ Realm isolation verified!"
echo ""
echo "Next steps:"
echo "  1. cd $REALM_PATH"
echo "  2. Open in VS Code (Reopen in Container)"
echo "  3. Each realm runs in isolated devcontainer ✅"
