"""
storyforge/atoms.py

Customizable Atomic Narrative Structures via Comprehensive Data Model Frameworks

This module provides a robust and flexible set of Pydantic data models for defining
atomic narrative elements that can be used across a variety of systems, including
world-building, character development, event simulation, and more. These models 
are designed to support the creation of rich, structured data for highly dynamic 
and customizable storytelling environments.

Key Features:
- Modular "atomic" narrative models representing customizable canonical components:
  characters, locations, events, items, memories, and relationships within custom worlds 
  and narrative universes.
- Scalable architecture for representing data across different levels, from 
  individual elements to complex simulations and universes.
- Flexible integration across diverse narrative contexts, from text-based RPGs 
  to expansive storytelling and world-building projects.
- Extensible framework for defining custom rules, scenarios, and simulations for a 
  cohesive system of atomic narrative elements.

These models are designed to empower developers, world builders, writers, and homebrew
game masters to bring their creative visions to life with ease. Create worlds as big 
as your imagination with a system built for continuity, flexibility, and depth.

Author: Adyn Blaed
Project: HyperTech StoryForge
Date: Saturday, September 7th, 2024
Version: v1.1
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field

# ----------------------------------------------
# Base Model
# ----------------------------------------------

class BaseEntity(BaseModel):
    """
    Base entity model providing core attributes for all game elements.
    
    Attributes:
        system_id (Union[str, int]): Systematic, machine-readable identifier for the entity.
        canonical_id (Union[str, int]): User-defined, lore-driven identifier for the entity. 
                                        This ID should be meaningful in the context of the lore or world.
        name (str): Name of the entity.
        description (str): Detailed description of the entity.
        tags (List[str]): List of tags for categorization and filtering of entities.
        timeline (Optional[Union[str, int]]): The timeline or period with which the entity is associated. 
                                              Useful for tracking the entity's significance over time.
        timestamp (Optional[Union[str, int]]): The specific moment of the entity's significance. 
                                               This can represent a key event or creation date.
    """
    system_id: Union[str, int] = Field(..., description="Systematic identifier for the entity.")
    canonical_id: Union[str, int] = Field(..., description="Lore-friendly identifier for the entity.")
    name: str = Field(..., description="Name of the entity.")
    description: str = Field("", description="Description of the entity.")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization and filtering.")
    timeline: Optional[Union[str, int]] = Field(None, description="Timeline the entity is associated with.")
    timestamp: Optional[Union[str, int]] = Field(None, description="Time of the entity's significance.")

    class Config:
        """
        Pydantic configuration for BaseEntity.
        
        - Allows population of fields by name for easier instantiation.
        - Ensures validation on assignment for dynamic data.
        """
        populate_by_name = True
        validate_assignment = True

# ----------------------------------------------
# Universal Enumerations
# ----------------------------------------------

class Alignment(str, Enum):
    """
    Enumeration of character alignments, defining moral and ethical perspectives.
    
    Attributes:
        LAWFUL_GOOD (str): Follows law and strives to do good.
        NEUTRAL_GOOD (str): Does good without preference for law or chaos.
        CHAOTIC_GOOD (str): Acts with a free spirit, but with a desire to do good.
        LAWFUL_NEUTRAL (str): Respects law and order without bias toward good or evil.
        TRUE_NEUTRAL (str): Balanced and indifferent to good, evil, law, or chaos.
        CHAOTIC_NEUTRAL (str): Acts without regard for order, focusing on personal freedom.
        LAWFUL_EVIL (str): Follows law and order but seeks to do harm or serve evil purposes.
        NEUTRAL_EVIL (str): Pursues evil or self-serving goals without preference for law or chaos.
        CHAOTIC_EVIL (str): Seeks destruction and harm without regard for rules or order.
    """
    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    TRUE_NEUTRAL = "True Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"

class Rarity(str, Enum):
    """
    Enumeration of item rarity levels, classifying availability and value.

    Attributes:
        COMMON (str): Frequently found and easy to obtain.
        UNCOMMON (str): Less frequently found but still accessible.
        RARE (str): Harder to find and valuable.
        VERY_RARE (str): Highly valuable and challenging to acquire.
        LEGENDARY (str): Extremely rare and powerful, often linked to unique lore.
        UNIQUE (str): One-of-a-kind items with exceptional significance or power.
    """
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    VERY_RARE = "Very Rare"
    LEGENDARY = "Legendary"
    UNIQUE = "Unique"

class EventType(str, Enum):
    """
    Enumeration of event types for world-building and storytelling.

    Classifies the context and significance of occurrences in the world.
    
    Attributes:
        PERSONAL (str): Events of personal significance to characters.
        HISTORICAL (str): Important events in the world's history.
        QUEST (str): Events tied to missions or tasks undertaken by characters.
        COMBAT (str): Battles or conflicts between entities.
        SOCIAL (str): Social or political gatherings and interactions.
        ECONOMIC (str): Events related to trade, wealth, or economic shifts.
        NATURAL (str): Natural occurrences like weather changes or disasters.
        SUPERNATURAL (str): Events involving magic, divine intervention, or unearthly forces.
        COSMIC (str): Events of a grand scale, affecting the universe or dimensions.
    """
    PERSONAL = "Personal"
    HISTORICAL = "Historical"
    QUEST = "Quest"
    COMBAT = "Combat"
    SOCIAL = "Social"
    ECONOMIC = "Economic"
    NATURAL = "Natural"
    SUPERNATURAL = "Supernatural"
    COSMIC = "Cosmic"

# ----------------------------------------------
# Character, Item, and Relationship Models
# ----------------------------------------------

class CharacterRace(BaseEntity):
    """
    Represents a character's race with associated traits and ability bonuses.

    Attributes:
        traits (List[str]): List of racial traits or characteristics.
        ability_bonuses (Dict[str, int]): Ability score bonuses granted by the race.
    """
    traits: List[str] = Field(default_factory=list, description="Racial traits or characteristics associated with the race.")
    ability_bonuses: Dict[str, int] = Field(default_factory=dict, description="Ability score bonuses provided by the race.")

class CharacterClass(BaseEntity):
    """
    Represents a character's class, defining its role and abilities.

    Attributes:
        primary_ability (str): The main ability associated with the class.
        saving_throw_proficiencies (List[str]): Proficiencies in saving throws granted by the class.
        skill_proficiencies (List[str]): Skills the class grants proficiency in.
    """
    primary_ability: str = Field(..., description="Main ability associated with the class (e.g., Strength, Intelligence).")
    saving_throw_proficiencies: List[str] = Field(default_factory=list, description="Saving throw proficiencies granted by the class.")
    skill_proficiencies: List[str] = Field(default_factory=list, description="Skills that the class has proficiency in.")

class CharacterBackground(BaseEntity):
    """
    Represents a character's background, encapsulating life experiences and skills.

    Attributes:
        skill_proficiencies (List[str]): Skills acquired based on background.
        feature (str): Special feature or ability granted by the background.
    """
    skill_proficiencies: List[str] = Field(default_factory=list, description="Skills acquired based on background.")
    feature: str = Field(..., description="Special feature or ability granted by the background.")

class AbilityScore(BaseEntity):
    """
    Represents an ability score with its base value and derived modifier.

    Attributes:
        score (int): Base ability score (1-30).
        modifier (int): Modifier derived from the ability score.
    """
    score: int = Field(..., ge=1, le=30, description="Base ability score between 1 and 30.")
    modifier: int = Field(0, description="Modifier derived from the ability score.")

class CharacterAbilityScores(BaseEntity):
    """
    Encapsulates all six primary ability scores for a character.

    Attributes:
        strength (AbilityScore): Strength score and modifier.
        dexterity (AbilityScore): Dexterity score and modifier.
        constitution (AbilityScore): Constitution score and modifier.
        intelligence (AbilityScore): Intelligence score and modifier.
        wisdom (AbilityScore): Wisdom score and modifier.
        charisma (AbilityScore): Charisma score and modifier.
    """
    strength: AbilityScore
    dexterity: AbilityScore
    constitution: AbilityScore
    intelligence: AbilityScore
    wisdom: AbilityScore
    charisma: AbilityScore

class CharacterSkill(BaseEntity):
    """
    Represents an individual skill, tied to a specific ability.

    Attributes:
        ability (str): The ability score this skill is tied to (e.g., Dexterity).
        proficient (bool): Indicates if the character is proficient in the skill.
        expertise (bool): Indicates if the character has expertise in the skill.
    """
    ability: str = Field(..., description="The ability score this skill is tied to (e.g., Dexterity).")
    proficient: bool = Field(False, description="Indicates if the character is proficient in the skill.")
    expertise: bool = Field(False, description="Indicates if the character has expertise in the skill.")

class CharacterTrait(BaseEntity):
    """
    Represents a special trait that a character possesses.

    Attributes:
        impact (str): The potential impact of the trait on gameplay or narrative.
    """
    impact: str = Field("", description="The potential impact of the trait on gameplay or the narrative.")

class Item(BaseEntity):
    """
    Represents an in-game item with properties like rarity, weight, and value.

    Attributes:
        rarity (Rarity): The rarity level of the item.
        weight (float): Weight of the item in arbitrary units.
        value (int): Monetary or barter value of the item.
    """
    rarity: Rarity
    weight: float = Field(0, ge=0, description="Weight of the item in arbitrary units.")
    value: int = Field(0, ge=0, description="Monetary or barter value of the item.")

class Relationship(BaseEntity):
    """
    Represents a relationship between characters or entities.

    Attributes:
        target_id (str): The ID of the entity this relationship is with.
        type (str): Type of relationship (e.g., Friend, Rival).
        strength (int): Strength of the relationship on a scale of -100 to 100.
    """
    type: str = Field(..., description="Type of relationship (e.g., Friend, Rival).")
    strength: int = Field(..., ge=-100, le=100, description="Strength of the relationship on a scale of -100 to 100.")

class CharacterSheet(BaseEntity):
    """
    Comprehensive model encapsulating all details about a character.

    Attributes:
        race (CharacterRace): The character's race.
        character_class (CharacterClass): The character's class.
        background (CharacterBackground): The character's background.
        level (int): Character's current level.
        experience (int): Experience points accumulated by the character.
        alignment (Alignment): Character's moral and ethical alignment.
        ability_scores (CharacterAbilityScores): Character's ability scores.
        skills (List[CharacterSkill]): List of the character's skills.
        traits (List[CharacterTrait]): List of character-specific traits.
        inventory (List[Item]): Items currently held by the character.
        relationships (List[Relationship]): Relationships with other characters.
        backstory (str): The character's personal backstory.
        notes (str): General notes or additional information.
    """
    race: CharacterRace
    character_class: CharacterClass
    background: CharacterBackground
    level: int = Field(1, ge=1, description="Character's level, starting at 1.")
    experience: int = Field(0, ge=0, description="Experience points accumulated by the character.")
    alignment: Alignment
    ability_scores: CharacterAbilityScores
    skills: List[CharacterSkill] = Field(default_factory=list, description="List of the character's skills.")
    traits: List[CharacterTrait] = Field(default_factory=list, description="List of character-specific traits.")
    inventory: List[Item] = Field(default_factory=list, description="Items currently held by the character.")
    relationships: List[Relationship] = Field(default_factory=list, description="Relationships with other characters.")
    backstory: str = Field("", description="The character's personal backstory.")
    notes: str = Field("", description="General notes or additional information.")

# ----------------------------------------------
# Location, Faction, and Event Models
# ----------------------------------------------

class Location(BaseEntity):
    """
    Represents a location within the world.

    Attributes:
        type (str): Type of location (e.g., City, Forest, Dungeon).
        inhabitants (List[str]): List of entities inhabiting this location.
        points_of_interest (List[str]): Notable locations or landmarks within this area.
        government_type (Optional[str]): Type of government overseeing the location.
        wealth (Optional[int]): Wealth level of the location, on a scale of 1-10.
        climate (Optional[str]): The general climate of the location.
    """
    type: str = Field(..., description="Type of location (e.g., City, Forest, Dungeon).")
    inhabitants: List[str] = Field(default_factory=list, description="List of entities inhabiting this location.")
    points_of_interest: List[str] = Field(default_factory=list, description="Notable locations or landmarks within this area.")
    government_type: Optional[str] = Field(None, description="Type of government overseeing the location.")
    wealth: Optional[int] = Field(None, ge=1, le=10, description="Wealth level of the location, on a scale of 1-10.")
    climate: Optional[str] = Field(None, description="The general climate of the location.")

class Faction(BaseEntity):
    """
    Represents a faction within the world.

    Attributes:
        leader (str): ID of the entity that leads the faction.
        members (List[str]): List of faction members.
        goals (List[str]): Goals or objectives the faction strives for.
        resources (List[str]): Resources or assets the faction controls.
    """
    leader: str = Field(..., description="ID of the entity that leads the faction.")
    members: List[str] = Field(default_factory=list, description="List of faction members.")
    goals: List[str] = Field(default_factory=list, description="Goals or objectives the faction strives for.")
    resources: List[str] = Field(default_factory=list, description="Resources or assets the faction controls.")

class Event(BaseEntity):
    """
    Represents significant occurrences in the timeline.

    Attributes:
        event_type (EventType): Type of event that occurred.
        date (datetime): Date and time the event took place.
        location (str): Location where the event occurred.
        participants (List[str]): List of participants involved in the event.
        consequences (List[str]): Consequences or outcomes of the event.
        related_items (List[str]): Items that played a role in the event.
        lasting_effects (str): Any long-lasting consequences of the event.
    """
    event_type: EventType = Field(..., description="Type of event that occurred.")
    date: datetime = Field(..., description="Date and time the event took place.")
    location: str = Field(..., description="Location where the event occurred.")
    participants: List[str] = Field(default_factory=list, description="List of participants involved in the event.")
    consequences: List[str] = Field(default_factory=list, description="Consequences or outcomes of the event.")
    related_items: List[str] = Field(default_factory=list, description="Items involved in the event.")
    lasting_effects: str = Field("", description="Any long-lasting consequences of the event.")

# ----------------------------------------------
# World and Universe Models
# ----------------------------------------------

class WorldSheet(BaseEntity):
    """
    Comprehensive model for world-building.

    Attributes:
        locations (List[Location]): List of all major locations in the world.
        factions (List[Faction]): List of factions present in the world.
        events (List[Event]): Major events that occurred within the world.
        characters (List[str]): List of characters present in the world.
        items (List[str]): List of notable items in the world.
        lore (str): General lore or history of the world.
        notes (str): Additional notes or general information.
    """
    locations: List[Location] = Field(default_factory=list, description="List of all major locations in the world.")
    factions: List[Faction] = Field(default_factory=list, description="List of factions present in the world.")
    events: List[Event] = Field(default_factory=list, description="Major events that occurred within the world.")
    characters: List[str] = Field(default_factory=list, description="List of characters present in the world.")
    items: List[str] = Field(default_factory=list, description="List of notable items in the world.")
    lore: str = Field("", description="General lore or history of the world.")
    notes: str = Field("", description="Additional notes or general information.")

class UniverseSheet(BaseEntity):
    """
    Comprehensive model for universe-building.

    Attributes:
        dimensions (List[Dimension]): List of dimensions within the universe.
        timeline (List[Event]): Events spanning across the universe's timeline.
        cosmic_entities (List[str]): Notable cosmic entities present in the universe.
        universal_laws (List[str]): Universal laws governing physics or magic in the universe.
        notes (str): Additional notes or information.
    """
    dimensions: List[str] = Field(default_factory=list, description="List of dimensions within the universe.")
    timeline: Optional[Union[str, int]] = Field(None, description="Timeline the universe is associated with.")
    cosmic_entities: List[str] = Field(default_factory=list, description="Notable cosmic entities present in the universe.")
    universal_laws: List[str] = Field(default_factory=list, description="Universal laws governing physics or magic in the universe.")
    notes: str = Field("", description="Additional notes or information.")

# ----------------------------------------------
# Rule, Scenario, and Simulation Models
# ----------------------------------------------

class Rule(BaseEntity):
    """
    Rule defines the mechanics or logic governing gameplay, scenarios, or interactions.
    
    Attributes:
        mechanics (Dict[str, Union[int, str, bool]]): Key mechanics or parameters governed by the rule.
    """
    mechanics: Dict[str, Union[int, str, bool]] = Field(default_factory=dict, description="Key mechanics or parameters governed by the rule.")

class Scenario(BaseEntity):
    """
    Scenarios represent key interactive scenes or situations within the game.

    Attributes:
        location (str): Location where the scenario takes place.
        characters (List[str]): List of characters involved in the scenario.
        objectives (List[str]): Goals or objectives for this scenario.
        challenges (List[str]): Challenges or obstacles present in the scenario.
    """
    location: str = Field(..., description="Location where the scenario takes place.")
    characters: List[str] = Field(default_factory=list, description="List of characters involved in the scenario.")
    objectives: List[str] = Field(default_factory=list, description="Goals or objectives for this scenario.")
    challenges: List[str] = Field(default_factory=list, description="Challenges or obstacles present in the scenario.")

class SimulationSheet(BaseEntity):
    """
    Comprehensive model for simulation, encapsulating rules, scenarios, and active elements in the world.

    Attributes:
        rules (List[Rule]): List of rules governing the simulation.
        scenarios (List[Scenario]): List of scenarios currently active within the simulation.
        active_characters (List[str]): Characters currently engaged in the simulation.
        current_world (str): The world where the current simulation is taking place.
        game_master_notes (str): Additional notes or observations from the game master.
    """
    rules: List[Rule] = Field(default_factory=list, description="Rules governing the simulation.")
    scenarios: List[Scenario] = Field(default_factory=list, description="Scenarios currently active within the simulation.")
    active_characters: List[str] = Field(default_factory=list, description="Characters currently engaged in the simulation.")
    current_world: str = Field(..., description="The world where the current simulation is taking place.")
    game_master_notes: str = Field("", description="Additional notes or observations from the game master.")

# ----------------------------------------------
# Dynamic Memory Models
# ----------------------------------------------

class Memories(BaseEntity):
    """
    Memory model stores memories or experiences linked to a specific entity.

    Attributes:
        memory_string (str): Detailed memory or experience associated with an entity.
        associated_entity_id (str): ID of the entity that this memory belongs to.
        event_id (Optional[str]): Optionally associate the memory with an event.
        location_id (Optional[str]): Optionally associate the memory with a location.
    """
    memory_string: str = Field(..., description="Detailed memory or experience to be associated with an entity.")
    associated_entity_id: str = Field(..., description="ID of the entity that this memory belongs to.")
    event_id: Optional[str] = Field(None, description="Optionally associate the memory with an event.")
    location_id: Optional[str] = Field(None, description="Optionally associate the memory with a location.")
    timeline: Optional[Union[str, int]] = Field(None, description="Timeline the memory is associated with.")
    timestamp: Optional[Union[str, int]] = Field(None, description="Time of the memory's significance.")
