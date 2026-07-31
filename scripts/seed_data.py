"""Seed ATLAS with real on-chain pins on studionet (AI verification)."""
from pathlib import Path

from gltest_cli.config.general import get_general_config
from gltest_cli.config.user import load_user_config
from gltest import get_contract_factory, get_default_account

ROOT = Path(__file__).resolve().parents[1]
ADDR = "0xee59893A6AAB0dCccD130557d1D8e17e2C2EdA87"
W = "https://en.wikipedia.org/api/rest_v1/page/summary/"

cfg = load_user_config(str(ROOT / "gltest.config.yaml"))
get_general_config().user_config = cfg
factory = get_contract_factory(contract_file_path=str(ROOT / "contracts" / "atlas.py"))
c = factory.build_contract(ADDR, account=get_default_account())

PLACES = [
    ("Eiffel Tower", "Wrought-iron lattice tower on the Champ de Mars in Paris, built 1889.", "landmark", "48.8584", "2.2945", W + "Eiffel_Tower", True),
    ("Statue of Liberty", "Neoclassical copper statue on Liberty Island in New York Harbor.", "monument", "40.6892", "-74.0445", W + "Statue_of_Liberty", True),
    ("Atlantis", "Legendary lost island city said to have sunk into the ocean.", "mystery", "31.0", "-24.0", W + "Atlantis", True),
    ("Mount Fuji", "Active stratovolcano and the highest mountain in Japan.", "nature", "35.3606", "138.7274", W + "Mount_Fuji", False),
    ("Sydney Opera House", "Multi-venue performing arts centre on Sydney Harbour.", "landmark", "-33.8568", "151.2153", W + "Sydney_Opera_House", False),
]


def main():
    if c.get_place_count().call() == 0:
        for (n, d, cat, lat, lng, url, _) in PLACES:
            c.add_place(args=[n, d, cat, lat, lng, url]).transact()
            print("pinned:", n)

    for pid in range(c.get_place_count().call()):
        p = c.get_place(args=[pid]).call()
        should = PLACES[pid][6] if pid < len(PLACES) else False
        if should and int(p["status"]) == 0:
            print("verifying (AI):", p["name"])
            try:
                c.verify(args=[pid]).transact()
            except Exception as e:
                print("  verify ->", e)

    for pid in range(c.get_place_count().call()):
        p = c.get_place(args=[pid]).call()
        print(pid, ["PENDING", "VERIFIED", "REJECTED"][int(p["status"])], p["name"], "|", (p["rationale"] or "")[:50])


if __name__ == "__main__":
    main()
