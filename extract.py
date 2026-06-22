"""
Extracts save files from the save directory and outputs them in a format that can be interpreted through an app such as JKSV.

Script originally written by suchmememanyskill and modified by HunterMario to add Unix support 
"""

import subprocess, os, urllib.request, json, re, argparse


def downloadTitleDb(dest="US.en.json") -> str:
    url = "https://raw.githubusercontent.com/blawar/titledb/master/US.en.json"
    # Check remote file size and skip download if local file matches
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req) as resp:
        remote_size = int(resp.headers.get("Content-Length", -1))
    if os.path.exists(dest) and remote_size > 0:
        local_size = os.path.getsize(dest)
        if local_size == remote_size:
            print("Title database is up to date, skipping download.")
            return dest
    urllib.request.urlretrieve(url, dest)
    return dest

def loadTitleDb(path="US.en.json") -> dict:
    """Load title DB and return a dict mapping title ID (uppercase) to game name."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    lookup = {}
    for entry in data.values():
        tid = entry.get("id")
        name = entry.get("name")
        if tid and name:
            lookup[tid.upper()] = name
    return lookup

def sanitizeDirName(name: str, strip_edition: bool = False) -> str:
    """Sanitize game name for path use, matching JKSV behavior (strip non-ASCII and invalid chars)."""
    if strip_edition:
        name = re.sub(r'\s*[–-]\s*Nintendo Switch\s*\d*\s*Edition', '', name)
    # Remove non-ASCII characters (™, ®, ©, etc.)
    name = name.encode("ascii", "ignore").decode("ascii")
    # Remove filesystem-invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Collapse multiple spaces and strip
    name = re.sub(r' +', ' ', name).strip()
    return name

def findInText(txt, find) -> str:
    if os.name == "posix":
        for x in txt.split("\\n"):
            if find in x:
                return x.split(":")[1].strip()
    else:
        for x in txt.split("\\r\\n"):
            if find in x:
                return x.split(":")[1].strip()
    raise ValueError

def hactoolPrep():
    if os.name == "posix":
        try:
            subprocess.run("hactool")
        except subprocess.CalledProcessError:
            raise FileNotFoundError("You need to install hactool before using this tool")
    
def checkKeys():
    if not os.path.exists("prod.keys"):
        raise FileNotFoundError("Please put your prod.keys in the SaveExtract directory")
    
def getHactoolOutput(fileName : str) -> str:
    if os.name == "nt":
        return getHactoolOutputWindows(fileName)
    else:
        return getHactoolOutputUnix(fileName)

def getHactoolOutputWindows(fileName : str) -> str:
    output = subprocess.check_output(["hactool.exe", "-k", "prod.keys", "-t", "save" , f"save/{fileName}", "--outdir", f"out/{fileName}"], stderr=subprocess.STDOUT)
    with open("hactool.log", "a", encoding="utf-8") as log:
        log.write(f"=== {fileName} ===\n")
        log.write(output.decode("utf-8", errors="replace"))
        log.write("\n")
    return str(output)

def getHactoolOutputUnix(fileName : str) -> str:
    output = subprocess.check_output(["hactool", "-k", "prod.keys", "-t", "save" , f"save/{fileName}", "--outdir", f"out/{fileName}"], stderr=subprocess.STDOUT)
    with open("hactool.log", "a", encoding="utf-8") as log:
        log.write(f"=== {fileName} ===\n")
        log.write(output.decode("utf-8", errors="replace"))
        log.write("\n")
    return str(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Nintendo Switch save files.")
    parser.add_argument("--game-names", action="store_true",
                        help="Organize output by game name (out/<game name>/<ID>/) instead of just ID")
    parser.add_argument("--strip-edition", action="store_true",
                        help="Remove edition suffixes (e.g. ' – Nintendo Switch 2 Edition') from game names")
    args = parser.parse_args()

    hactoolPrep()

    titleDb = {}
    if args.game_names:
        print("Downloading title database...")
        downloadTitleDb()
        titleDb = loadTitleDb()

    directory = os.fsencode("./save")
    os.makedirs("out", exist_ok=True)
    for file in os.listdir(directory):
        fileName = os.fsdecode(file)

        print(f"Extracting {fileName}")
        text = getHactoolOutput(fileName)
        try:
            titleId = findInText(text, "Title ID:").upper()

            if args.game_names:
                gameName = titleDb.get(titleId)
                if gameName:
                    gameName = sanitizeDirName(gameName, strip_edition=args.strip_edition)
                    destDir = f"out/{gameName}/{titleId}"
                else:
                    print(f"  Warning: Title ID {titleId} not found in title database")
                    destDir = f"out/{titleId}"
                os.makedirs(os.path.dirname(destDir), exist_ok=True)
            else:
                destDir = f"out/{titleId}"

            if os.path.exists(destDir):
                dirnumber = 1
                while os.path.exists(f"{destDir}_{dirnumber}"):
                    dirnumber += 1
                os.rename(f"out/{fileName}", f"{destDir}_{dirnumber}")
            else:
                os.rename(f"out/{fileName}", destDir)

            print(f"  {fileName} => {destDir}")
        except ValueError:
            pass