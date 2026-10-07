import asyncio, json, sys
from core.pipeline import check_text

async def main():
    items = json.load(open("data/demo.json"))
    for i in [int(x) for x in sys.argv[1:]]:
        res = await check_text(items[i]["text"])
        print("=" * 70)
        print(items[i]["text"])
        for c in res["claims"]:
            print("\nCLAIM:", c["text"])
            print("LABEL:", c["label"])
            print("WHY:", c["explanation_en"])
            for e in c["evidence"]:
                print("  -", e["source"], e["date"], "|", e["quote"][:150])

asyncio.run(main())
