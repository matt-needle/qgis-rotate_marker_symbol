#!/bin/bash
# Translation Management Script for Rotate Marker Symbol Plugin
# 
# This script helps manage translations by automating the extract and compile process.
# 
# Usage:
#   ./manage-translations.sh extract   - Extract translatable strings
#   ./manage-translations.sh compile   - Compile .ts to .qm files
#   ./manage-translations.sh all       - Extract and compile
#   ./manage-translations.sh add <lang> - Add a new language

# Configuration
PLUGIN_NAME="rotate_marker_symbol"
SOURCE_FILES="*.py core/*.py"
I18N_DIR="i18n"

# Define which languages to support
# Start with essential European languages
LANGUAGES="nl de fr es it"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if required tools are available
check_tools() {
    if ! command -v pylupdate5 &> /dev/null && ! command -v pylupdate6 &> /dev/null; then
        echo -e "${RED}Error: pylupdate5 or pylupdate6 not found${NC}"
        echo "Install Qt development tools (python3-pyqt5-dev or python3-pyqt6-dev)"
        exit 1
    fi
    
    if ! command -v lrelease &> /dev/null && ! command -v lrelease-qt5 &> /dev/null; then
        echo -e "${RED}Error: lrelease not found${NC}"
        echo "Install Qt development tools"
        exit 1
    fi
}

# Determine which version of tools to use
get_pylupdate() {
    if command -v pylupdate5 &> /dev/null; then
        echo "pylupdate5"
    else
        echo "pylupdate6"
    fi
}

get_lrelease() {
    if command -v lrelease &> /dev/null; then
        echo "lrelease"
    else
        echo "lrelease-qt5"
    fi
}

# Extract translatable strings from source code
extract_strings() {
    echo -e "${GREEN}Extracting translatable strings...${NC}"
    
    # Create i18n directory if it doesn't exist
    mkdir -p "$I18N_DIR"
    
    PYLUPDATE=$(get_pylupdate)
    
    for lang in $LANGUAGES; do
        echo -e "  → ${YELLOW}$I18N_DIR/${lang}.ts${NC}"
        $PYLUPDATE -noobsolete $SOURCE_FILES -ts "$I18N_DIR/${lang}.ts"
    done
    
    echo ""
    echo -e "${GREEN}✓ Extraction complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Edit the .ts files in Qt Linguist:"
    echo "     linguist $I18N_DIR/nl.ts"
    echo ""
    echo "  2. After translating, compile the translations:"
    echo "     $0 compile"
}

# Compile .ts files to .qm files
compile_translations() {
    echo -e "${GREEN}Compiling translation files...${NC}"
    
    LRELEASE=$(get_lrelease)
    COMPILED=0
    
    for lang in $LANGUAGES; do
        ts_file="$I18N_DIR/${lang}.ts"
        qm_file="$I18N_DIR/${lang}.qm"
        
        if [ -f "$ts_file" ]; then
            echo -e "  → ${YELLOW}$qm_file${NC}"
            $LRELEASE "$ts_file" > /dev/null 2>&1
            
            if [ -f "$qm_file" ]; then
                COMPILED=$((COMPILED + 1))
            fi
        else
            echo -e "  ${RED}✗ $ts_file not found${NC}"
        fi
    done
    
    echo ""
    echo -e "${GREEN}✓ Compiled $COMPILED translation files${NC}"
    echo ""
    echo "Translation files are ready for distribution!"
    echo "Include the $I18N_DIR/*.qm files in your plugin package."
}

# Add a new language
add_language() {
    local new_lang=$1
    
    if [ -z "$new_lang" ]; then
        echo -e "${RED}Error: Language code required${NC}"
        echo "Usage: $0 add <language_code>"
        echo ""
        echo "Examples:"
        echo "  $0 add pt    # Portuguese"
        echo "  $0 add pl    # Polish"
        echo "  $0 add ru    # Russian"
        exit 1
    fi
    
    echo -e "${GREEN}Adding new language: $new_lang${NC}"
    
    # Add to LANGUAGES if not already there
    if [[ ! " $LANGUAGES " =~ " $new_lang " ]]; then
        echo "Note: Add '$new_lang' to the LANGUAGES variable in this script to include it in future operations."
    fi
    
    PYLUPDATE=$(get_pylupdate)
    
    echo -e "  → ${YELLOW}$I18N_DIR/${new_lang}.ts${NC}"
    $PYLUPDATE -noobsolete $SOURCE_FILES -ts "$I18N_DIR/${new_lang}.ts"
    
    echo ""
    echo -e "${GREEN}✓ Created $I18N_DIR/${new_lang}.ts${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Edit the new translation file:"
    echo "     linguist $I18N_DIR/${new_lang}.ts"
    echo ""
    echo "  2. Compile when done:"
    echo "     $0 compile"
}

# Show statistics about translations
show_stats() {
    echo -e "${GREEN}Translation Statistics:${NC}"
    echo ""
    
    for lang in $LANGUAGES; do
        ts_file="$I18N_DIR/${lang}.ts"
        qm_file="$I18N_DIR/${lang}.qm"
        
        if [ -f "$ts_file" ]; then
            # Count total and translated messages
            total=$(grep -c "<message>" "$ts_file" 2>/dev/null || echo "0")
            translated=$(grep -c "<translation>[^<]" "$ts_file" 2>/dev/null || echo "0")
            
            if [ -f "$qm_file" ]; then
                compiled="✓"
            else
                compiled="✗"
            fi
            
            echo "  $lang: $translated/$total translated [$compiled]"
        fi
    done
    
    echo ""
}

# Main script logic
case "$1" in
    extract)
        check_tools
        extract_strings
        ;;
    
    compile)
        check_tools
        compile_translations
        ;;
    
    all)
        check_tools
        extract_strings
        compile_translations
        ;;
    
    add)
        check_tools
        add_language "$2"
        ;;
    
    stats)
        show_stats
        ;;
    
    *)
        echo "Usage: $0 {extract|compile|all|add|stats}"
        echo ""
        echo "Commands:"
        echo "  extract          Extract translatable strings from source code"
        echo "  compile          Compile .ts files to .qm files"
        echo "  all              Extract and compile in one step"
        echo "  add <lang>       Add a new language"
        echo "  stats            Show translation statistics"
        echo ""
        echo "Examples:"
        echo "  $0 extract       # Extract strings to .ts files"
        echo "  $0 compile       # Compile .ts to .qm"
        echo "  $0 all           # Do both"
        echo "  $0 add pt        # Add Portuguese"
        echo "  $0 stats         # Show translation progress"
        echo ""
        echo "Supported languages: $LANGUAGES"
        exit 1
        ;;
esac

exit 0
