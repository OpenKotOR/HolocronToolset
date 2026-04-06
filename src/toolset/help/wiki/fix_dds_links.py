"""Fix specific link labels in the DDS paragraph that are missing backticks."""
content = open("wiki/Texture-Formats.md", encoding="utf-8").read()

# Fix specific broken link labels (missing backticks, or tab-corrupted)
fixes = [
    ("[TPCDDSReader.load L191+]", "[`TPCDDSReader.load` L191+]"),
    ("[TPCDDSReader L49+]", "[`TPCDDSReader` L49+]"),
    ("[TPCDDSWriter L351+]", "[`TPCDDSWriter` L351+]"),
    ("[\tpc_auto.py]", "[`tpc_auto.py`]"),   # \t is a literal tab char here
]

changed = False
for old, new in fixes:
    if old in content:
        content = content.replace(old, new, 1)
        changed = True
        print(f"Fixed: {repr(old)} -> {repr(new)}")
    else:
        print(f"NOT FOUND: {repr(old)}")

if changed:
    open("wiki/Texture-Formats.md", "w", encoding="utf-8").write(content)
    print("File written.")
else:
    print("No changes made.")
