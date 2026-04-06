"""Fix the missing backticks in the DDS implementation paragraph."""
content = open("wiki/Texture-Formats.md", encoding="utf-8").read()

old_para = (
    "PyKotor reads both variants via [TPCDDSReader.load L191+]"
    "(https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/"
    "Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py#L191) "
    "(class [TPCDDSReader L49+]"
    "(https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/"
    "Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py#L49)) "
    "and writes standard DDS via [TPCDDSWriter L351+]"
    "(https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/"
    "Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py#L351), "
    "routed through [tpc_auto.py]"
    "(https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/"
    "resource/formats/tpc/tpc_auto.py) via ResourceType.DDS detection. "
    "The same structure is decoded by [xoreos src/graphics/images/dds.cpp]"
    "(https://github.com/xoreos/xoreos/blob/master/src/graphics/images/dds.cpp) "
    "(engine, both variants) and [xoreos-tools src/images/dds.cpp]"
    "(https://github.com/xoreos/xoreos-tools/blob/master/src/images/dds.cpp) "
    "(command-line conversion). Reone has no standalone DDS reader and loads all textures through "
    "[TPC via TpcReader::load L32+]"
    "(https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/"
    "src/libs/graphics/format/tpcreader.cpp#L32). "
    "KotOR.js follows the TPC path via [TPCObject.ts]"
    "(https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TPCObject.ts) "
    "and [TextureLoader.ts]"
    "(https://github.com/KobaltBlu/KotOR.js/blob/master/src/loaders/TextureLoader.ts); "
    "Kotor.NET manages textures under [Kotor.NET/Formats/KotorTPC/]"
    "(https://github.com/NickHugi/Kotor.NET/tree/master/Kotor.NET/Formats/KotorTPC) "
    "with no separate DDS project. DDS is primarily a tool interchange format \u2014 "
    "KotOR ships textures as [TPC](Texture-Formats#tpc) \u2014 but DDS files in the override "
    "folder are fully supported. For mod workflows see "
    "[HoloPatcher for mod developers](HoloPatcher#mod-developers); "
    "related formats: [TPC](Texture-Formats#tpc), [TXI](Texture-Formats#txi)."
)

new_para = (
    "PyKotor reads both variants via [`TPCDDSReader.load` L191+]"
    "(https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/"
    "Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py#L191) "
    "(class [`TPCDDSReader` L49+]"
    "(https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/"
    "Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py#L49)) "
    "and writes standard DDS via [`TPCDDSWriter` L351+]"
    "(https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/"
    "Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py#L351), "
    "routed through [`tpc_auto.py`]"
    "(https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/"
    "resource/formats/tpc/tpc_auto.py) via `ResourceType.DDS` detection. "
    "The same structure is decoded by [xoreos `src/graphics/images/dds.cpp`]"
    "(https://github.com/xoreos/xoreos/blob/master/src/graphics/images/dds.cpp) "
    "(engine, both variants) and [xoreos-tools `src/images/dds.cpp`]"
    "(https://github.com/xoreos/xoreos-tools/blob/master/src/images/dds.cpp) "
    "(command-line conversion). Reone has no standalone DDS reader and loads all textures through "
    "[TPC via `TpcReader::load` L32+]"
    "(https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/"
    "src/libs/graphics/format/tpcreader.cpp#L32). "
    "KotOR.js follows the TPC path via [`TPCObject.ts`]"
    "(https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TPCObject.ts) "
    "and [`TextureLoader.ts`]"
    "(https://github.com/KobaltBlu/KotOR.js/blob/master/src/loaders/TextureLoader.ts); "
    "Kotor.NET manages textures under [`Kotor.NET/Formats/KotorTPC/`]"
    "(https://github.com/NickHugi/Kotor.NET/tree/master/Kotor.NET/Formats/KotorTPC) "
    "with no separate DDS project. DDS is primarily a tool interchange format \u2014 "
    "KotOR ships textures as [TPC](Texture-Formats#tpc) \u2014 but DDS files in the override "
    "folder are fully supported. For mod workflows see "
    "[HoloPatcher for mod developers](HoloPatcher#mod-developers); "
    "related formats: [TPC](Texture-Formats#tpc), [TXI](Texture-Formats#txi)."
)

if old_para in content:
    new_content = content.replace(old_para, new_para, 1)
    open("wiki/Texture-Formats.md", "w", encoding="utf-8").write(new_content)
    print("Fixed!")
    print("Backtick check:", "`TPCDDSReader.load`" in new_content)
else:
    print("Not found - printing current paragraph start:")
    idx = content.find("PyKotor reads both variants")
    print(repr(content[idx:idx+500]))
