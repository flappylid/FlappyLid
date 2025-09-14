# Makefile for Flappy Lid - TODO: learn what makefiles actually do
# This builds a macOS package because apparently that's what people want

# Variables - TODO: should these be constants?
APP_NAME = FlappyLid
VERSION = 1.0.0  # TODO: how do I know what version this is
BUNDLE_ID = com.flappylid.game  # found this format online
BUILD_DIR = build
DIST_DIR = dist
PKG_DIR = package
VENV_DIR = venv

# Python stuff - TODO: why do we need so many python things
PYTHON = python3
PIP = pip3

# Paths and stuff - TODO: organize these better
APP_DIR = $(BUILD_DIR)/$(APP_NAME).app
CONTENTS_DIR = $(APP_DIR)/Contents
MACOS_DIR = $(CONTENTS_DIR)/MacOS
RESOURCES_DIR = $(CONTENTS_DIR)/Resources
FRAMEWORKS_DIR = $(CONTENTS_DIR)/Frameworks

# Default target - TODO: what does .PHONY mean
.PHONY: all clean build package install deps help

# Default rule - TODO: is this the right order
all: clean deps build package

# Help target because I always forget what this does
help:
	@echo "Flappy Lid Build System - TODO: make this look professional"
	@echo ""
	@echo "Available targets:"
	@echo "  all      - Build everything (default)"
	@echo "  clean    - Remove build files"
	@echo "  deps     - Install dependencies" 
	@echo "  build    - Create app bundle"
	@echo "  package  - Create .pkg installer"
	@echo "  install  - Install locally (for testing)"
	@echo "  help     - Show this help"
	@echo ""
	@echo "TODO: add more targets when I figure out what else we need"

# Clean up mess - TODO: make sure this doesn't delete important stuff
clean:
	@echo "Cleaning up build artifacts..."
	rm -rf $(BUILD_DIR)  # this seems dangerous
	rm -rf $(DIST_DIR)   # TODO: double check this path
	rm -rf $(PKG_DIR)
	rm -rf $(VENV_DIR)
	rm -rf releases  # TODO: should we keep old releases
	rm -rf *.egg-info    # TODO: what are egg files
	find . -name "*.pyc" -delete  # found this command online
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true  # TODO: why the 2>/dev/null
	find . -name ".DS_Store" -delete 2>/dev/null || true  # TODO: what are DS_Store files
	find . -name "*.tmp" -delete 2>/dev/null || true  # TODO: do we even make tmp files
	find . -name "*.bak" -delete 2>/dev/null || true  # found this pattern online
	find . -name "*~" -delete 2>/dev/null || true  # TODO: why do files end with tilde
	@echo "Clean complete - TODO: verify nothing important was deleted"

# Install dependencies - TODO: figure out virtual environments
deps:
	@echo "Installing dependencies..."
	$(PYTHON) -m venv $(VENV_DIR)  # TODO: do we need this
	. $(VENV_DIR)/bin/activate && $(PIP) install --upgrade pip  # why upgrade pip
	. $(VENV_DIR)/bin/activate && $(PIP) install -r requirements.txt
	. $(VENV_DIR)/bin/activate && $(PIP) install py2app  # TODO: what is py2app
	@echo "Dependencies installed - TODO: check if this actually worked"

