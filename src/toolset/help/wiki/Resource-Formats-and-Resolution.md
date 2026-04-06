# Resource formats and resolution

KotOR does not load files by extension alone. The runtime resolves a resource as a `(ResRef, type ID)` pair, so `foo.utc`, `foo.utp`, `foo.uti`, and `foo.tga` are four different resources even when they share the same base name. PyKotor's registry is the best current single-source summary because each `ResourceType` member carries the numeric ID, canonical extension, broad content family, and declared engine support rather than only a flat filename mapping [[`BiowareEngine`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L49-L67), [`ResourceTuple`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L147-L172), [`ResourceType`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L175-L209)].

This page is the wiki SSOT for KotOR-facing resource IDs, the Odyssey-specific extension block that older Aurora tables often omit, and the relationship between loose files, module capsules, and global archives. Community documentation and tool history line up with that model: Holowan-era install guidance distinguishes Override files, module files, lips, and TLK placement, while xoreos and related tooling treat KotOR resource handling as a typed, container-aware pipeline rather than a loose bag of files [[Darth333's install guide](https://www.lucasforumsarchive.com/thread/129789-guide-for-the-newbie-what-tools-do-i-need-to-mod-kotor-how-to-install-mods), [xoreos KotOR wiki page](https://wiki.xoreos.org/index.php?title=Knights_of_the_Old_Republic), [xoreos 0.0.6 release notes](https://xoreos.org/blog/2020/08/03/xoreos-0-dot-0-6-elanee-released/)]. For the broader prose on precedence, override behaviour, module capsules, KEY/BIF, and language IDs, see [Concepts](Concepts).

## Resource resolution order

Full prose (resource manager demands, KEY's role, override vs MOD/ERF/[RIM](Container-Formats#rim)): **[Concepts — Resource resolution order](Concepts#resource-resolution-order)**.

**Operational summary:**

1. Loose files in `Override` win first. That is why classic mod-install instructions tell users to drop most replacement assets there, and why collision-heavy mods break when they overwrite the same filename without a patcher [[Holowan install guide](https://www.lucasforumsarchive.com/thread/129789-guide-for-the-newbie-what-tools-do-i-need-to-mod-kotor-how-to-install-mods), [Holowan load-order thread](https://www.lucasforumsarchive.com/thread/206128-load-order)].
2. Module-local containers come next. KotOR commonly loads module data from [MOD](Container-Formats#erf), [ERF](Container-Formats#erf), or [RIM](Container-Formats#rim) capsules, and save-specific capsules can temporarily shadow shipped module resources when the game is working from save-state copies instead of pristine module assets [[Concepts](Concepts#resource-resolution-order), [`RIM`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L417-L419), [`MOD`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L249-L250), [`SAV`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L299-L300)].
3. Global shipped resources then fall back through [KEY](Container-Formats#key)/[BIF](Container-Formats#bif), which is why extraction tools and modding references treat KEY as the index and BIF as the payload store rather than two independent formats [[Container-Formats](Container-Formats#key), [`KEY`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L2110-L2110), [xoreos 0.0.6 release notes](https://xoreos.org/blog/2020/08/03/xoreos-0-dot-0-6-elanee-released/)].
4. `dialog.tlk` is resolved through its own string-reference path. Patchers therefore append StrRefs and then inject those numeric values into 2DA, GFF, SSF, or script data instead of shipping whole-table replacements [[Deadly Stream TSLPatcher page](https://deadlystream.com/files/file/1039-tsl-patcher-tlked-and-accessories/), [TSLPatcher TLKList Syntax](TSLPatcher-TLKList-Syntax)].

The practical modder rule that emerged from Holowan still holds: avoid blind overwrites, prefer data patching for shared files, and treat identical filenames in Override as a load-order conflict rather than a mergeable state [[Holowan load-order thread](https://www.lucasforumsarchive.com/thread/206128-load-order)].

## ResRef and resource type

**ResRef** is the base resource name. **Resource type** is the numeric discriminator that says whether that name is a creature template, placeable template, compiled script, model, texture metadata file, or something else entirely. KotOR resolves those two pieces together, so the type ID is not optional bookkeeping: it is part of the lookup key [[Concepts — ResRef](Concepts#resref-resource-reference), [`ResourceType`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L175-L209)].

PyKotor's registry is especially useful because it records more than ID and extension. Each row also carries a broad category, a `contents` family such as `binary`, `plaintext`, `gff`, `erf`, or `lips`, and a `supported_engines` tuple. That makes it possible to distinguish "valid KotOR runtime type", "shared BioWare heritage type", and "tooling-only or unknown-support helper" instead of collapsing them into one giant undifferentiated list [[`ResourceTuple`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L147-L172)].

Use the tables on this page with the following reading rules:

- **Type ID** is the canonical numeric value stored by containers and resource managers.
- **Contents** tells you the storage family, which matters for whether a file is raw binary, text, [GFF](GFF-File-Format)-backed, [ERF](Container-Formats#erf)-backed, or LIP-specific.
- **Engine support** should be read as "known/declared support in the registry", not "confirmed retail usage in every shipped title". Some entries survive in the registry because KotOR tooling inherits broader Aurora/Odyssey lineage [[`BiowareEngine`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L49-L67)].

**Language IDs** (`dialog.tlk`, localization): [Concepts — Language IDs](Concepts#language-ids-kotor).

## Resource Type Identifiers

KotOR uses the inherited Aurora `0x0000-0x0812` range plus an Odyssey-specific extension block beginning at `3000`. Older community tables often stop before that Odyssey block or describe some legacy IDs only as "unknown", even though modern code and tooling can now classify them more precisely [[`ResourceType`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L231-L238), [`ResourceType`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L411-L479)].

### Common KotOR resource types

| Resource | Type ID | Contents | Engine support | Typical use |
| -------- | ------- | -------- | -------------- | ----------- |
| [2DA](2DA-File-Format) | `0x07E1` | binary table | Aurora, Odyssey, Eclipse | Gameplay tables, progression data, spell rows, appearances, and shared configuration |
| [ARE](GFF-Module-and-Area#are) | `0x07DC` | GFF | Aurora, Odyssey | Area metadata |
| [DLG](GFF-Creature-and-Dialogue#dlg) | `0x07ED` | GFF | Aurora, Odyssey, Eclipse | Dialog trees and conversation state |
| [ERF](Container-Formats#erf) / [MOD](Container-Formats#erf) / [SAV](Container-Formats#erf) / [RIM](Container-Formats#rim) | `0x270D` / `0x07DB` / `0x0809` / `3002` | container | Aurora/Odyssey, Odyssey | Capsule-style module, save, and shipped-area containers |
| [GFF](GFF-File-Format) | `0x07F5` | GFF | Aurora, Odyssey, Eclipse | Structured binary payload family used by most UT*, DLG, GIT, IFO, JRL, GUI, and related resources |
| [GIT](GFF-Module-and-Area#git) / [IFO](GFF-Module-and-Area#ifo) | `0x07E7` / `0x07DE` | GFF | Aurora, Odyssey | Module instance state and module metadata |
| [LIP](Audio-and-Localization-Formats#lip) / `BIP` | `3004` / `3028` | lips | Odyssey | Lip-sync timing and related facial timing data |
| [LYT](Level-Layout-Formats#lyt) / [VIS](Level-Layout-Formats#vis) / [PTH](GFF-Spatial-Objects#pth) | `3000` / `3001` / `3003` | plaintext / plaintext / GFF | Odyssey | Area layout, room visibility, and path data |
| [MDL](MDL-MDX-File-Format) / [MDX](MDL-MDX-File-Format) | `0x07D2` / `3008` | binary | Aurora/Odyssey/Eclipse, Odyssey | Model hierarchy plus mesh-sidecar data |
| [NCS](NCS-File-Format) / [NSS](NSS-File-Format) | `0x07DA` / `0x07D9` | binary / plaintext | Aurora, Odyssey | Compiled and source NWScript |
| [SSF](Audio-and-Localization-Formats#ssf) / [TLK](Audio-and-Localization-Formats#tlk) | `0x080C` / `0x07E2` | binary | Aurora, Odyssey / Aurora, Odyssey, Eclipse | Soundset-to-StrRef mappings and localized talk table strings |
| [TPC](Texture-Formats#tpc) / [TGA](https://en.wikipedia.org/wiki/Truevision_TGA) / [DDS](Texture-Formats#dds) / [TXI](Texture-Formats#txi) | `3007` / `0x0003` / `0x07F1` / `0x07E6` | binary / binary / binary / plaintext | Odyssey / shared / shared / Aurora, Odyssey | Common texture payloads and texture metadata |
| [UTC](GFF-Creature-and-Dialogue#utc) / [UTI](GFF-Items-and-Economy#uti) / [UTP](GFF-Spatial-Objects#utp) / [UTD](GFF-Spatial-Objects#utd) / [UTM](GFF-Items-and-Economy#utm) / [UTW](GFF-Spatial-Objects#utw) | `0x07EB` / `0x07E9` / `0x07FC` / `0x07FA` / `0x0803` / `0x080A` | GFF | Aurora, Odyssey | Creature, item, placeable, door, merchant, and waypoint templates |
| [WOK](Level-Layout-Formats#bwm) / [DWK](Level-Layout-Formats#bwm) / [PWK](Level-Layout-Formats#bwm) / `BWM` | `0x07E0` / `0x0804` / `0x0805` / `3005` | binary | Aurora, Odyssey / Odyssey | Walkmesh family for areas, doors, placeables, and Odyssey binary walkmesh assets |

The practical split is simple: most modders live in GFF resources, 2DA tables, scripts, talk tables, and models/textures, while engine and tool authors also need the Odyssey-specific `3000+` block because that is where layout, visibility, binary walkmesh, texture-container, and MDX sidecar types are declared [[`ResourceType` 2000-2063 block](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L239-L307), [`ResourceType` 3000-3028 block](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L411-L479)].

### Odyssey extension block (`3000+`)

These IDs are the biggest omission in many older KotOR summaries because they sit outside the classic Aurora range. In practice they cover exactly the kinds of assets that make Odyssey areas, rooms, visibility, lips, and texture/model sidecars work.

| Extension | Type ID | Contents | Typical KotOR role |
| --------- | ------- | -------- | ------------------ |
| [LYT](Level-Layout-Formats#lyt) | `3000` | plaintext | Area room/layout mapping |
| [VIS](Level-Layout-Formats#vis) | `3001` | plaintext | Room-to-room visibility graph |
| [RIM](Container-Formats#rim) | `3002` | binary container | Odyssey area/archive container |
| [PTH](GFF-Spatial-Objects#pth) | `3003` | GFF | Path and waypoint-network data |
| [LIP](Audio-and-Localization-Formats#lip) | `3004` | lips | Lip-sync timing |
| `bwm` | `3005` | binary | Odyssey binary walkmesh |
| `txb` | `3006` | binary | Texture-related Odyssey helper type retained in the registry |
| [TPC](Texture-Formats#tpc) | `3007` | binary | Primary Odyssey texture container |
| [MDX](MDL-MDX-File-Format) | `3008` | binary | Model mesh/geometry sidecar |
| `rsv` / `sig` | `3009` / `3010` | binary | Reserved or presently-unused Odyssey IDs |
| `mab` | `3011` | binary | Material-related binary type |
| `qst2` / `sto` | `3012` / `3013` | GFF | Odyssey quest/store-adjacent data types retained in the registry |
| `hex` | `3015` | binary | Hex-grid related helper type |
| `mdx2` / `txb2` | `3016` / `3017` | binary | Secondary model/texture helper types |
| `fsm` / `art` / `amp` / `cwa` | `3022` / `3023` / `3024` / `3025` | binary / plaintext / binary / GFF | State-machine, area-environment, brightness, and crowd-attribute helpers |
| `bip` | `3028` | lips | Binary lip-sync companion type |

All of those entries are declared as Odyssey-supported in the current registry, even when only a smaller subset is encountered in normal KotOR mod distribution workflows [[`LYT` through `BIP`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L411-L479)].

### Legacy and cross-engine IDs that still matter in KotOR tooling

Some registry members survive because KotOR shares lineage with broader Aurora/Odyssey tooling, not because every title uses them equally. The most relevant examples are `BMU`, `MPG`, `WMA`, `WMV`, and `XMV` for audio/video payload families; `HAK` and `NWM` from Aurora container history; and `BIK` for Bink video. They are worth keeping documented because extraction tools, archive browsers, and cross-engine libraries need one registry that can reason about both KotOR and its neighboring BioWare formats [[`BMU`-`XMV`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L231-L238), [`HAK`-`BIK`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L303-L307), [xoreos 0.0.6 release notes](https://xoreos.org/blog/2020/08/03/xoreos-0-dot-0-6-elanee-released/)].

### Extended classic registry table

| Resource Name | Type ID | Description                                    |
| ------------- | ------- | ---------------------------------------------- |
| RES           | 0x0000  | Used for `.res` resources within the [save game containers](Container-Formats#erf)                     |
| BMP           | 0x0001  | Bitmap image                         |
| MVE           | 0x0002  | Movie/video file       Not used in *KotOR*                   |
| [TGA](https://en.wikipedia.org/wiki/Truevision_TGA)           | 0x0003  | TarGA image format                          |
| [WAV](Audio-and-Localization-Formats#wav)           | 0x0004  | Wave audio file (see [WAV File Format](Audio-and-Localization-Formats#wav)) |
| [INI](https://en.wikipedia.org/wiki/INI_file)           | 0x0007  | Configuration file (e.g., `swkotor.ini`, `swkotor2.ini`)                          |
| BMU           | 0x0008  | Odyssey audio payload family; TSL commonly treats these as music-like assets rather than generic unknown data [[`BMU`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L231)]                                |
| MPG           | 0x0009  | MPEG video/audio-adjacent payload retained in the Odyssey registry [[`MPG`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L232)]                            |
| [TXT](https://en.wikipedia.org/wiki/Text_file)           | 0x000A  | Text file                                  |
| WMA           | 0x000B  | Windows Media Audio; retained as an Odyssey-supported registry type [[`WMA`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L236)] |
| WMV           | 0x000C  | Windows Media Video; retained as an Odyssey-supported registry type [[`WMV`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L237)] |
| XMV           | 0x000D  | Xbox media/video type retained as an Odyssey-supported registry type [[`XMV`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L238)] |
| PLH           | 0x07D0  | *PLaceable Header* type.  Not used in *KotOR*                      |
| TEX           | 0x07D1  | Texture. Not used in *KotOR*                      |
| [MDL](MDL-MDX-File-Format)           | 0x07D2  | 3D [model](MDL-MDX-File-Format) file (see [MDL/MDX File Format](MDL-MDX-File-Format))                                   |
| THG           | 0x07D3  | Unknown. Not used in *KotOR*                                |
| FNT           | 0x07D5  | Font file. Not used in *KotOR*                                  |
| Lua           | 0x07D7  | Lua script. Not used in *KotOR*                             |
| SLT           | 0x07D8  | Unknown. Not used in *KotOR*                               |
| [NSS](NSS-File-Format)           | 0x07D9  | *NWScript* source code (see [NSS File Format](NSS-File-Format))                            |
| [NCS](NCS-File-Format)           | 0x07DA  | *Compiled NWScript* bytecode (see [NCS File Format](NCS-File-Format))                     |
| [MOD](Container-Formats#erf)           | 0x07DB  | [*Module* ERF archive/container](Container-Formats#erf)                         |
| [ARE](GFF-File-Format#are-area)           | 0x07DC  | *Area* definition (see [GFF-ARE](GFF-Module-and-Area#are))                                 |
| SET           | 0x07DD  | Unknown.  Not used in *KotOR*                               |
| [IFO](GFF-File-Format#ifo-module-info)           | 0x07DE  | *Module* InFOrmation (see [GFF-IFO](GFF-Module-and-Area#ifo))                              |
| BIC           | 0x07DF  | BlueprInt Creature. *KotOR* supports these but nobody uses them, use [UTC](GFF-Creature-and-Dialogue#utc) instead.                  |
| [WOK](Level-Layout-Formats#bwm)           | 0x07E0  | *Walkmesh* (see [BWM File Format](Level-Layout-Formats#bwm))                                |
| [2DA](2DA-File-Format)           | 0x07E1  | *Two-Dimensional Array* data (see [2DA File Format](2DA-File-Format))                      |
| [TLK](Audio-and-Localization-Formats#tlk)           | 0x07E2  | *Talk Table* (Localized Strings, see [TLK File Format](Audio-and-Localization-Formats#tlk))                 |
| [TXI](Texture-Formats#txi)           | 0x07E6  | [TeXture Information](Texture-Formats#txi)                            |
| [GIT](GFF-File-Format#git-game-instance-template)           | 0x07E7  | [Game Instance Template](GFF-File-Format#git-game-instance-template) (see [GFF-GIT](GFF-Module-and-Area#git))                          |
| BTI           | 0x07E8  | Blueprint Template Item. *KotOR* supports these but nobody uses them, use [UTI](GFF-Items-and-Economy#uti) instead.                 |
| [UTI](GFF-File-Format#uti-item)           | 0x07E9  | [item templates](GFF-File-Format#uti-item) (see [GFF-UTI](GFF-Items-and-Economy#uti))                                   |
| BTC           | 0x07EA  | Blueprint Template Creature. *KotOR* supports these but nobody uses them, use [UTC](GFF-Creature-and-Dialogue#utc) instead.                |
| [UTC](GFF-File-Format#utc-creature)           | 0x07EB  | [Creature Template](GFF-File-Format#utc-creature) (see [GFF-UTC](GFF-Creature-and-Dialogue#utc))                               |
| [DLG](GFF-File-Format#dlg-dialogue)           | 0x07ED  | Dialogue/conversation (see [GFF-DLG](GFF-Creature-and-Dialogue#dlg))                           |
| [ITP](Bioware-Aurora-Module-and-Area#paletteitp)           | 0x07EE  | *ITP* format (see [Bioware-Aurora-PaletteITP](Bioware-Aurora-Module-and-Area#paletteitp)).                         |
| BTT           | 0x07EF  | *Blueprint Template Trigger*. *KotOR* supports these but nobody uses them, use [UTT](GFF-Spatial-Objects#utt) instead.                 |
| [UTT](GFF-File-Format#utt-trigger)           | 0x07F0  | *Trigger Template* (see [GFF-UTT](GFF-Spatial-Objects#utt)).                                |
| DDS           | 0x07F1  | *DirectDraw Surface Texture* (see [DDS File Format](Texture-Formats#dds)).                                |
| [UTS](GFF-File-Format#uts-sound)           | 0x07F3  | *Sound Template* (see [GFF-UTS](GFF-Spatial-Objects#uts)).                                |
| LTR           | 0x07F4  | *Letter Format* (see [LTR File Format](LTR-File-Format)). Not used in *KotOR*                                |
| [GFF](GFF-File-Format)           | 0x07F5  | Generic file format (container, see [GFF File Format](GFF-File-Format))                 |
| [FAC](GFF-File-Format#fac-faction)           | 0x07F6  | Faction                               |
| BTE           | 0x07F7  | Blueprint encounter                   |
| [UTE](GFF-File-Format#ute-encounter)           | 0x07F8  | [encounter template](GFF-File-Format#ute-encounter) (see [GFF-UTE](GFF-Spatial-Objects#ute))                              |
| BTD           | 0x07F9  | Blueprint door    Not used in *KotOR*     |
| [UTD](GFF-File-Format#utd-door)           | 0x07FA  | [door templates](GFF-File-Format#utd-door) (see [GFF-UTD](GFF-Spatial-Objects#utd))                                   |
| BTP           | 0x07FB  | Blueprint placeable   Not used in *KotOR*  |
| [UTP](GFF-File-Format#utp-placeable)           | 0x07FC  | [placeable templates](GFF-File-Format#utp-placeable) (see [GFF-UTP](GFF-Spatial-Objects#utp))                              |
| DTF           | 0x07FD  | Unknown  Not used in *KotOR*                                |
| GIC           | 0x07FE  | Unknown  Not used in *KotOR*                                |
| [GUI](GFF-File-Format#gui-graphical-user-interface)           | 0x07FF  | User interface definition (see [GFF-GUI](GFF-GUI))                       |
| CSS           | 0x0800  | Unknown  Not used in *KotOR*                                |
| CCS           | 0x0801  | Unknown  Not used in *KotOR*                                |
| BTM           | 0x0802  | Blueprint merchant.  *KotOR* supports these but nobody uses them, use [UTM](GFF-Items-and-Economy#utm) instead.              |
| [UTM](GFF-File-Format#utm-merchant)           | 0x0803  | [Merchant/store template](GFF-File-Format#utm-merchant) (see [GFF-UTM](GFF-Items-and-Economy#utm))                         |
| [DWK](Level-Layout-Formats#bwm)           | 0x0804  | [Door walkmesh](Level-Layout-Formats#bwm) (see [BWM File Format](Level-Layout-Formats#bwm))                                |
| [PWK](Level-Layout-Formats#bwm)           | 0x0805  | [Placeable walkmesh](Level-Layout-Formats#bwm) (see [BWM File Format](Level-Layout-Formats#bwm))                                |
| BTG           | 0x0806  | Blueprint trigger  Not used in *KotOR*       |
| UTG           | 0x0807  | Unknown            Not used in *KotOR*   |
| [JRL](GFF-File-Format#jrl-journal)           | 0x0808  | Journal/quest log (see [GFF-JRL](GFF-Items-and-Economy#jrl))                               |
| SAV           | 0x0809  | [Save game containers](Container-Formats#erf) (see [ERF File Format](Container-Formats#erf))                               |
| [UTW](GFF-File-Format#utw-waypoint)           | 0x080A  | [Waypoint Template](GFF-File-Format#utw-waypoint)                               |
| 4PC           | 0x080B  | Unknown  Not used in *KotOR*          |
| [SSF](Audio-and-Localization-Formats#ssf)           | 0x080C  | [Sound Set Files](Audio-and-Localization-Formats#ssf) (see [SSF File Format](Audio-and-Localization-Formats#ssf))                                  |
| HAK           | 0x080D  | Hak pak container. Not used in *KotOR*                                |
| NWM           | 0x080E  | *Neverwinter Nights* module (Not used in *KotOR*)                                 |
| BIK           | 0x080F  | BInK video format                                |
| PTM           | 0x0811  | Unknown       Not used in *KotOR*         |
| PTT           | 0x0812  | Unknown       Not used in *KotOR*         |
| [ERF](Container-Formats#erf)           | 0x270D  | [Encapsulated Resource File](Container-Formats#erf) (see [ERF File Format](Container-Formats#erf))                      |
| [BIF](Container-Formats#bif)           | 0x270E  | [Bioware Index File](Container-Formats#bif) (container, see [BIF File Format](Container-Formats#bif))                    |
| [KEY](Container-Formats#key)           | 0x270F  | [KEY](Container-Formats#key) table ([BIF](Container-Formats#bif) index, see [KEY File Format](Container-Formats#key))                          |

For KotOR specifically, do not stop reading at `0x270F`: the Odyssey-only `3000+` block above is part of the real resource landscape and includes some of the most important room/layout/visibility/model-sidecar types in the games [[`LYT` through `BIP`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py#L411-L479)].

## File format index

### File formats

- **[MDL/MDX File Format](MDL-MDX-File-Format)** ← Complete reference for 3D [model](MDL-MDX-File-Format) files
  - **[2DA File Format](2DA-File-Format)** ← Complete reference for Two-Dimensional array format (see also [Official Bioware 2DA Documentation](Bioware-Aurora-Core-Formats#2da)). All individual 2DA file documentation has been inlined into this document.
  - [acbonus.2da](2DA-File-Format#acbonus2da)
  - [ambientmusic.2da](2DA-File-Format#ambientmusic2da)
  - [ambientsound.2da](2DA-File-Format#ambientsound2da)
  - [ammunitiontypes.2da](2DA-File-Format#ammunitiontypes2da)
  - [animations.2da](2DA-File-Format#animations2da)
  - [appearance.2da](2DA-File-Format#appearance2da)
  - [appearancesndset.2da](2DA-File-Format#appearancesndset2da)
  - [baseitems.2da](2DA-File-Format#baseitems2da)
  - [bindablekeys.2da](2DA-File-Format#bindablekeys2da)
  - [bodybag.2da](2DA-File-Format#bodybag2da)
  - [camerastyle.2da](2DA-File-Format#camerastyle2da)
  - [classes.2da](2DA-File-Format#classes2da)
  - [classpowergain.2da](2DA-File-Format#classpowergain2da)
  - [combatanimations.2da](2DA-File-Format#combatanimations2da)
  - [creaturespeed.2da](2DA-File-Format#creaturespeed2da)
  - [cursors.2da](2DA-File-Format#cursors2da)
  - [dialoganimations.2da](2DA-File-Format#dialoganimations2da)
  - [difficultyopt.2da](2DA-File-Format#difficultyopt2da)
  - [disease.2da](2DA-File-Format#disease2da)
  - [doortypes.2da](2DA-File-Format#doortypes2da)
  - [droiddischarge.2da](2DA-File-Format#droiddischarge2da)
  - [effecticon.2da](2DA-File-Format#effecticon2da)
  - [emotion.2da](2DA-File-Format#emotion2da)
  - [encdifficulty.2da](2DA-File-Format#encdifficulty2da)
  - [exptable.2da](2DA-File-Format#exptable2da)
  - [facialanim.2da](2DA-File-Format#facialanim2da)
  - [feat.2da](2DA-File-Format#feat2da)
  - [featgain.2da](2DA-File-Format#featgain2da)
  - [feedbacktext.2da](2DA-File-Format#feedbacktext2da)
  - [footstepsounds.2da](2DA-File-Format#footstepsounds2da)
  - [forceshields.2da](2DA-File-Format#forceshields2da)
  - [fractionalcr.2da](2DA-File-Format#fractionalcr2da)
  - [gender.2da](2DA-File-Format#gender2da)
  - [genericdoors.2da](2DA-File-Format#genericdoors2da)
  - [globalcat.2da](2DA-File-Format#globalcat2da)
  - [grenadesnd.2da](2DA-File-Format#grenadesnd2da)
  - [guisounds.2da](2DA-File-Format#guisounds2da)
  - [heads.2da](2DA-File-Format#heads2da)
  - [inventorysnds.2da](2DA-File-Format#inventorysnds2da)
  - [iprp_abilities.2da](2DA-File-Format#iprp_abilities2da)
  - [iprp_acmodtype.2da](2DA-File-Format#iprp_acmodtype2da)
  - [iprp_aligngrp.2da](2DA-File-Format#iprp_aligngrp2da)
  - [iprp_ammotype.2da](2DA-File-Format#iprp_ammotype2da)
  - [iprp_combatdam.2da](2DA-File-Format#iprp_combatdam2da)
  - [iprp_costtable.2da](2DA-File-Format#iprp_costtable2da)
  - [iprp_damagecost.2da](2DA-File-Format#iprp_damagecost2da)
  - [iprp_damagetype.2da](2DA-File-Format#iprp_damagetype2da)
  - [iprp_immunity.2da](2DA-File-Format#iprp_immunity2da)
  - [iprp_lightcol.2da](2DA-File-Format#iprp_lightcol2da)
  - [iprp_monstdam.2da](2DA-File-Format#iprp_monstdam2da)
  - [iprp_mosterhit.2da](2DA-File-Format#iprp_mosterhit2da)
  - [iprp_onhit.2da](2DA-File-Format#iprp_onhit2da)
  - [iprp_paramtable.2da](2DA-File-Format#iprp_paramtable2da)
  - [iprp_protection.2da](2DA-File-Format#iprp_protection2da)
  - [iprp_saveelement.2da](2DA-File-Format#iprp_saveelement2da)
  - [iprp_savingthrow.2da](2DA-File-Format#iprp_savingthrow2da)
  - [iprp_walk.2da](2DA-File-Format#iprp_walk2da)
  - [itempropdef.2da](2DA-File-Format#itempropdef2da)
  - [itemprops.2da](2DA-File-Format#itemprops2da)
  - [keymap.2da](2DA-File-Format#keymap2da)
  - [loadscreenhints.2da](2DA-File-Format#loadscreenhints2da)
  - [loadscreens.2da](2DA-File-Format#loadscreens2da)
  - [masterfeats.2da](2DA-File-Format#masterfeats2da)
  - [modulesave.2da](2DA-File-Format#modulesave2da)
  - [movies.2da](2DA-File-Format#movies2da)
  - [pazaakdecks.2da](2DA-File-Format#pazaakdecks2da)
  - [placeableobjsnds.2da](2DA-File-Format#placeableobjsnds2da)
  - [placeables.2da](2DA-File-Format#placeables2da)
  - [planetary.2da](2DA-File-Format#planetary2da)
  - [plot.2da](2DA-File-Format#plot2da)
  - [poison.2da](2DA-File-Format#poison2da)
  - [portraits.2da](2DA-File-Format#portraits2da)
  - [prioritygroups.2da](2DA-File-Format#prioritygroups2da)
  - [racialtypes.2da](2DA-File-Format#racialtypes2da)
  - [ranges.2da](2DA-File-Format#ranges2da)
  - [regeneration.2da](2DA-File-Format#regeneration2da)
  - [repute.2da](2DA-File-Format#repute2da)
  - [skills.2da](2DA-File-Format#skills2da)
  - [soundset.2da](2DA-File-Format#soundset2da)
  - [spells.2da](2DA-File-Format#spells2da)
  - [stringtokens.2da](2DA-File-Format#stringtokens2da)
  - [subrace.2da](2DA-File-Format#subrace2da)
  - [surfacemat.2da](2DA-File-Format#surfacemat2da)
  - [texpacks.2da](2DA-File-Format#texpacks2da)
  - [traps.2da](2DA-File-Format#traps2da)
  - [tutorial.2da](2DA-File-Format#tutorial2da)
  - [upcrystals.2da](2DA-File-Format#upcrystals2da)
  - [upgrade.2da](2DA-File-Format#upgrade2da)
  - [videoeffects.2da](2DA-File-Format#videoeffects2da)
  - [visualeffects.2da](2DA-File-Format#visualeffects2da)
  - [weaponsounds.2da](2DA-File-Format#weaponsounds2da)
  - [xptable.2da](2DA-File-Format#xptable2da)
- **[TLK File Format](Audio-and-Localization-Formats#tlk)** ← Complete reference for [Talk Table](Audio-and-Localization-Formats#tlk) format
- [BIF File Format](Container-Formats#bif) ← BioWare Infinity format
- [KEY File Format](Container-Formats#key) ← [KEY](Container-Formats#key) file format
- **[BWM File Format](Level-Layout-Formats#bwm)** ← Complete reference for Binary [walkmesh](Level-Layout-Formats#bwm) format
- **[GUI File Format](GFF-GUI)** ← Complete reference for Graphical User Interface format
- [ERF File Format](Container-Formats#erf) ← Encapsulated Resource format (MOD, SAV, HAK; [RIM comparison](Container-Formats#rim-versus-erf))
- **[Kit Structure Documentation](Kit-Structure-Documentation)** ← Complete reference for indoor kit structure and generation
- [GFF File Format](GFF-File-Format) ← Generic file Format (see also [Official Bioware GFF Documentation](Bioware-Aurora-Core-Formats#gff))
  - [ARE (Area)](GFF-Module-and-Area#are)
  - [DLG (Dialogue)](GFF-Creature-and-Dialogue#dlg)
  - [GIT (Game Instance Template)](GFF-Module-and-Area#git)
  - [GUI (Graphical User Interface)](GFF-GUI)
  - [IFO (Module Info)](GFF-Module-and-Area#ifo)
  - [JRL (Journal)](GFF-Items-and-Economy#jrl)
  - [PTH (Path)](GFF-Spatial-Objects#pth)
  - [UTC (Creature)](GFF-Creature-and-Dialogue#utc)
  - [UTD (Door)](GFF-Spatial-Objects#utd)
  - [UTE (Encounter)](GFF-Spatial-Objects#ute)
  - [UTI (Item)](GFF-Items-and-Economy#uti)
  - [UTM (Merchant)](GFF-Items-and-Economy#utm)
  - [UTP (Placeable)](GFF-Spatial-Objects#utp)
  - [UTS (Sound)](GFF-Spatial-Objects#uts)
  - [UTT (Trigger)](GFF-Spatial-Objects#utt)
  - [UTW (Waypoint)](GFF-Spatial-Objects#utw)
- [DDS File Format](Texture-Formats#dds) ← DirectDraw Surface texture format
- [LIP File Format](Audio-and-Localization-Formats#lip) ← [LIP](Audio-and-Localization-Formats#lip) sync format
- [LTR File Format](LTR-File-Format) ← [Letter](LTR-File-Format) format
- [LYT File Format](Level-Layout-Formats#lyt) ← [Layout](Level-Layout-Formats#lyt) format
- [NCS File Format](NCS-File-Format) ← [NwScript Compiled Script](NCS-File-Format) format
- [NSS File Format](NSS-File-Format) ← [NwScript Source](NSS-File-Format) format (*nwscript.nss*, function/constant definitions)
- [RIM File Format](Container-Formats#rim) ← [Resource Image](Container-Formats#rim) format
- [SSF File Format](Audio-and-Localization-Formats#ssf) ← [Sound Set Files](Audio-and-Localization-Formats#ssf) format
- [TPC File Format](Texture-Formats#tpc) ← [Texture Pack Container](Texture-Formats#tpc) format
- [TXI File Format](Texture-Formats#txi) ← [Texture Info](Texture-Formats#txi) format
- [VIS File Format](Level-Layout-Formats#vis) ← [Visibility](Level-Layout-Formats#vis) format
- [WAV File Format](Audio-and-Localization-Formats#wav) ← [Wave](Audio-and-Localization-Formats#wav) audio format

### See also

- [Concepts](Concepts) — Override, BIF/KEY, MOD/ERF/RIM, GFF, 2DA, language IDs
- [Container-Formats#key](Container-Formats#key) — KEY binary layout and index role
- [Mod-Creation-Best-Practices](Mod-Creation-Best-Practices#file-priority-and-where-to-put-your-files) — Where to install files
- [Home](Home) — Wiki hub
- [Reverse Engineering Findings — Resource Management System](reverse_engineering_findings#resource-management-system) — Engine `CExoResMan` / resource loading (conceptual)
