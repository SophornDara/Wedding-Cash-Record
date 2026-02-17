# Quick Start Guide - Khmer Font Fix

# របៀបដោះស្រាយបញ្ហាពុម្ពអក្សរខ្មែរ

## ✅ What Was Fixed:

1. **Automatic Font Detection** - The app now automatically finds and uses available Khmer fonts
2. **Font Fallback System** - If preferred font isn't found, it tries other Khmer fonts
3. **Custom Message Boxes** - All dialogs now properly display Khmer text
4. **Improved Treeview** - Better font rendering for the guest list table
5. **Taller Row Heights** - Accommodates Khmer vowels and diacritics properly

## 🚀 Quick Steps to Test:

### Step 1: Check if Khmer fonts are installed

```bash
python test_fonts.py
```

This will show you which Khmer fonts are available on your system.

### Step 2: Install Khmer fonts (if needed)

**If no fonts were found:**

1. See `KHMER_FONT_GUIDE.md` for detailed instructions
2. Quick method: Install Windows Khmer language pack
   - Windows Settings → Time & Language → Language
   - Add "Khmer (Cambodia)"
   - Windows will auto-install Khmer fonts

### Step 3: Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the application

```bash
python main.py
```

## ✓ Expected Results:

If everything is working correctly, you should see:

- **Sidebar**: Clear Khmer text for labels:
  - បញ្ចូលព័ត៌មាន (Enter Information)
  - ឈ្មោះភ្ញៀវ (Guest Name)
  - ប្រាក់រៀល (KHR)
  - ប្រាក់ដុល្លារ (USD)
  - រក្សាទុក (Save)

- **Table Headers**:
  - ល.រ (ID)
  - ឈ្មោះ (Name)
  - ប្រាក់រៀល (KHR)
  - ប្រាក់ដុល្លារ (USD)
  - អាសយដ្ឋាន (Address)

- **Message Dialogs**: Properly formatted Khmer text with custom styling

## ⚠️ Troubleshooting:

### Problem: Still seeing boxes (□□□) instead of Khmer text

**Solutions:**

1. Run `python test_fonts.py` to check available fonts
2. Install Khmer fonts (see KHMER_FONT_GUIDE.md)
3. **Restart your computer** after installing fonts
4. Try running the app again

### Problem: Some vowels are cut off or misaligned

**Solutions:**

1. This is fixed with increased row height in the new code
2. If still occurring, try a different Khmer font:
   - Edit `.env` file (create from `.env.example`)
   - Change `FONT_NAME=Khmer OS Battambang`
   - Try different fonts from the list in `.env.example`

### Problem: "Module not found" error

**Solutions:**

```bash
# Install missing dependencies
pip install customtkinter pandas openpyxl python-dotenv

# Or install all at once
pip install -r requirements.txt
```

## 📝 Configuration (Optional):

Create a `.env` file to customize settings:

```bash
# Copy the example file
copy .env.example .env
```

Then edit `.env`:

```env
DB_NAME=wedding_data.db
APP_TITLE=Wedding Manager
FONT_NAME=Khmer OS Siemreap
FONT_SIZE=12
```

## 🎨 Features of the Fixed Version:

1. **Smart Font Detection**:
   - Automatically finds best available Khmer font
   - Falls back to alternatives if preferred font missing
   - Shows which font is being used (run test_fonts.py)

2. **Enhanced UI**:
   - Custom dialogs with Khmer font support
   - Improved table rendering
   - Better spacing for Khmer characters
   - Proper row heights for vowels and subscripts

3. **Better Error Handling**:
   - Bilingual messages (Khmer + English)
   - Clear, readable dialogs
   - Proper font rendering in all UI elements

## 📞 Need Help?

1. Run `python test_fonts.py` first to diagnose font issues
2. Check `KHMER_FONT_GUIDE.md` for font installation
3. See `README.md` for full documentation
4. Verify Python version: `python --version` (need 3.8+)

## ✨ Testing the Application:

Try entering this test data:

- **Name**: វុត្ថា (Vutha)
- **KHR**: 100000
- **USD**: 25
- **Address**: ភ្នំពេញ (Phnom Penh)

If you can see all Khmer characters clearly, the fix is working! ✓
