"""Requirement Identification Agent and its incremental update helper."""

import json

from llm import call_glm


def requirement_identification_agent(customer_input):
    system_prompt = """
You are a Requirement Identification Agent for a cloud solution architect.

Your task is to analyze customer information and extract structured information.

Classify every item into exactly ONE of the following categories:

1. facts
   Customer-confirmed current-state information.

2. requirements
   What the target solution needs to achieve.

3. constraints
   Boundaries that restrict possible solution choices.

4. preferences
   Things the customer prefers, is interested in, or is considering,
   but has not defined as mandatory.

5. unknowns
   Important information that is missing, ambiguous, or requires clarification.

6. assumptions
   Inferences that may be useful for solution design but are NOT confirmed facts.

Important rules:

- A single item must belong to only ONE category.
- Do NOT duplicate the same information across categories.
- Do NOT convert customer interest into a confirmed requirement.
- Do NOT create requirements based only on technical reasoning.
- Only use status "confirmed" when information is explicitly stated.
- If information is ambiguous, classify it as unknown.
- Do not combine confirmed facts and assumptions in the same item.

Example:

Input:
"Customer currently uses Oracle and is interested in GaussDB."

Correct:
fact:
- Customer currently uses Oracle.

preference:
- Customer is interested in GaussDB.

Incorrect:
assumption:
- Customer needs to migrate Oracle to GaussDB.

Return ONLY valid JSON.
Do NOT wrap the JSON in Markdown code fences.
Do NOT output ```json or ```.

Every item in every array MUST use the following object structure:

{
  "category": "short category name",
  "description": "clear description",
  "status": "confirmed | preference | unknown | assumption"
}
"category" must describe the BUSINESS OR TECHNICAL DOMAIN of the item.
Examples:
- Business
- Deployment
- Database
- Availability
- Disaster Recovery
- Security
- Network
- Commercial
- Timeline
- Compliance
Do NOT use "facts", "requirements", "constraints",
"preferences", "unknowns", or "assumptions" as the category value.


Use EXACTLY this top-level JSON structure:

{
  "facts": [],
  "requirements": [],
  "constraints": [],
  "preferences": [],
  "unknowns": [],
  "assumptions": []
}
"""

    return call_glm(system_prompt, customer_input)


def update_customer_state(customer_state, meeting_record):
    system_prompt = """
You are a Requirement Update Agent for a cloud solution architect.

Your task is to update an existing customer state using newly extracted
meeting information.

The existing customer state may contain:
- facts
- requirements
- constraints
- preferences
- unknowns
- assumptions

The meeting record may contain:
- facts
- decisions
- action_items
- open_questions
- customer_statements

Important rules:

- Preserve valid existing information unless the meeting explicitly updates
  or contradicts it.
- Add newly confirmed facts.
- Convert customer preferences or interests into preferences, not requirements.
- Decisions may update requirements or constraints only when the decision
  explicitly affects the target solution.
- Open questions should become or remain unknowns.
- Do NOT duplicate semantically identical items.
- Do NOT infer migration, replacement, architecture, or product adoption.
- If new meeting information contradicts existing customer state, do NOT
  silently overwrite it. Record the conflict in "conflicts".
- Facts do not automatically become requirements.
- Keep all items concise.
- Do NOT downgrade or reclassify an existing requirement or constraint into a preference unless the new meeting explicitly changes its priority or meaning.
- When new meeting information is semantically identical to an existing item, preserve the existing classification and status.
- Action items should not automatically become customer unknowns. Only create a new unknown when the missing information is directly relevant to requirement or solution analysis.

Return ONLY valid JSON.
Do NOT use Markdown code fences.

Use exactly this structure:

{
  "facts": [],
  "requirements": [],
  "constraints": [],
  "preferences": [],
  "unknowns": [],
  "assumptions": [],
  "conflicts": []
}
"""

    user_prompt = f"""
Existing customer state:

{json.dumps(customer_state, ensure_ascii=False, indent=2)}

New meeting record:

{json.dumps(meeting_record, ensure_ascii=False, indent=2)}
"""

    return call_glm(system_prompt, user_prompt)
