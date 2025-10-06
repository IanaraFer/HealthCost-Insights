import webbrowser
import os

# Get the full path to the HTML file
html_file = os.path.join(os.getcwd(), "HealthCost_Insights_Complete_Project.html")

# Open in default browser
webbrowser.open('file://' + html_file)

print("✅ HTML file opened in your default browser!")
print("📄 To export to PDF:")
print("   1. Press Ctrl+P (Print)")
print("   2. Select 'Save as PDF' as destination")
print("   3. Adjust settings if needed")
print("   4. Click 'Save'")
print("")
print(f"📁 HTML file location: {html_file}")