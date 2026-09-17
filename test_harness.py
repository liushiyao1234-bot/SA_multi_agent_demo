
from harness.setup import create_harness


registry, executor = create_harness()

print("Registered tools:")
print(registry.list_tools())

products = executor.execute(
    agent_name="Product Search Agent",
    tool_name="load_product_catalog"
)

print("\nLoaded products:")
print(len(products))

results = executor.execute(
    agent_name="Product Search Agent",
    tool_name="search_product_capabilities",
    query="dual-active",
    products=products
)


print("\nSearch results:")
for item in results:
    print(item)

# 临时测试一下
test_queries = [
    "private cloud deployment SPEI financial system",
    "GaussDB dual-active deployment",
    "OPEX business model cloud solutions",
    "local high availability intra-city cross-datacenter dual-active",
    "disaster recovery RPO RTO database solutions",
]

print("\n=== Retrieval Tests ===")

for query in test_queries:
    print(f"\nQuery: {query}")

    results = executor.execute(
        agent_name="Product Search Agent",
        tool_name="search_product_capabilities",
        query=query,
        products=products
    )

    print(f"Results: {len(results)}")

    for item in results:
        print(
            f"- {item.get('product')} | "
            f"{item.get('category')} | "
            f"{item.get('capability')}"
        )