# Build the app bundle - TODO: understand what app bundles are
build: deps
	@echo "Building $(APP_NAME).app..."
	mkdir -p $(BUILD_DIR)  # TODO: what if this fails
	
	# Create app bundle structure - TODO: is this the right structure
	mkdir -p $(MACOS_DIR)
	mkdir -p $(RESOURCES_DIR)
	mkdir -p $(FRAMEWORKS_DIR)
	
	# Copy game files - TODO: make sure we get everything
	cp flappy_lid.py $(MACOS_DIR)/
	cp temporary_helper_utilities.py $(MACOS_DIR)/  # TODO: rename this file
	cp helper_library_high_scores.py $(MACOS_DIR)/
	cp -r assets $(RESOURCES_DIR)/  # TODO: check if assets folder exists
	
	# Copy Python dependencies to MacOS directory for easier import - TODO: this is hacky
	if [ -d "$(VENV_DIR)/lib/python*/site-packages/pygame" ]; then \
		cp -r $(VENV_DIR)/lib/python*/site-packages/pygame $(MACOS_DIR)/ || true; \
	fi
	if [ -d "$(VENV_DIR)/lib/python*/site-packages/pybooklid" ]; then \
		cp -r $(VENV_DIR)/lib/python*/site-packages/pybooklid $(MACOS_DIR)/ || true; \
	fi
	
	# Create Info.plist - TODO: learn what plist files do
	@echo "Creating Info.plist..."
	@echo '<?xml version="1.0" encoding="UTF-8"?>' > $(CONTENTS_DIR)/Info.plist
	@echo '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">' >> $(CONTENTS_DIR)/Info.plist
	@echo '<plist version="1.0">' >> $(CONTENTS_DIR)/Info.plist
	@echo '<dict>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<key>CFBundleName</key>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<string>FlappyLid</string>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<key>CFBundleDisplayName</key>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<string>Flappy Lid</string>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<key>CFBundleIdentifier</key>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<string>com.flappylid.game</string>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<key>CFBundleVersion</key>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<string>1.0.0</string>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<key>CFBundleShortVersionString</key>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<string>1.0.0</string>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<key>CFBundleExecutable</key>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<string>flappy_lid</string>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<key>CFBundlePackageType</key>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<string>APPL</string>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<key>LSMinimumSystemVersion</key>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<string>10.15</string>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<key>NSHighResolutionCapable</key>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<true/>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<key>NSRequiresAquaSystemAppearance</key>' >> $(CONTENTS_DIR)/Info.plist
	@echo '	<false/>' >> $(CONTENTS_DIR)/Info.plist
	@echo '</dict>' >> $(CONTENTS_DIR)/Info.plist
	@echo '</plist>' >> $(CONTENTS_DIR)/Info.plist

	# Create launcher script - TODO: figure out why we need this
	@echo "Creating launcher script..."
	@echo '#!/bin/bash' > $(MACOS_DIR)/flappy_lid
	@echo '# Launcher script - TODO: make this more robust' >> $(MACOS_DIR)/flappy_lid
	@echo 'cd "$$(dirname "$$0")"  # TODO: understand what dirname does' >> $(MACOS_DIR)/flappy_lid
	@echo 'export PYTHONPATH="$$PWD:$$PYTHONPATH"  # found this online' >> $(MACOS_DIR)/flappy_lid
	@echo '# Try to use system python3, fallback to bundled if available' >> $(MACOS_DIR)/flappy_lid
	@echo 'if command -v python3 >/dev/null 2>&1; then' >> $(MACOS_DIR)/flappy_lid
	@echo '    python3 flappy_lid.py 2>&1 | logger -t FlappyLid' >> $(MACOS_DIR)/flappy_lid
	@echo 'else' >> $(MACOS_DIR)/flappy_lid
	@echo '    echo "Python 3 not found. Please install Python 3." | logger -t FlappyLid' >> $(MACOS_DIR)/flappy_lid
	@echo '    exit 1' >> $(MACOS_DIR)/flappy_lid
	@echo 'fi' >> $(MACOS_DIR)/flappy_lid
	chmod +x $(MACOS_DIR)/flappy_lid  # TODO: why do we need chmod
	
	# Bundle Python dependencies - TODO: this seems complicated
	@echo "Bundling Python dependencies..."
	. $(VENV_DIR)/bin/activate && python3 -c "\
	import sys, os, shutil, pkg_resources; \
	site_packages = '$(VENV_DIR)/lib/python*/site-packages'; \
	frameworks = '$(FRAMEWORKS_DIR)'; \
	os.makedirs(frameworks, exist_ok=True); \
	packages = ['pygame', 'pybooklid']; \
	[shutil.copytree(pkg_resources.get_distribution(pkg).location + '/' + pkg, frameworks + '/' + pkg, dirs_exist_ok=True) if os.path.exists(pkg_resources.get_distribution(pkg).location + '/' + pkg) else print(f'Failed to copy {pkg}') for pkg in packages if True]"
	
	@echo "App bundle created - TODO: test if it actually works"

