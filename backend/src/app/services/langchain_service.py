from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.orm import Session
import json # For parsing potential JSON responses
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Optional, Any, Tuple, Callable # Přidána Callable
import re # Přidán import pro regulární výrazy

from app.core.config import settings
from app import crud, schemas # Import main crud and schemas modules
from app.models import User # Assuming CRUD functions might need the user

# Mapování typů entit na CRUD funkce (vytvoření a získání všech)
# Typ klíče: str (entity_type)
# Typ hodnoty: Tuple[Callable, Type[BaseModel], Callable]
# (create_function, CreateSchema, get_all_by_world_function)
ENTITY_CRUD_MAP: Dict[str, Tuple[Callable, Any, Callable]] = {
    "character": (crud.create_character, schemas.CharacterCreate, crud.get_all_characters_in_world),
    "location": (crud.create_location, schemas.LocationCreate, crud.get_locations_by_world),
    "organization": (crud.create_organization, schemas.OrganizationCreate, crud.get_organizations_by_world),
    "item": (crud.create_item, schemas.ItemCreate, crud.get_items_by_world),
}

class LangChainService:
    def __init__(self):
        """Initializes the LangChain service with the configured LLM."""
        # Ensure the API key is available
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in settings.")

        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7 # Add some creativity
        )
        print(f"LangChainService initialized with model: {settings.GEMINI_MODEL_NAME}") # For debugging

    async def generate_entity(
        self,
        db: Session,
        current_user: User,
        world_id: int, # Added world_id
        entity_type: str,
        existing_entities: list[dict],
        context: str | None = None
    ) -> Any: # Return type will depend on the created entity schema
        """
        Generates a new game entity using LLM, saves it to the database.
        """
        print(f"[LangChainService] Generating {entity_type} for user {current_user.id} in world {world_id}...")

        # Získání CRUD funkcí z mapy
        if entity_type not in ENTITY_CRUD_MAP:
            raise ValueError(f"Unsupported entity type: {entity_type}")
        crud_function, create_schema, get_all_function = ENTITY_CRUD_MAP[entity_type]

        # Načtení VŠECH existujících entit daného typu v tomto světě pro získání názvů
        try:
            print(f"[LangChainService] Fetching all existing {entity_type} names for world {world_id}...")
            all_existing_entities_in_world = get_all_function(db=db, world_id=world_id, limit=1000) # Zvýšený limit pro jistotu
            existing_names = [entity.name for entity in all_existing_entities_in_world]
            print(f"[LangChainService] Found {len(existing_names)} existing names.")
        except Exception as e:
            # Pokračujeme i v případě chyby, ale zalogujeme ji
            print(f"[LangChainService] Warning: Failed to fetch existing names for {entity_type}: {e}")
            existing_names = []

        # Define the prompt template
        prompt_template_str = """
You are an assistant helping design content for a role-playing game.
Analyze the language used in the 'Existing Examples' and 'Context'. Respond ONLY in that same language.
Generate a new RPG entity of type '{entity_type}' based on the provided examples and context.

Entity Type: {entity_type}
Context: {context}
Existing Examples (used for style and content inspiration):
{examples}

List of existing names for {entity_type} in this world (DO NOT use these names):
{existing_names_list}

Please generate ONLY the raw JSON object containing the core details for the new entity. Do NOT include any markdown formatting like ```json or ``` around the JSON object.
Your entire response must start directly with `{` and end directly with `}`.
Ensure the generated JSON is valid and uses correct UTF-8 encoding for all characters.
The JSON object must have the following keys:
- "name": (string) The name of the {entity_type}. It must be unique and not in the list above.
- "description": (string) A detailed description of the {entity_type}, including any necessary Markdown formatting INSIDE the string value.

Example JSON format:
{{ "name": "Unique Example Name", "description": "Example **description** with markdown." }}

Valid JSON Output:
"""
        prompt = PromptTemplate(
            template=prompt_template_str,
            input_variables=["entity_type", "context", "examples", "existing_names_list"],
        )

        # Prepare chain s StrOutputParser
        chain = prompt | self.llm | StrOutputParser()

        try:
            print(f"[LangChainService] Invoking LLM for {entity_type}...")
            # Format examples for the prompt
            formatted_examples = "\n".join([f"- {json.dumps(ex)}" for ex in existing_entities])
            # Format existing names for the prompt
            formatted_existing_names = "\n".join([f"- {name}" for name in existing_names]) if existing_names else "(No existing names found or provided)"

            llm_raw_output: str = await chain.ainvoke({
                "entity_type": entity_type,
                "context": context or "No additional context provided.",
                "examples": formatted_examples,
                "existing_names_list": formatted_existing_names
            })
            print(f"[LangChainService] Raw LLM output received:\n{llm_raw_output}")

            # Extrakce JSON - vylepšená logika
            json_string = None
            # 1. Pokus: Najít blok ```json ... ``` nebo ``` ... ```
            match = re.search(r"```(?:json)?\s*({.*?})\s*```", llm_raw_output, re.DOTALL | re.IGNORECASE)
            if match:
                json_string = match.group(1) # Skupina 1 obsahuje obsah mezi {}              
            else:
                # 2. Pokus: Najít první platný JSON objekt (začínající { končící })
                # Toto je méně spolehlivé, ale může zachytit případy bez značek
                match = re.search(r"({.*?})", llm_raw_output, re.DOTALL)
                if match:
                    # Zkusíme parsovat, zda je to validní JSON, abychom se vyhnuli chycení neúplných {} bloků
                    potential_json = match.group(1)
                    try:
                        json.loads(potential_json, strict=False)
                        json_string = potential_json
                        print("[LangChainService] Warning: Extracted JSON without ``` markers.")
                    except json.JSONDecodeError:
                        print("[LangChainService] Warning: Found {} block, but it's not valid JSON.")
                        pass # Necháme json_string None

            # Pokud se nepodařilo extrahovat JSON ani jedním způsobem
            if json_string is None:
                 print(f"[LangChainService] FATAL: Could not extract JSON block from LLM output.\n>>>\n{llm_raw_output}\n<<<")
                 raise ValueError("Could not extract JSON block from LLM response.")
            
            print(f"[LangChainService] Extracted JSON string:\n{json_string}")

            # Parsování JSON stringu
            try:
                # Použití strict=False pro větší toleranci k formátování
                llm_response_dict = json.loads(json_string, strict=False)
            except json.JSONDecodeError as jde:
                # Log the exact string that failed parsing for easier debugging
                print(f"[LangChainService] FATAL: Failed to decode JSON string. Error: {jde}. String content was:\\n>>>\\n{json_string}\\n<<<")
                raise ValueError(f"Failed to decode JSON from LLM response (see logs for full string). Error: {jde}")

            print(f"[LangChainService] Parsed LLM response dict: {llm_response_dict}")

        except Exception as e:
            # Zde již nechytáme OutputParserException, protože ho nepoužíváme
            print(f"[LangChainService] Error invoking LLM chain or processing response: {e}")
            import traceback
            print(f"Error during LLM chain invocation or processing: {traceback.format_exc()}")
            # Re-raise as a different error or handle appropriately
            raise RuntimeError(f"Failed during LLM interaction or response processing: {e}")

        # --- Data Preparation & Validation ---
        generated_data_dict = llm_response_dict # Nyní používáme náš parsovaný slovník

        # Zkontrolujeme, zda vygenerovaný název není v seznamu existujících (pro jistotu)
        if generated_data_dict.get('name') in existing_names:
            print(f"[LangChainService] Warning: LLM generated a duplicate name '{generated_data_dict.get('name')}'. Attempting to add suffix.")
            generated_data_dict['name'] = f"{generated_data_dict.get('name')} (AI Gen)"
            # TODO: Možná lepší strategie - požádat LLM znovu?

        # Inject required fields not generated by LLM
        generated_data_dict['world_id'] = world_id
        # Add user_id if the schema requires it (adjust based on your actual schemas)
        if 'user_id' in create_schema.model_fields:
            generated_data_dict['user_id'] = current_user.id

        # Validate and create the Pydantic schema object
        try:
            # Nejprve vytvoříme slovník jen s klíči, které existují ve schématu
            schema_fields = create_schema.model_fields.keys()
            valid_data_for_schema = {k: v for k, v in generated_data_dict.items() if k in schema_fields}
            entity_in = create_schema(**valid_data_for_schema)
        except Exception as e: # Catch Pydantic validation errors etc.
            missing_fields = [field for field in create_schema.model_fields if field not in generated_data_dict and create_schema.model_fields[field].is_required()]
            print(f"[LangChainService] Pydantic validation failed. Data: {generated_data_dict}, Missing/Invalid fields?: {missing_fields}, Error: {e}")
            raise ValueError(f"LLM output failed validation for {entity_type}. Missing fields: {missing_fields}. Error: {e}")

        # Call the appropriate CRUD function to save to DB
        print(f"[LangChainService] Calling CRUD function for {entity_type}...")

        # Dynamically determine the argument name for the Pydantic object
        # Convention: 'location' for create_location, 'character' for create_character, etc.
        pydantic_arg_name = entity_type 

        # Prepare keyword arguments for the CRUD function call
        crud_kwargs = {
            "db": db,
            pydantic_arg_name: entity_in
        }
        
        # Note: If any CRUD functions require *additional* arguments beyond 'db' 
        # and the pydantic object (like owner_id was previously assumed for items, but 
        # signature check revealed it's not needed directly in create_item), 
        # they would need specific handling here.
        # Based on checked signatures, only db and the pydantic object seem required.

        # Volání CRUD funkce s dynamickými argumenty
        created_entity = crud_function(**crud_kwargs)

        print(f"[LangChainService] Successfully created {entity_type} with ID: {created_entity.id}")
        return created_entity

    async def summarize_session(self, session_data: dict, journal_entries: list[dict]) -> str:
        """
        Summarizes a game session based on session details and journal entries.
        (Placeholder implementation)
        """
        # TODO: Implement prompt engineering and LLM call
        prompt = f"Summarize the session: {session_data} based on journal entries: {journal_entries}"
        print("[LangChainService] Summarizing session...")
        # Example call (replace with actual LangChain logic)
        # response = await self.llm.ainvoke(prompt)
        # summary = response.content
        return "This is a placeholder summary of the session generated by LangChainService." # Placeholder

# Optional: Add a function to parse LLM responses if they are structured (e.g., JSON)
# def parse_llm_response(response) -> dict:
#     # Implement parsing logic here
#     pass

# Single instance (dependency injection can be handled later if needed)
langchain_service = LangChainService() 