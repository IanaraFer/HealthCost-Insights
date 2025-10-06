"""
PDF Export Script for HealthCost Insights Project
Converts Jupyter notebook to PDF with code and outputs
"""

import subprocess
import sys
import os
from pathlib import Path

def install_required_packages():
    """Install required packages for PDF export"""
    required_packages = [
        'nbconvert',
        'pandoc',
        'xelatex',  # For LaTeX PDF generation
    ]
    
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Could not install {package} via pip")

def export_notebook_to_pdf(notebook_path, output_path=None):
    """
    Export Jupyter notebook to PDF using nbconvert
    """
    if output_path is None:
        output_path = notebook_path.replace('.ipynb', '.pdf')
    
    try:
        # Method 1: Try direct PDF conversion
        cmd = [
            'jupyter', 'nbconvert',
            '--to', 'pdf',
            '--execute',  # Re-execute cells to ensure outputs
            '--allow-errors',  # Continue even if there are errors
            notebook_path,
            '--output', output_path
        ]
        
        print(f"🔄 Converting {notebook_path} to PDF...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully exported to {output_path}")
            return True
        else:
            print(f"❌ PDF conversion failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️ jupyter nbconvert not found. Trying alternative method...")
        return export_via_html(notebook_path, output_path)

def export_via_html(notebook_path, output_path):
    """
    Alternative method: Convert to HTML first, then to PDF
    """
    try:
        # Convert to HTML first
        html_path = notebook_path.replace('.ipynb', '.html')
        
        cmd_html = [
            'jupyter', 'nbconvert',
            '--to', 'html',
            '--execute',
            '--allow-errors',
            notebook_path,
            '--output', html_path
        ]
        
        print(f"🔄 Converting to HTML first...")
        result = subprocess.run(cmd_html, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ HTML conversion successful: {html_path}")
            print(f"📄 You can now manually convert {html_path} to PDF using:")
            print(f"   - Print to PDF from your browser")
            print(f"   - Use wkhtmltopdf: wkhtmltopdf {html_path} {output_path}")
            return True
        else:
            print(f"❌ HTML conversion failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error in HTML conversion: {e}")
        return False

def main():
    """Main export function"""
    print("📄 HealthCost Insights - PDF Export Tool")
    print("=" * 60)
    
    # Path to the notebook
    notebook_path = "HealthCost_Insights_Complete_Export.ipynb"
    
    if not os.path.exists(notebook_path):
        print(f"❌ Notebook not found: {notebook_path}")
        print("Please ensure the notebook exists in the current directory.")
        return
    
    # Check if jupyter is available
    try:
        subprocess.run(['jupyter', '--version'], capture_output=True, check=True)
        print("✅ Jupyter found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Jupyter not found. Please install Jupyter:")
        print("   pip install jupyter")
        return
    
    # Try to export
    success = export_notebook_to_pdf(notebook_path)
    
    if success:
        print("\n🎉 Export completed successfully!")
        print(f"📄 Your PDF is ready for sharing and presentation.")
    else:
        print("\n⚠️ Direct PDF export failed. Here are alternative options:")
        print("\n📋 MANUAL EXPORT OPTIONS:")
        print("1. Open the notebook in Jupyter:")
        print("   jupyter notebook HealthCost_Insights_Complete_Export.ipynb")
        print("2. Go to File > Download as > PDF via LaTeX (.pdf)")
        print("3. Or use File > Print Preview and print to PDF")
        print("\n📋 BROWSER EXPORT:")
        print("1. Open the generated HTML file in your browser")
        print("2. Press Ctrl+P (or Cmd+P on Mac)")
        print("3. Select 'Save as PDF' as destination")
        print("4. Adjust settings for best quality")
        
        # Generate HTML as backup
        export_via_html(notebook_path, notebook_path.replace('.ipynb', '.pdf'))

if __name__ == "__main__":
    main()