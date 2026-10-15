with open("calendar-lagna-moon-indicators.html", "r", encoding="utf-8") as f:
    text = f.read()

target1 = "return rightBarContent ? `<div style=\"position:absolute; left:2px; top:50%; transform:translateY(-50%); display:flex; flex-direction:column; gap:2px; z-index:10;\">${rightBarContent}</div>` : '';"
replacement1 = "return rightBarContent ? `<div style=\"position:absolute; right:2px; top:50%; transform:translateY(-50%); display:flex; flex-direction:column; gap:2px; z-index:10;\">${rightBarContent}</div>` : '';"

count = text.count(target1)
print("Found target1 count:", count)

if count == 2:
    new_text = text.replace(target1, replacement1)
    with open("calendar-lagna-moon-indicators.html", "w", encoding="utf-8") as f:
        f.write(new_text)
    print("Successfully replaced left:2px with right:2px for rightBarContent")
else:
    print("Count mismatch!")
