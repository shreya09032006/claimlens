import asyncio, json
from core.pipeline import check_text


async def main():
    items = json.load(open("data/demo.json"))
    ok = 0
    for it in items:
        res = await check_text(it["text"])
        labels = [c["label"] for c in res["claims"]]; got = it["expected"] if it["expected"] in labels else (labels[0] if labels else "NO CLAIM")
        match = got == it["expected"]
        ok += match
        print(("PASS" if match else "FAIL"), "| expected:", it["expected"], "| got:", got, "|", it["text"][:60])
        await asyncio.sleep(15)
    print(f"\n{ok}/{len(items)} matched")


asyncio.run(main())
