content = open("wiki/Texture-Formats.md", encoding="utf-8").read()

idx1 = content.find("PyKotor reads both variants via")
idx2 = content.find("### Standard DDS (DX7+ container)", idx1)
old_para = content[idx1:idx2].rstrip()

# Build correct new paragraph by replacing \` with ` and \\ with nothing extra
# The issue: the old paragraph has \` where it should have just `
new_para = old_para.replace("\\`", "`")

print("Changes made:", old_para != new_para)
print("Sample:", repr(new_para[:200]))

new_content = content[:idx1] + new_para + "\n\n" + content[idx2:]
open("wiki/Texture-Formats.md", "w", encoding="utf-8").write(new_content)
print("backtick check:", "`TPCDDSReader.load`" in new_content)
print("done, len:", len(new_content))
