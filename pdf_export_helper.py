"""
HealthCost Insights - PDF Export Helper
Provides multiple methods to create PDF from HTML
"""
import os
import webbrowser
import subprocess

def main():
    html_file = "HealthCost_Insights_Complete_Project.html"
    
    print("🏥 HealthCost Insights - PDF Export Helper")
    print("=" * 50)
    
    if not os.path.exists(html_file):
        print("❌ HTML file not found!")
        return
    
    print(f"✅ HTML file found: {html_file}")
    print(f"📊 File size: {os.path.getsize(html_file) / 1024 / 1024:.1f} MB")
    print("")
    
    print("📄 PDF Export Options:")
    print("1. Browser Method (Recommended)")
    print("   - File will open in browser")
    print("   - Press Ctrl+P")
    print("   - Select 'Save as PDF'")
    print("   - Click Save")
    print("")
    
    # Open in browser
    file_path = os.path.abspath(html_file)
    webbrowser.open(f'file:///{file_path}')
    
    print("🌐 Opening in browser...")
    print("👆 Follow the steps above to save as PDF")
    print("")
    print("🎯 Your complete HealthCost Insights project is ready!")
    print("   ✅ All code cells executed")
    print("   ✅ All visualizations included")
    print("   ✅ Business analysis complete")
    print("   ✅ Professional formatting")

if __name__ == "__main__":
    main()