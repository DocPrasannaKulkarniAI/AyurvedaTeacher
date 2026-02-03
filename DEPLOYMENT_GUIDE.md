# 🚀 STREAMLIT CLOUD DEPLOYMENT GUIDE

## ✅ **SOLUTION FOR YOUR ERROR:**

Your app shows "No subjects in database" because the database is empty on Streamlit Cloud.

---

## 📋 **DEPLOYMENT STEPS:**

### **Option 1: Upload Excel File (Recommended)**

1. **Add Excel file to your GitHub repo:**
   ```
   your-repo/
   ├── app.py
   ├── import_data.py
   ├── requirements.txt
   ├── LMS_All_Sheets_Combined.xlsx  ← Add this!
   └── modules/
       └── ...
   ```

2. **Commit and push:**
   ```bash
   git add LMS_All_Sheets_Combined.xlsx
   git commit -m "Add Excel data file"
   git push
   ```

3. **Redeploy on Streamlit Cloud:**
   - App will auto-import data on first run
   - Database gets created automatically

### **Option 2: Include Pre-populated Database**

1. **On local machine, create database:**
   ```powershell
   python import_data.py
   # Creates: data/ayurveda_syllabus.db
   ```

2. **Add to GitHub:**
   ```bash
   git add data/ayurveda_syllabus.db
   git commit -m "Add pre-populated database"
   git push
   ```

3. **Update `.gitignore`** - Make sure it doesn't exclude `.db` files:
   ```
   # Comment out or remove:
   # *.db
   # data/*.db
   ```

---

## 📁 **REQUIRED FILES FOR DEPLOYMENT:**

### **Minimum Files:**
```
your-repo/
├── app.py
├── requirements.txt
├── LMS_All_Sheets_Combined.xlsx  ← REQUIRED!
├── import_data.py
└── modules/
    ├── __init__.py
    ├── database.py
    ├── dashboard.py
    ├── slo_browser_enhanced.py
    ├── planned_slos.py
    ├── teaching_diary.py
    ├── coverage.py
    ├── monthly_reports.py
    ├── reports.py
    └── abbreviations.py
```

### **Optional but Recommended:**
```
├── data/
│   └── ayurveda_syllabus.db  ← Pre-populated database
└── README.md
```

---

## ⚙️ **STREAMLIT CLOUD SETTINGS:**

### **In Streamlit Cloud Dashboard:**

1. **Python version:** 3.9 or higher

2. **Main file:** `app.py`

3. **Requirements:** Make sure `requirements.txt` has:
   ```
   streamlit
   pandas
   openpyxl
   ```

4. **Secrets:** Not needed for this app

---

## 🔧 **TROUBLESHOOTING:**

### **Error: "No subjects in database"**
**Solution:** Upload `LMS_All_Sheets_Combined.xlsx` to your repo

### **Error: "Excel file not found"**
**Solution:** Make sure file is in repo root, not in a subfolder

### **Error: "Permission denied"**
**Solution:** Streamlit Cloud has limited permissions. Use Option 1 (Excel upload) instead of Option 2 (database file)

### **Import takes too long**
**Solution:** Use Option 2 - upload pre-populated database instead of Excel

---

## 🎯 **RECOMMENDED DEPLOYMENT APPROACH:**

### **Best Practice:**

1. **Locally:**
   ```powershell
   # Import data
   python import_data.py
   
   # Test app
   streamlit run app.py
   
   # If works, commit everything
   ```

2. **Add to GitHub:**
   ```bash
   # Add Excel file
   git add LMS_All_Sheets_Combined.xlsx
   
   # Add database (optional but faster)
   git add data/ayurveda_syllabus.db
   
   # Commit
   git commit -m "Ready for deployment"
   git push
   ```

3. **Deploy on Streamlit Cloud:**
   - Connect your GitHub repo
   - Set main file: `app.py`
   - Deploy!

---

## ✅ **WHAT WILL HAPPEN:**

### **First Deploy (with Excel):**
```
1. User visits site
2. App detects empty database
3. Shows: "🔄 First-time setup: Importing data..."
4. Imports all 7,197 SLOs
5. Shows login screen
6. Ready to use!
```

### **Subsequent Visits:**
```
1. Database already exists
2. Goes straight to login
3. Fast loading!
```

---

## 📊 **FILE SIZES:**

```
LMS_All_Sheets_Combined.xlsx  ~2 MB
ayurveda_syllabus.db          ~5 MB

GitHub free tier supports up to 100 MB per file
Both files are well within limits! ✅
```

---

## 🚀 **QUICK FIX FOR YOUR CURRENT DEPLOYMENT:**

1. **Download your Excel file**
2. **Go to your GitHub repo**
3. **Click "Add file" → "Upload files"**
4. **Upload `LMS_All_Sheets_Combined.xlsx`**
5. **Commit changes**
6. **Streamlit Cloud will auto-redeploy**
7. **Visit your app again - data will import!**

---

## 💡 **ALTERNATIVE: Use Demo Data**

If you can't upload the Excel file, I can create a small demo dataset:

```python
# In import_data.py, add demo data function
def create_demo_data(db):
    # Creates 50 demo SLOs for testing
    # Perfect for demo deployments
```

Let me know if you need this!

---

**Upload Excel → Redeploy → Works!** 🎉
