# Project Structure

```
bff-fabric-flattener/
├── .github/
│   └── workflows/
│       └── build.yml              # GitHub Actions CI/CD workflow
├── bff/                            # BFF executable folder (created during build)
│   └── bff-command-line.exe       # BFF binary (Windows)
├── main.py                         # Main application entry point
├── requirements.txt                # Python dependencies
├── BFF-Fabric-Flattener.spec      # PyInstaller build specification
├── README.md                       # User documentation
├── PROJECT_STRUCTURE.md            # This file
├── LICENSE                         # License file
├── icon.ico                        # Application icon (optional)
└── .gitignore                      # Git ignore rules
```

## File Descriptions

### Core Application Files

**`main.py`**
- Main application code
- Contains PyQt6 GUI implementation
- BFF processing logic
- SVG conversion utilities

**`requirements.txt`**
- Lists Python package dependencies
- Used by pip for installation
- Required for both development and building

**`BFF-Fabric-Flattener.spec`**
- PyInstaller specification file
- Defines how to bundle the application
- Includes BFF executable in the bundle

### GitHub Actions

**`.github/workflows/build.yml`**
- Automated build pipeline
- Compiles BFF from source
- Packages Python GUI with PyInstaller
- Creates Windows releases
- Runs on every push/tag

### BFF Executable

**`bff/bff-command-line.exe`**
- Compiled BFF binary for Windows
- Built from: https://github.com/GeometryCollective/boundary-first-flattening
- Requires SuiteSparse dependency
- Command-line interface to BFF algorithm

## Setup Instructions

### Initial Setup

1. **Create the repository structure:**
   ```bash
   mkdir bff-fabric-flattener
   cd bff-fabric-flattener
   mkdir bff .github/workflows
   ```

2. **Add the files:**
   - Copy `main.py` to root
   - Copy `requirements.txt` to root
   - Copy `BFF-Fabric-Flattener.spec` to root
   - Copy `build.yml` to `.github/workflows/`
   - Copy `README.md` to root

3. **Create .gitignore:**
   ```
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   build/
   develop-eggs/
   dist/
   downloads/
   eggs/
   .eggs/
   lib/
   lib64/
   parts/
   sdist/
   var/
   wheels/
   *.egg-info/
   .installed.cfg
   *.egg
   
   # PyInstaller
   *.manifest
   *.spec
   
   # Virtual environments
   venv/
   ENV/
   env/
   
   # IDE
   .vscode/
   .idea/
   *.swp
   *.swo
   
   # OS
   .DS_Store
   Thumbs.db
   
   # BFF source (if building locally)
   bff-source/
   
   # Built executables are tracked in releases, not git
   bff/*.exe
   ```

4. **Initialize git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

5. **Create GitHub repository:**
   - Go to GitHub and create a new repository
   - Push your local repository:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/bff-fabric-flattener.git
   git branch -M main
   git push -u origin main
   ```

### Building Locally (Development)

1. **Setup Python environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Build BFF executable:**
   ```bash
   # Clone BFF
   git clone --recursive https://github.com/GeometryCollective/boundary-first-flattening.git bff-source
   cd bff-source
   
   # Install vcpkg if not already installed
   git clone https://github.com/Microsoft/vcpkg.git C:\vcpkg
   cd C:\vcpkg
   .\bootstrap-vcpkg.bat
   .\vcpkg integrate install
   
   # Install dependencies
   .\vcpkg install suitesparse:x64-windows
   
   # Build BFF
   cd path\to\bff-source
   mkdir build
   cd build
   cmake .. -G "Visual Studio 17 2022" -A x64 ^
     -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake ^
     -DBUILD_GUI=OFF
   cmake --build . --config Release --target bff-command-line
   
   # Copy to project
   copy Release\bff-command-line.exe ..\..\bff\
   ```

3. **Run application:**
   ```bash
   python main.py
   ```

4. **Build standalone executable:**
   ```bash
   pyinstaller BFF-Fabric-Flattener.spec
   # Output will be in dist/BFF-Fabric-Flattener.exe
   ```

### Using GitHub Actions (Automated)

1. **Push code to GitHub:**
   ```bash
   git push origin main
   ```

2. **GitHub Actions will automatically:**
   - Build BFF from source
   - Package the GUI application
   - Create artifacts

3. **Create a release:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Download from Releases page:**
   - Go to your repository's Releases page
   - Download `BFF-Fabric-Flattener-Windows.zip`
   - Extract and run!

## Development Workflow

### Making Changes

1. **Edit code:**
   ```bash
   # Make changes to main.py or other files
   ```

2. **Test locally:**
   ```bash
   python main.py
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

4. **GitHub Actions builds automatically:**
   - Check Actions tab for build status
   - Download artifacts for testing

### Creating Releases

1. **Update version:**
   - Edit version string in `main.py`
   - Update `README.md` changelog

2. **Create and push tag:**
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

3. **GitHub Actions creates release:**
   - Automatically builds
   - Creates GitHub Release
   - Attaches Windows ZIP file

## Troubleshooting Build Issues

### BFF Build Fails

**Problem:** CMake can't find SuiteSparse

**Solution:**
```bash
# Ensure vcpkg is properly installed
vcpkg integrate install
vcpkg install suitesparse:x64-windows
```

### PyInstaller Issues

**Problem:** Missing dependencies in executable

**Solution:** Add to `BFF-Fabric-Flattener.spec`:
```python
hiddenimports=['missing_module_name']
```

**Problem:** BFF executable not found in bundle

**Solution:** Check the `datas` section includes:
```python
datas=[('bff/bff-command-line.exe', 'bff')]
```

### GitHub Actions Fails

**Problem:** Build times out

**Solution:** Increase timeout in workflow:
```yaml
jobs:
  build-bff:
    timeout-minutes: 60
```

**Problem:** vcpkg install fails

**Solution:** Use pre-built binaries or cache vcpkg:
```yaml
- name: Cache vcpkg
  uses: actions/cache@v3
  with:
    path: C:/vcpkg
    key: ${{ runner.os }}-vcpkg
```

## Optional Enhancements

### Add Application Icon

1. Create `icon.ico` (256x256 recommended)
2. Place in root directory
3. PyInstaller will automatically use it

### Add Sample Models

```
samples/
├── sphere.obj
├── bunny.obj
└── torus.obj
```

### Add Tests

```
tests/
├── test_bff_processing.py
└── test_svg_export.py
```

## Resources

- **BFF Source:** https://github.com/GeometryCollective/boundary-first-flattening
- **PyQt6 Docs:** https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **PyInstaller Manual:** https://pyinstaller.org/en/stable/
- **GitHub Actions:** https://docs.github.com/en/actions
