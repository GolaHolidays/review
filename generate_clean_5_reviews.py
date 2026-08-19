import asyncio
from app.core.review_generator import agenerate_review

async def generate_five():
    reviews = []
    print("Generating 5 reviews...")
    for i in range(1, 6):
        while True:
            try:
                rev = await agenerate_review()
                if rev and len(rev.strip()) > 15:
                    reviews.append(rev)
                    print(f"=== SUCCESS REVIEW {i} ===")
                    print(rev)
                    print()
                    break
            except Exception as e:
                print(f"Waiting 15s due to API limit on review {i}...")
                await asyncio.sleep(15)
        await asyncio.sleep(2)
    
    with open("five_reviews_output.txt", "w", encoding="utf-8") as f:
        for idx, r in enumerate(reviews, 1):
            f.write(f"=== REVIEW {idx} ===\n{r}\n\n")

if __name__ == "__main__":
    asyncio.run(generate_five())
