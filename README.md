Modification of suchmememanyskill's SaveExtract script to turn saves extracted from the user partition to saves injectable through a homebrew app such as [JKSV](https://github.com/J-D-K/JKSV).

Huge thanks for [suchmememanyskill](https://github.com/suchmememanyskill) for the original script!

## Requirements

- Python 3.6+
- [hactool](https://github.com/SciresM/hactool) installed and available in PATH (Linux) or as `hactool.exe` in the script directory (Windows)
- `prod.keys` file placed in the SaveExtract directory

## Usage

Place your save files in a `save/` directory, then run:

```bash
# Default mode: outputs to out/<TitleID>/
python extract.py

# Game name mode: outputs to out/<Game Name>/<TitleID>/
python extract.py --game-names

# Game name mode without edition suffixes (Switch 2 games use same folder as Switch):
python extract.py --game-names --strip-edition
```

### Options

| Flag              | Description                                                                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `--game-names`    | Organize saves by game name using the [titledb](https://github.com/blawar/titledb) database. Downloads `US.en.json` automatically if needed. |
| `--strip-edition` | Remove edition suffixes (e.g. ` – Nintendo Switch 2 Edition`) from game names, so Switch and Switch 2 versions share the same folder.        |

### Output structure

**Default:**
```
out/
└── 0100646009FBE000/
    └── <save data>
```

**With `--game-names`:**
```
out/
└── Dead Cells/
    └── 0100646009FBE000/
        └── <save data>
```

Game names are sanitized to ASCII (e.g. `Mario Kart™ 8 Deluxe` → `Mario Kart 8 Deluxe`) for compatibility with JKSV.
