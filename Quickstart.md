# Quick Start Guide

Get up and running with BFF Fabric Flattener in 5 minutes!

## Option 1: Use Pre-built Release (Easiest) ⚡

1. **Download the latest release:**
   - Go to the [Releases page](https://github.com/YOUR_USERNAME/bff-fabric-flattener/releases)
   - Download `BFF-Fabric-Flattener-Windows.zip`

2. **Extract and run:**
   - Extract the ZIP file
   - Double-click `BFF-Fabric-Flattener.exe`
   - That's it! 🎉

## Option 2: Build Yourself 🔨

### Prerequisites Checklist

- [ ] Windows 10/11
- [ ] Python 3.11+ ([Download](https://www.python.org/downloads/))
- [ ] Git ([Download](https://git-scm.com/downloads))
- [ ] Visual Studio 2022 Community ([Download](https://visualstudio.microsoft.com/downloads/))
  - Install "Desktop development with C++" workload

### Step-by-Step Build

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/bff-fabric-flattener.git
cd bff-fabric-flattener

# 2. Create Python virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install vcpkg (package manager)
git clone https://github.com/Microsoft/vcpkg.git C:\vcpkg
cd C:\vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg integrate install

# 5. Install SuiteSparse (BFF dependency)
.\vcpkg install suitesparse:x64-windows

# 6. Build BFF
cd path\to\bff-fabric-flattener
git clone --recursive https://github.com/GeometryCollective/boundary-first-flattening.git bff-source
cd bff-source
mkdir build
cd build

cmake .. -G "Visual Studio 17 2022" -A x64 ^
  -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake ^
  -DBUILD_GUI=OFF

cmake --build . --config Release --target bff-command-line

# 7. Copy BFF executable to project
mkdir ..\..\bff
copy Release\bff-command-line.exe ..\..\bff\

# 8. Return to project root and test
cd ..\..
python main.py
```

**Success!** The GUI should open. You can now use it directly or build a standalone executable:

```bash
# Optional: Build standalone .exe
pyinstaller BFF-Fabric-Flattener.spec
# Find the .exe in dist/
```

## Option 3: Use GitHub Actions (Fully Automated) 🤖

1. **Fork this repository** on GitHub

2. **Enable GitHub Actions:**
   - Go to Actions tab
   - Click "I understand my workflows, go ahead and enable them"

3. **Make a small change and push:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/bff-fabric-flattener.git
   cd bff-fabric-flattener
   # Edit README.md or any file
   git commit -am "Trigger build"
   git push
   ```

4. **Wait for build to complete** (~10-15 minutes)

5. **Download artifacts:**
   - Go to Actions tab
   - Click on the latest workflow run
   - Download `windows-release` artifact

**Create a release** by pushing a tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will automatically create a release!

## First Usage 🎨

1. **Launch the application:**
   - Run `BFF-Fabric-Flattener.exe` or `python main.py`

2. **Load a 3D model:**
   - Click "Browse" under "Input 3D Model"
   - Select an `.obj` file
   - Try with a simple mesh first (sphere, torus)

3. **Process:**
   - Click "Process Model" button
   - Wait for completion message

4. **Find your outputs:**
   - `yourmodel_flattened.obj` - Flattened mesh with UV coordinates
   - `yourmodel_flattened.svg` - Vector pattern for printing

## Testing Your Setup 🧪

### Download a Test Model

**Simple Sphere (recommended for first test):**
```bash
# Create a simple sphere in Blender:
# 1. Open Blender
# 2. Select default cube, delete it
# 3. Add > Mesh > UV Sphere
# 4. File > Export > Wavefront (.obj)
# 5. Save as "test-sphere.obj"
```

Or download test models from:
- [Free3D](https://free3d.com/)
- [TurboSquid Free](https://www.turbosquid.com/Search/3D-Models/free)
- [Thingiverse](https://www.thingiverse.com/)

### Expected Results

**Good flattening indicators:**
- ✅ SVG file is created
- ✅ Pattern looks reasonable (not overlapping)
- ✅ No error messages in log
- ✅ Process completes in seconds

**Troubleshooting signs:**
- ❌ "BFF executable not found" → Check `bff/` folder has the `.exe`
- ❌ "Processing failed" → Try enabling "Auto-cut mesh"
- ❌ Long processing time → Model might be too complex

## Common Issues & Fixes 🔧

### "BFF executable not found"

**Cause:** The `bff-command-line.exe` is not in the right location.

**Fix:**
```bash
# Ensure this file exists:
bff-fabric-flattener\bff\bff-command-line.exe

# If not, rebuild BFF (see step 6-7 above)
```

### "ModuleNotFoundError: No module named 'PyQt6'"

**Cause:** Python dependencies not installed.

**Fix:**
```bash
pip install -r requirements.txt
```

### BFF Build Errors

**Cause:** Missing Visual Studio or CMake.

**Fix:**
1. Install Visual Studio 2022 with C++ workload
2. CMake is included with VS, or [download separately](https://cmake.org/download/)
3. Restart your terminal

### "Access Denied" when running .exe

**Cause:** Windows Defender/Antivirus blocking unsigned executable.

**Fix:**
1. Right-click the .exe → Properties
2. Check "Unblock" at the bottom
3. Click OK

Or add exclusion in Windows Security.

## Next Steps 📚

Once you have the basic setup working:

1. **Read the full README.md** for detailed documentation
2. **Experiment with options:**
   - Try cone singularities for better results
   - Test different models
3. **Learn about fabric printing:**
   - Check out [Nervous System's blog](https://n-e-r-v-o-u-s.com/blog/)
   - Research DTG (Direct-to-Garment) printing
4. **Contribute:**
   - Report bugs
   - Suggest features
   - Submit pull requests

## Getting Help 💬

- **Check the logs** - The application shows detailed progress
- **Read error messages** - They usually indicate the problem
- **GitHub Issues** - [Create an issue](https://github.com/YOUR_USERNAME/bff-fabric-flattener/issues)
- **BFF Documentation** - [Official docs](https://geometrycollective.github.io/boundary-first-flattening/)

## Success Checklist ✅

Before asking for help, verify:

- [ ] Python 3.11+ is installed (`python --version`)
- [ ] Dependencies are installed (`pip list | findstr PyQt6`)
- [ ] BFF executable exists in `bff/` folder
- [ ] You can run the GUI (`python main.py` works)
- [ ] Test model is valid OBJ format
- [ ] You're using a simple model for testing first

---

**Happy flattening!** 🎉

If this guide helped you, please ⭐ star the repository!
