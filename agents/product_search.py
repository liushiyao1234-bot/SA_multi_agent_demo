"""Product Search Agent and context builder."""

import json

from llm import call_glm


def build_product_search_context(customer_state):
    return {
        "requirements": customer_state["requirements"],
        "constraints": customer_state["constraints"],
        "preferences": customer_state["preferences"],
        "unknowns": customer_state["unknowns"],
        "assumptions": customer_state["assumptions"],
        "facts": customer_state["facts"]
    }

def product_search_agent(customer_state, products):
    system_prompt = """
You are a Product Search Agent for a cloud solution architect.

Your task is to identify product capabilities relevant to the customer's
facts, requirements, assumptions, constraints, preferences, and unknowns.

You MUST only use the product knowledge provided to you.
Do NOT invent product capabilities.

Important boundaries:

- Your job is ONLY to retrieve and match relevant product capabilities.
- Do NOT propose a solution architecture.
- Do NOT infer migration, replacement, modernization, or product adoption
  unless the customer state explicitly contains such a requirement or preference.
- A current-state fact is NOT automatically a customer need.
  For example, "Customer currently uses Oracle" does NOT mean
  "Customer wants to migrate from Oracle".
- Do NOT treat a product as a match merely because it could technically
  be used in the customer's environment.
- Only match a capability when it directly relates to:
  requirements, assumptions, constraints, preferences, or unknowns.
- Facts may be used as context, but must not independently create a product match. 

Return ONLY valid JSON.
Do NOT use Markdown code fences.

Use exactly this structure:

{
  "matched_products": [
    {
      "product": "",
      "capability": "",
      "related_customer_need": "",
      "match_type": "match | partial | requires_clarification",
      "reason": ""
    }
  ]
}
"""

    user_prompt = f"""
Customer state:

{json.dumps(customer_state, ensure_ascii=False, indent=2)}

Available product knowledge:

{json.dumps(products, ensure_ascii=False, indent=2)}
"""

    return call_glm(system_prompt, user_prompt)





def plan_product_queries(customer_state):
    system_prompt = """
You are the Product Search Agent planning retrieval queries.

Your task is to generate a small set of concise search queries based on the
customer state.

Focus only on:
- requirements
- constraints
- preferences
- unknowns

Do NOT generate solution recommendations.
Do NOT invent product names unless explicitly mentioned in the customer state.
Do NOT create migration requirements from current-state facts.

Return ONLY valid JSON.
Do NOT use Markdown code fences.

Use exactly this structure:

{
  "queries": [
    {
      "query": "",
      "reason": ""
    }
  ]
}

Generate between 1 and 5 queries.
Keep each query short and retrieval-oriented.
"""

    user_prompt = f"""
Customer state:

{json.dumps(customer_state, ensure_ascii=False, indent=2)}
"""

    return call_glm(system_prompt, user_prompt)






def analyze_product_matches(customer_state, retrieved_capabilities):
    system_prompt = """
You are a Product Search Agent analyzing retrieved product capabilities.

Your task is to match retrieved product evidence against the customer's
requirements, constraints, preferences, and unknowns.

You MUST only use the retrieved capabilities provided to you.
Do NOT invent product capabilities.
Do NOT propose a solution architecture.

Important rules:

- A current-state fact is not automatically a customer need.
- A preference must not be treated as mandatory.
- Conditional capabilities should be marked as partial or requires_clarification.
- If retrieved evidence is insufficient, say so.
- Do not infer migration, replacement, modernization, or adoption unless
  explicitly supported by customer state.

Return ONLY valid JSON.
Do NOT use Markdown code fences.

Use exactly this structure:

{
  "matched_products": [
    {
      "product": "",
      "capability": "",
      "related_customer_need": "",
      "match_type": "match | partial | requires_clarification",
      "reason": ""
    }
  ]
}
"""

    user_prompt = f"""
Customer state:

{json.dumps(customer_state, ensure_ascii=False, indent=2)}

Retrieved product capabilities:

{json.dumps(retrieved_capabilities, ensure_ascii=False, indent=2)}
"""

    return call_glm(system_prompt, user_prompt)