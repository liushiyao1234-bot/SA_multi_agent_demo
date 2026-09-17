
import json


def load_product_catalog(file_path="products.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def search_product_capabilities(query, products):
    stop_words = {
        "the", "a", "an", "and", "or", "for", "to", "of",
        "system", "solutions", "solution"
    }

    query_terms = {
        term.lower()
        for term in query.replace("-", " ").split()
        if len(term) > 2 and term.lower() not in stop_words
    }

    scored_results = []

    for item in products:
        product = str(item.get("product", "")).lower()
        category = str(item.get("category", "")).lower()
        capability = str(item.get("capability", "")).lower()
        description = str(item.get("description", "")).lower()

        score = 0
        matched_terms = set()

        for term in query_terms:
            if term in product:
                score += 4
                matched_terms.add(term)

            if term in capability:
                score += 3
                matched_terms.add(term)

            if term in category:
                score += 2
                matched_terms.add(term)

            if term in description:
                score += 1
                matched_terms.add(term)

        # 至少命中两个不同关键词，或者明确命中产品名
        product_name_matched = any(
            term in product for term in query_terms
        )

        if len(matched_terms) >= 2 or product_name_matched:
            scored_results.append(
                {
                    "score": score,
                    "matched_terms": list(matched_terms),
                    "data": item
                }
            )

    scored_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return [
        result["data"]
        for result in scored_results
    ]