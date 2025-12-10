"""
Extracts save files from the save directory and outputs them in a format that can be interpreted through an app such as JKSV.

Script originally written by suchmememanyskill and modified by HunterMario to add Unix support 
"""

import subprocess, os


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
    return str(subprocess.check_output(["hactool.exe", "-k", "prod.keys", "-t", "save" , f"save/{fileName}", "--outdir", f"out/{fileName}"]))

def getHactoolOutputUnix(fileName : str) -> str:
    return str(subprocess.check_output(["hactool", "-k", "prod.keys", "-t", "save" , f"save/{fileName}", "--outdir", f"out/{fileName}"]))


if __name__ == "__main__":
    hactoolPrep()
    directory = os.fsencode("./save")
    for file in os.listdir(directory):
        fileName = os.fsdecode(file)

        print(f"Extracting {fileName}")
        text = getHactoolOutput(fileName)
        # findInText() may raise a ValueError if "Title ID" is not found in the file
        try:
            portion = findInText(text, "Title ID:").upper()
            print(f"{fileName} => {portion}")
            if (os.path.exists(f"out/{portion}")):
                dirnumber = 1
                while (os.path.exists(f"out/{portion}_{dirnumber}")):
                    dirnumber += 1
                os.rename(f"out/{fileName}", f"out/{portion}_{dirnumber}")
            else:
                os.rename(f"out/{fileName}", f"out/{portion}")
        except ValueError:
            pass