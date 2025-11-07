#!/usr/bin/env bash
# Translation Management Script for QGIS Plugin (simple + reliable)
# Uses the OSGeo4W Python environment directly

# --- Force OSGeo4W Python on PATH -----------------------------------------
export PATH="/c/OSGeo4W/bin:/c/OSGeo4W/apps/Qt5/bin:$PATH"

PYLUPDATE_BIN="lupdate"
LRELEASE_BIN="lrelease"

PLUGIN_NAME="rotate_marker_symbol"
SOURCE_FILES="$(find . -name '*.py')"
I18N_DIR="i18n"
LANGUAGES="nl de fr es it"

PYTHON_BIN="python.exe"

# --- Qt tools -------------------------------------------------------------
PYLUPDATE_BIN="pylupdate5"
LRELEASE_BIN="lrelease"

# --- Actions --------------------------------------------------------------
extract_strings() {
    echo "📦 Extracting translatable strings..."
    mkdir -p "$I18N_DIR"

    for lang in $LANGUAGES; do
        echo "→ $I18N_DIR/${lang}.ts"
        "$PYLUPDATE_BIN" $SOURCE_FILES -ts "$I18N_DIR/${lang}.ts" -noobsolete
    done

    echo "✅ Extraction complete"
}

compile_translations() {
    echo "🔧 Compiling translations..."
    mkdir -p "$I18N_DIR"

    for lang in $LANGUAGES; do
        ts="$I18N_DIR/${lang}.ts"
        qm="$I18N_DIR/${lang}.qm"
        if [ -f "$ts" ]; then
            echo "→ $qm"
            "$LRELEASE_BIN" "$ts" -qm "$qm"
        else
            echo "⚠️  Missing $ts"
        fi
    done

    echo "✅ Compilation complete"
}

# --- Entry point ----------------------------------------------------------
case "$1" in
    extract) extract_strings ;;
    compile) compile_translations ;;
    all) extract_strings; compile_translations ;;
    *)
        echo "Usage: $0 {extract|compile|all}"
        exit 1
        ;;
esac