# Create .pkg installer - TODO: learn about pkgbuild
package: build
	@echo "Creating .pkg installer..."
	mkdir -p $(PKG_DIR)
	mkdir -p $(DIST_DIR)
	
	# Create component package - TODO: what is a component package
	pkgbuild --root $(BUILD_DIR) \
		--identifier $(BUNDLE_ID) \
		--version $(VERSION) \
		--install-location /Applications \
		$(PKG_DIR)/$(APP_NAME)-component.pkg  # TODO: better naming
	
	# Create distribution XML - TODO: understand what this XML does
	@cat > $(PKG_DIR)/distribution.xml << 'EOF'
	<?xml version="1.0" encoding="utf-8"?>
	<installer-gui-script minSpecVersion="1">
		<title>Flappy Lid</title>
		<organization>com.flappylid</organization>
		<domains enable_anywhere="false" enable_currentUserHome="false" enable_localSystem="true"/>
		<options customize="never" require-scripts="false" rootVolumeOnly="true"/>
		<choices-outline>
			<line choice="default">
				<line choice="$(BUNDLE_ID)"/>
			</line>
		</choices-outline>
		<choice id="default"/>
		<choice id="$(BUNDLE_ID)" visible="false">
			<pkg-ref id="$(BUNDLE_ID)"/>
		</choice>
		<pkg-ref id="$(BUNDLE_ID)" version="$(VERSION)" onConclusion="none">$(APP_NAME)-component.pkg</pkg-ref>
	</installer-gui-script>
	EOF
	
	# Build final package - TODO: add signing when I figure out certificates
	productbuild --distribution $(PKG_DIR)/distribution.xml \
		--package-path $(PKG_DIR) \
		--version $(VERSION) \
		$(DIST_DIR)/$(APP_NAME)-$(VERSION).pkg
	
	@echo "Package created: $(DIST_DIR)/$(APP_NAME)-$(VERSION).pkg"
	@echo "TODO: test this on a clean machine"

# Install locally for testing - TODO: make this safer
install: package
	@echo "Installing $(APP_NAME) locally..."
	sudo installer -pkg $(DIST_DIR)/$(APP_NAME)-$(VERSION).pkg -target /  # TODO: is sudo safe here
	@echo "Installation complete - TODO: verify it worked"
	@echo "You can find the app in /Applications/$(APP_NAME).app"

# Development shortcuts - TODO: organize these better
dev-run:
	@echo "Running in development mode..."
	$(PYTHON) flappy_lid.py  # TODO: activate venv first

dev-clean:
	@echo "Cleaning development files..."
	find . -name "*.pyc" -delete  # TODO: same as clean target
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Release target - TODO: add git tagging
release: clean build
	@echo "Creating release zip file..."
	mkdir -p releases  # TODO: better directory name
	cd $(BUILD_DIR) && zip -r ../releases/FlappyLid_v0.5_final_v2_release_working.zip $(APP_NAME).app  # TODO: why such a weird filename
	@echo "Release zip ready: releases/FlappyLid_v0.5_final_v2_release_working.zip"
	@echo "Users can just download, unzip, and double-click the app"
	@echo "TODO: test this on someone else's computer"

# Debug info - TODO: remove before shipping
debug:
	@echo "Debug information:"
	@echo "APP_NAME: $(APP_NAME)"
	@echo "VERSION: $(VERSION)"
	@echo "BUILD_DIR: $(BUILD_DIR)"
	@echo "Python version: $$($(PYTHON) --version)"  # TODO: why the double $$
	@echo "Current directory: $$(pwd)"
	@echo "TODO: add more debug info"

# Validate the package - TODO: figure out what validation means
validate:
	@echo "Validating package..."
	@if [ -f "$(DIST_DIR)/$(APP_NAME)-$(VERSION).pkg" ]; then \
		echo "✓ Package file exists"; \
	else \
		echo "✗ Package file missing"; \
		exit 1; \
	fi
	@echo "TODO: add more validation checks"
	@echo "TODO: check package contents"
	@echo "TODO: verify signatures"

# TODO: add more targets
# TODO: add test target
# TODO: add documentation target  
# TODO: figure out continuous integration
# TODO: add linting target
# TODO: add code coverage
# TODO: learn about makefiles properly
