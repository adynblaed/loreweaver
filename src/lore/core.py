"""
src/lore/core.py

Foundations for Dynamic Lore and Worldbuilding via Advanced Data Models

This module provides a flexible, scalable, and well-structured set of Pydantic data models
designed to define the core elements of worldbuilding and lore creation. The models support 
the development of intricate, dynamic storytelling environments, including characters, events, 
locations, and other narrative elements that form the foundation of any custom universe.

Key Features:
- Modular "lore-core" elements representing atomic narrative components such as characters, locations, events, items, memories, and relationships.
- Scalable architecture for building data structures that support everything from single elements 
  to complex world simulations and interconnected universes.
- Flexible integration with various narrative contexts, including tabletop RPGs, open-world video 
  games, and expansive storytelling projects, allowing for both system-driven and creative world-building.
- Extensible framework for adding custom rules, simulations, and scenarios that can evolve with 
  your worlds over time, supporting continuity and depth across multiple projects or universes.

These LoreCore data models are designed to empower developers, world builders, authors, and game masters
to create rich, dynamic universes with narrative continuity. Whether you're building a single character 
arc or an entire timeline of events, this framework allows you to bring your lore to life in a 
structured yet creative way.

Author: Adyn Blaed
Project: HyperTech LoreCore
Date: Saturday, September 7th, 2024
Version: v1.0
"""

import uuid
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from slugify import slugify

# ----------------------------------------------
# Base Models and Mixins
# ----------------------------------------------

class VersionControl(BaseModel):
    """
    Model to track version history and branching of an entity for rollback and alternate timeline support.

    Attributes:
        version_id (UUID): Unique identifier for this version.
        parent_version (Optional[UUID]): UUID of the parent version (for branching).
        timestamp (datetime): Timestamp when this version was created.
        changes (Dict[str, Any]): Dictionary of changes made in this version.
        author (str): Author responsible for changes.
    """
    version_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for this version")
    parent_version: Optional[uuid.UUID] = Field(None, description="UUID of the parent version (for branching)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when this version was created")
    changes: Dict[str, Any] = Field(..., description="Dictionary of changes made in this version")
    author: str = Field(..., description="Author responsible for changes")

class VersionedEntityMixin(BaseModel):
    """
    Mixin for versioning and history tracking.

    Attributes:
        version (int): Version number of the entity.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        change_log (List[str]): Log of changes made to the entity.
        version_history (List[VersionControl]): List of version control history entries.
    """
    version: int = Field(1, description="Version number of the entity")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    change_log: List[str] = Field(default_factory=list, description="Log of changes made to the entity")
    version_history: List[VersionControl] = Field(default_factory=list, description="List of version control history entries")

class LocalizedString(BaseModel):
    """
    Model for localized strings supporting multiple languages.

    Attributes:
        default (str): Default language string.
        translations (Dict[str, str]): Translations keyed by language code.
    """
    default: str = Field(..., description="Default language string")
    translations: Dict[str, str] = Field(default_factory=dict, description="Translations keyed by language code")

class Tag(BaseModel):
    """
    Model for structured tagging system.

    Attributes:
        category (str): Category of the tag.
        value (str): Value of the tag.
    """
    category: str = Field(..., description="Category of the tag")
    value: str = Field(..., description="Value of the tag")

class BaseEntity(VersionedEntityMixin):
    """
    Base entity model providing core attributes for all game elements. This model is designed 
    to be flexible, allowing for both system-driven fields (e.g., UUIDs, timestamps) and 
    world-building-friendly attributes (e.g., canonical names, custom time formats).

    Attributes:
        uuid (Union[uuid.UUID, str, int]): Unique identifier for the entity. Can be a UUID, a string, or an integer.
        system_name (Union[str, int]): System-friendly name of the entity. Automatically generated if not provided.
        canonical_name (LocalizedString): The world-builder friendly name of the entity used for display or narrative purposes.
        description (Optional[LocalizedString]): A description of the entity. Can be localized for multiple languages.
        timeline (Optional[Union[uuid.UUID, str, int]]): The ID of the timeline the entity is associated with. 
        system_timestamp (Optional[datetime]): System-generated timestamp for technical tracking and real-world reference.").
        canonical_timestamp (Optional[Union[str, int]]): User-defined and entity-specific timestamp for continuity and canonical reference").
        metadata (Dict[str, Any]): Additional metadata for storing any extra information about the entity.
        tags (List[Tag]): A list of tags to categorize and filter entities.    
    """
    
    uuid: Union[str, int] = Field(default_factory=uuid.uuid4, description="Unique identifier for the entity. Can be UUID, string, or integer.")
    system_name: Union[str, int] = Field(None, description="System-friendly name of the entity. Auto-generated from uuid or canonical name if not provided.")
    canonical_name: 'LocalizedString' = Field(..., description="World-builder friendly canonical name of the entity, used for display or narrative purposes.")
    description: Optional['LocalizedString'] = Field(None, description="Description of the entity. Can be localized for multiple languages.")
    timeline: Optional[Union[str, int]] = Field(None, description="ID or name of the timeline this entity is associated with.")
    system_timestamp: Optional[datetime] = Field(None, description="System-generated timestamp for technical tracking and real-world reference (e.g., ISO 8601 format).")
    canonical_timestamp: Optional[Union[str, int]] = Field(None, description="User-defined or world-specific timestamp, allowing flexible formats (e.g., 'Epoch 5023', 'Year 200 of the Dawn Era').")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the entity, to store extra information.")
    tags: List['Tag'] = Field(default_factory=list, description="Tags for categorization and filtering of the entity.")

    def auto_set_slug(cls, values):
        """Generate slug from canonical_name if not provided."""
        if 'slug' not in values or not values['slug']:
            values['slug'] = slugify(values.get('canonical_name').default)
        return values

    def set_system_name(cls, v, values):
        """Use uuid as system_name if not provided."""
        return v or str(values.get('uuid'))

    def update_timestamp(self):
        """Update the 'updated_at' timestamp."""
        self.updated_at = datetime.utcnow()

    def add_change_log_entry(self, entry: str):
        """Add an entry to the change log."""
        self.change_log.append(f"{datetime.utcnow().isoformat()}: {entry}")
        self.update_timestamp()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary, useful for YAML serialization."""
        return {
            k: (v.dict() if isinstance(v, BaseModel) else v)
            for k, v in self.dict(exclude_none=True).items()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create an entity from a dictionary, useful for YAML deserialization."""
        return cls(**data)

    class Config:
        populate_by_name = True
        json_encoders = {
            uuid.UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat(),
        }

class RelationshipDynamic(BaseModel):
    """
    Represents the dynamic state of a relationship, which evolves over time.

    Attributes:
        trust (float): Trust level between entities.
        loyalty (float): Loyalty level between entities.
        familiarity (float): Familiarity level between entities.
        tension (float): Tension level between entities.
        shared_history (List[UUID]): List of events shared between the two entities.
    """
    trust: float = Field(0.0, ge=-1.0, le=1.0, description="Trust level between entities")
    loyalty: float = Field(0.0, ge=-1.0, le=1.0, description="Loyalty level between entities")
    familiarity: float = Field(0.0, ge=-1.0, le=1.0, description="Familiarity level between entities")
    tension: float = Field(0.0, ge=-1.0, le=1.0, description="Tension between entities")
    shared_history: List[uuid.UUID] = Field(default_factory=list, description="Event UUIDs that shape the relationship")

class Relationship(BaseModel):
    """
    Represents a relationship between two entities.

    Attributes:
        source_id (UUID): UUID of the source entity.
        target_id (UUID): UUID of the target entity.
        relationship_type (str): Type of relationship (e.g., Ally, Rival, Family).
        dynamics (RelationshipDynamic): Dynamic states of the relationship.
        notes (LocalizedString): Additional notes on the relationship.
    """
    source_id: uuid.UUID = Field(..., description="UUID of the source entity")
    target_id: uuid.UUID = Field(..., description="UUID of the target entity")
    relationship_type: str = Field(..., description="Type of relationship (e.g., Ally, Rival, Family)")
    dynamics: RelationshipDynamic = Field(..., description="Dynamic states of the relationship")
    notes: Optional[LocalizedString] = Field(None, description="Additional notes on the relationship")

# ----------------------------------------------
# Enumerations
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

class Locale(str, Enum):
    """
    Enumeration of supported locales for localization.

    Attributes:
        EN_US (str): English (United States).
        ES_ES (str): Spanish (Spain).
        FR_FR (str): French (France).
        DE_DE (str): German (Germany).
        JA_JP (str): Japanese (Japan).
    """
    EN_US = "en-US"
    ES_ES = "es-ES"
    FR_FR = "fr-FR"
    DE_DE = "de-DE"
    JA_JP = "ja-JP"

# ----------------------------------------------
# Character Models
# ----------------------------------------------

class CharacterRace(BaseEntity):
    """
    Represents a character's race with associated traits and ability bonuses.

    Attributes:
        traits (List[LocalizedString]): List of racial traits or characteristics.
        ability_bonuses (Dict[str, int]): Ability score bonuses granted by the race.
    """
    traits: List[LocalizedString] = Field(default_factory=list, description="Racial traits or characteristics associated with the race")
    ability_bonuses: Dict[str, int] = Field(default_factory=dict, description="Ability score bonuses provided by the race")

class CharacterClass(BaseEntity):
    """
    Represents a character's class, defining its role and abilities.

    Attributes:
        primary_ability (str): The main ability associated with the class.
        saving_throw_proficiencies (List[str]): Proficiencies in saving throws granted by the class.
        skill_proficiencies (List[str]): Skills the class grants proficiency in.
    """
    primary_ability: str = Field(..., description="Main ability associated with the class (e.g., Strength, Intelligence)")
    saving_throw_proficiencies: List[str] = Field(default_factory=list, description="Saving throw proficiencies granted by the class")
    skill_proficiencies: List[str] = Field(default_factory=list, description="Skills that the class has proficiency in")

class CharacterBackground(BaseEntity):
    """
    Represents a character's background, encapsulating life experiences and skills.

    Attributes:
        skill_proficiencies (List[str]): Skills acquired based on background.
        feature (LocalizedString): Special feature or ability granted by the background.
    """
    skill_proficiencies: List[str] = Field(default_factory=list, description="Skills acquired based on background")
    feature: LocalizedString = Field(..., description="Special feature or ability granted by the background")

class AbilityScore(BaseModel):
    """
    Represents an ability score with its base value and derived modifier.

    Attributes:
        score (int): Base ability score (1-30).
        modifier (int): Modifier derived from the ability score.
    """
    score: int = Field(..., ge=1, le=30, description="Base ability score between 1 and 30")
    modifier: int = Field(0, description="Modifier derived from the ability score")

    def calculate_modifier(cls, v, values):
        """Calculates the ability modifier from the score."""
        if 'score' in values:
            return (values['score'] - 10) // 2
        return v

class CharacterAbilityScores(BaseModel):
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
    ability: str = Field(..., description="The ability score this skill is tied to (e.g., Dexterity)")
    proficient: bool = Field(False, description="Indicates if the character is proficient in the skill")
    expertise: bool = Field(False, description="Indicates if the character has expertise in the skill")

class CharacterTrait(BaseEntity):
    """
    Represents a special trait that a character possesses.

    Attributes:
        impact (LocalizedString): The potential impact of the trait on gameplay or narrative.
    """
    impact: LocalizedString = Field(default_factory=LocalizedString, description="The potential impact of the trait on gameplay or narrative")

class CharacterVoice(BaseModel):
    """
    Represents the unique voice and dialogue style of a character.

    Attributes:
        speech_patterns (List[str]): Common speech patterns or phrases.
        tone (str): Overall tone of the character's speech.
        vocabulary (List[str]): Unique or characteristic words used by the character.
    """
    speech_patterns: List[str] = Field(default_factory=list, description="Common speech patterns or phrases")
    tone: str = Field(..., description="Overall tone of the character's speech")
    vocabulary: List[str] = Field(default_factory=list, description="Unique or characteristic words used by the character")

class CharacterArc(BaseModel):
    """
    Represents a character's development arc over time.

    Attributes:
        starting_state (LocalizedString): Initial state or personality of the character.
        key_events (List[UUID]): UUIDs of events crucial to character development.
        ending_state (LocalizedString): Final or current state of the character's development.
    """
    starting_state: LocalizedString = Field(..., description="Initial state or personality of the character")
    key_events: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of events crucial to character development")
    ending_state: LocalizedString = Field(..., description="Final or current state of the character's development")

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
        inventory (List[UUID]): Items currently held by the character.
        relationships (List[Relationship]): Relationships with other characters.
        backstory (LocalizedString): The character's personal backstory.
        voice (CharacterVoice): The character's unique voice and dialogue style.
        character_arc (CharacterArc): The character's development arc.
        notes (LocalizedString): General notes or additional information.
    """
    race: CharacterRace
    character_class: CharacterClass
    background: CharacterBackground
    level: int = Field(1, ge=1, description="Character's level, starting at 1")
    experience: int = Field(0, ge=0, description="Experience points accumulated by the character")
    alignment: Alignment
    ability_scores: CharacterAbilityScores
    skills: List[CharacterSkill] = Field(default_factory=list, description="List of the character's skills")
    traits: List[CharacterTrait] = Field(default_factory=list, description="List of character-specific traits")
    inventory: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of items held by the character")
    relationships: List[Relationship] = Field(default_factory=list, description="Relationships with other characters")
    backstory: LocalizedString = Field(default_factory=LocalizedString, description="The character's personal backstory")
    voice: CharacterVoice = Field(..., description="The character's unique voice and dialogue style")
    character_arc: CharacterArc = Field(..., description="The character's development arc")
    notes: LocalizedString = Field(default_factory=LocalizedString, description="General notes or additional information")

# ----------------------------------------------
# Item Models
# ----------------------------------------------

class ItemEvolution(BaseModel):
    """
    Represents the evolution of an item over time or through specific events.

    Attributes:
        stages (List[Dict[str, Any]]): List of evolution stages with their properties.
        current_stage (int): Index of the current evolution stage.
        evolution_trigger (Optional[str]): Condition that triggers evolution to the next stage.
    """
    stages: List[Dict[str, Any]] = Field(..., description="List of evolution stages with their properties")
    current_stage: int = Field(0, description="Index of the current evolution stage")
    evolution_trigger: Optional[str] = Field(None, description="Condition that triggers evolution to the next stage")

class ItemCraftingRecipe(BaseModel):
    """
    Represents a recipe for crafting an item.

    Attributes:
        ingredients (List[Dict[UUID, int]]): List of required ingredient UUIDs and quantities.
        tools (List[UUID]): List of required tool UUIDs.
        skill_requirements (Dict[str, int]): Required skills and their minimum levels.
        crafting_time (int): Time required to craft the item in minutes.
        difficulty (int): Difficulty of crafting on a scale of 1-100.
    """
    ingredients: List[Dict[uuid.UUID, int]] = Field(..., description="List of required ingredient UUIDs and quantities")
    tools: List[uuid.UUID] = Field(default_factory=list, description="List of required tool UUIDs")
    skill_requirements: Dict[str, int] = Field(default_factory=dict, description="Required skills and their minimum levels")
    crafting_time: int = Field(..., description="Time required to craft the item in minutes")
    difficulty: int = Field(..., ge=1, le=100, description="Difficulty of crafting on a scale of 1-100")

class Item(BaseEntity):
    """
    Represents an in-game item with properties like rarity, weight, and value.

    Attributes:
        rarity (Rarity): The rarity level of the item.
        weight (float): Weight of the item in arbitrary units.
        value (int): Monetary or barter value of the item.
        evolution (Optional[ItemEvolution]): Evolution stages of the item.
        crafting_recipe (Optional[ItemCraftingRecipe]): Recipe for crafting the item.
    """
    rarity: Rarity
    weight: float = Field(0, ge=0, description="Weight of the item in arbitrary units")
    value: int = Field(0, ge=0, description="Monetary or barter value of the item")
    evolution: Optional[ItemEvolution] = Field(None, description="Evolution stages of the item")
    crafting_recipe: Optional[ItemCraftingRecipe] = Field(None, description="Recipe for crafting the item")

# ----------------------------------------------
# Location Models
# ----------------------------------------------

class ClimateModel(BaseModel):
    """
    Represents the climate of a location.

    Attributes:
        temperature_range (Dict[str, float]): Temperature range for different seasons.
        precipitation (Dict[str, float]): Precipitation levels for different seasons.
        wind_patterns (Dict[str, str]): Wind patterns for different seasons.
        natural_disasters (List[str]): Possible natural disasters in the area.
    """
    temperature_range: Dict[str, float] = Field(..., description="Temperature range for different seasons")
    precipitation: Dict[str, float] = Field(..., description="Precipitation levels for different seasons")
    wind_patterns: Dict[str, str] = Field(..., description="Wind patterns for different seasons")
    natural_disasters: List[str] = Field(default_factory=list, description="Possible natural disasters in the area")

class LocationHistory(BaseModel):
    """
    Represents the historical changes of a location over time.

    Attributes:
        key_events (List[UUID]): UUIDs of significant events in the location's history.
        previous_names (List[LocalizedString]): Previous names of the location.
        major_changes (List[LocalizedString]): Major changes the location has undergone.
    """
    key_events: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of significant events in the location's history")
    previous_names: List[LocalizedString] = Field(default_factory=list, description="Previous names of the location")
    major_changes: List[LocalizedString] = Field(default_factory=list, description="Major changes the location has undergone")

class Location(BaseEntity):
    """
    Represents a location within the world.

    Attributes:
        type (str): Type of location (e.g., City, Forest, Dungeon).
        parent_location (Optional[UUID]): UUID of the parent location.
        sub_locations (List[UUID]): UUIDs of sub-locations within this location.
        inhabitants (List[UUID]): UUIDs of entities inhabiting this location.
        points_of_interest (List[LocalizedString]): Notable landmarks within this area.
        government_type (Optional[str]): Type of government overseeing the location.
        wealth (Optional[int]): Wealth level of the location, on a scale of 1-10.
        climate (ClimateModel): Climate model of the location.
        history (LocationHistory): Historical information about the location.
    """
    type: str = Field(..., description="Type of location (e.g., City, Forest, Dungeon)")
    parent_location: Optional[uuid.UUID] = Field(None, description="UUID of the parent location")
    sub_locations: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of sub-locations within this location")
    inhabitants: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of entities inhabiting this location")
    points_of_interest: List[LocalizedString] = Field(default_factory=list, description="Notable landmarks within this area")
    government_type: Optional[str] = Field(None, description="Type of government overseeing the location")
    wealth: Optional[int] = Field(None, ge=1, le=10, description="Wealth level of the location, on a scale of 1-10")
    climate: ClimateModel = Field(..., description="Climate model of the location")
    history: LocationHistory = Field(..., description="Historical information about the location")

# ----------------------------------------------
# Faction Models
# ----------------------------------------------

class FactionRank(BaseModel):
    """
    Represents a rank within a faction's hierarchy.

    Attributes:
        name (LocalizedString): Name of the rank.
        level (int): Numeric level of the rank within the hierarchy.
        responsibilities (List[LocalizedString]): Responsibilities associated with the rank.
        privileges (List[LocalizedString]): Privileges granted to members of this rank.
    """
    name: LocalizedString = Field(..., description="Name of the rank")
    level: int = Field(..., description="Numeric level of the rank within the hierarchy")
    responsibilities: List[LocalizedString] = Field(default_factory=list, description="Responsibilities associated with the rank")
    privileges: List[LocalizedString] = Field(default_factory=list, description="Privileges granted to members of this rank")

class FactionHierarchy(BaseModel):
    """
    Represents the internal structure and ranks of a faction.

    Attributes:
        ranks (List[FactionRank]): List of ranks within the faction.
        leadership_structure (LocalizedString): Description of how leadership is structured.
    """
    ranks: List[FactionRank] = Field(..., description="List of ranks within the faction")
    leadership_structure: LocalizedString = Field(..., description="Description of how leadership is structured")

class FactionDiplomacy(BaseModel):
    """
    Represents diplomatic relations between factions.

    Attributes:
        allies (List[UUID]): UUIDs of allied factions.
        enemies (List[UUID]): UUIDs of enemy factions.
        neutral (List[UUID]): UUIDs of factions with neutral relations.
        trade_agreements (List[UUID]): UUIDs of factions with trade agreements.
    """
    allies: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of allied factions")
    enemies: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of enemy factions")
    neutral: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of factions with neutral relations")
    trade_agreements: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of factions with trade agreements")

class Faction(BaseEntity):
    """
    Represents a faction within the world.

    Attributes:
        leader (UUID): UUID of the entity that leads the faction.
        members (List[UUID]): UUIDs of faction members.
        goals (List[LocalizedString]): Goals or objectives the faction strives for.
        resources (List[LocalizedString]): Resources or assets the faction controls.
        hierarchy (FactionHierarchy): Internal structure and ranks of the faction.
        diplomacy (FactionDiplomacy): Diplomatic relations with other factions.
    """
    leader: uuid.UUID = Field(..., description="UUID of the entity that leads the faction")
    members: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of faction members")
    goals: List[LocalizedString] = Field(default_factory=list, description="Goals or objectives the faction strives for")
    resources: List[LocalizedString] = Field(default_factory=list, description="Resources or assets the faction controls")
    hierarchy: FactionHierarchy = Field(..., description="Internal structure and ranks of the faction")
    diplomacy: FactionDiplomacy = Field(..., description="Diplomatic relations with other factions")

# ----------------------------------------------
# Event Models
# ----------------------------------------------

class EventImpact(BaseModel):
    """
    Represents the impact of an event on various entities in the world.

    Attributes:
        affected_characters (List[Dict[UUID, str]]): UUIDs of affected characters and descriptions of effects.
        affected_locations (List[Dict[UUID, str]]): UUIDs of affected locations and descriptions of effects.
        affected_factions (List[Dict[UUID, str]]): UUIDs of affected factions and descriptions of effects.
        world_changes (List[LocalizedString]): General changes to the world as a result of the event.
    """
    affected_characters: List[Dict[uuid.UUID, str]] = Field(default_factory=list, description="UUIDs of affected characters and descriptions of effects")
    affected_locations: List[Dict[uuid.UUID, str]] = Field(default_factory=list, description="UUIDs of affected locations and descriptions of effects")
    affected_factions: List[Dict[uuid.UUID, str]] = Field(default_factory=list, description="UUIDs of affected factions and descriptions of effects")
    world_changes: List[LocalizedString] = Field(default_factory=list, description="General changes to the world as a result of the event")

class Event(BaseEntity):
    """
    Represents significant occurrences in the timeline.

    Attributes:
        event_type (EventType): Type of event that occurred.
        date (datetime): Date and time the event took place.
        location (UUID): UUID of the location where the event occurred.
        participants (List[UUID]): UUIDs of participants involved in the event.
        consequences (List[LocalizedString]): Consequences or outcomes of the event.
        related_items (List[UUID]): UUIDs of items involved in the event.
        impact (EventImpact): Detailed impact of the event on the world and its entities.
    """
    event_type: EventType = Field(..., description="Type of event that occurred")
    date: datetime = Field(..., description="Date and time the event took place")
    location: uuid.UUID = Field(..., description="UUID of the location where the event occurred")
    participants: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of participants involved in the event")
    consequences: List[LocalizedString] = Field(default_factory=list, description="Consequences or outcomes of the event")
    related_items: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of items involved in the event")
    impact: EventImpact = Field(..., description="Detailed impact of the event on the world and its entities")

class EventChain(BaseModel):
    """
    Represents a chain of related events.

    Attributes:
        events (List[UUID]): UUIDs of events in the chain, in chronological order.
        causality (List[LocalizedString]): Descriptions of how each event led to the next.
    """
    events: List[uuid.UUID] = Field(..., description="UUIDs of events in the chain, in chronological order")
    causality: List[LocalizedString] = Field(default_factory=list, description="Descriptions of how each event led to the next")

# ----------------------------------------------
# World and Universe Models
# ----------------------------------------------

class WorldSheet(BaseEntity):
    """
    Comprehensive model for world-building.

    Attributes:
        locations (List[UUID]): UUIDs of all major locations in the world.
        factions (List[UUID]): UUIDs of factions present in the world.
        events (List[UUID]): UUIDs of major events that occurred within the world.
        characters (List[UUID]): UUIDs of characters present in the world.
        items (List[UUID]): UUIDs of notable items in the world.
        lore (LocalizedString): General lore or history of the world.
        notes (LocalizedString): Additional notes or general information.
    """
    locations: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of all major locations in the world")
    factions: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of factions present in the world")
    events: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of major events that occurred within the world")
    characters: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of characters present in the world")
    items: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of notable items in the world")
    lore: LocalizedString = Field(default_factory=LocalizedString, description="General lore or history of the world")
    notes: LocalizedString = Field(default_factory=LocalizedString, description="Additional notes or general information")

class TimelineEvent(BaseModel):
    """
    Represents an event specifically tied to a point in the timeline.

    Attributes:
        event_id (UUID): UUID of the associated event.
        timestamp (datetime): Specific timestamp of the event in the timeline.
        significance (LocalizedString): Description of the event's significance in the timeline.
    """
    event_id: uuid.UUID = Field(..., description="UUID of the associated event")
    timestamp: datetime = Field(..., description="Specific timestamp of the event in the timeline")
    significance: LocalizedString = Field(..., description="Description of the event's significance in the timeline")

class TimelineNode(BaseModel):
    """
    Represents a node in a branching timeline, allowing for complex narrative progression.

    Attributes:
        event_id (UUID): UUID of the associated event.
        timestamp (datetime): Timestamp for when this node occurs.
        next_nodes (List[UUID]): UUIDs of potential future timeline nodes.
        previous_nodes (List[UUID]): UUIDs of previous timeline nodes.
        branch_probability (float): Likelihood of this branch being followed.
    """
    event_id: uuid.UUID = Field(..., description="UUID of the associated event")
    timestamp: datetime = Field(..., description="Timestamp for when this node occurs")
    next_nodes: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of potential future timeline nodes")
    previous_nodes: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of previous timeline nodes")
    branch_probability: float = Field(1.0, ge=0.0, le=1.0, description="Likelihood of this branch being followed")

class Timeline(BaseEntity):
    """
    Represents a timeline with support for branching and parallel timelines.

    Attributes:
        nodes (List[TimelineNode]): Nodes representing events in the timeline.
        active_branch (UUID): The currently active node in the timeline.
        convergence_points (List[UUID]): UUIDs of points where branches converge.
    """
    nodes: List[TimelineNode] = Field(default_factory=list, description="Nodes representing events in the timeline")
    active_branch: uuid.UUID = Field(..., description="The currently active node in the timeline")
    convergence_points: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of points where branches converge")

class UniverseSheet(BaseEntity):
    """
    Comprehensive model for universe-building.

    Attributes:
        dimensions (List[UUID]): UUIDs of dimensions within the universe.
        timelines (List[UUID]): UUIDs of timelines in the universe.
        cosmic_entities (List[UUID]): UUIDs of notable cosmic entities present in the universe.
        universal_laws (List[LocalizedString]): Universal laws governing physics or magic in the universe.
        notes (LocalizedString): Additional notes or information.
    """
    dimensions: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of dimensions within the universe")
    timelines: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of timelines in the universe")
    cosmic_entities: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of notable cosmic entities present in the universe")
    universal_laws: List[LocalizedString] = Field(default_factory=list, description="Universal laws governing physics or magic in the universe")
    notes: LocalizedString = Field(default_factory=LocalizedString, description="Additional notes or information")

# ----------------------------------------------
# Rule, Scenario, and Simulation Models
# ----------------------------------------------

class Rule(BaseEntity):
    """
    Defines the mechanics or logic governing gameplay, scenarios, or interactions.

    Attributes:
        mechanics (Dict[str, Union[int, str, bool]]): Key mechanics or parameters governed by the rule.
        applicability (List[str]): Contexts or situations where this rule applies.
        exceptions (List[LocalizedString]): Exceptions to the rule.
    """
    mechanics: Dict[str, Union[int, str, bool]] = Field(default_factory=dict, description="Key mechanics or parameters governed by the rule")
    applicability: List[str] = Field(default_factory=list, description="Contexts or situations where this rule applies")
    exceptions: List[LocalizedString] = Field(default_factory=list, description="Exceptions to the rule")

class Scenario(BaseEntity):
    """
    Represents key interactive scenes or situations within the game.

    Attributes:
        location (UUID): UUID of the location where the scenario takes place.
        characters (List[UUID]): UUIDs of characters involved in the scenario.
        objectives (List[LocalizedString]): Goals or objectives for this scenario.
        challenges (List[LocalizedString]): Challenges or obstacles present in the scenario.
        outcomes (List[LocalizedString]): Possible outcomes of the scenario.
    """
    location: uuid.UUID = Field(..., description="UUID of the location where the scenario takes place")
    characters: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of characters involved in the scenario")
    objectives: List[LocalizedString] = Field(default_factory=list, description="Goals or objectives for this scenario")
    challenges: List[LocalizedString] = Field(default_factory=list, description="Challenges or obstacles present in the scenario")
    outcomes: List[LocalizedString] = Field(default_factory=list, description="Possible outcomes of the scenario")

class SimulationParameter(BaseModel):
    """
    Represents a customizable parameter for world simulations.

    Attributes:
        name (str): Name of the parameter.
        value (Union[int, float, str, bool]): Current value of the parameter.
        description (LocalizedString): Description of what this parameter affects.
        range (Optional[Dict[str, Union[int, float]]]): Possible range of values for numeric parameters.
    """
    name: str = Field(..., description="Name of the parameter")
    value: Union[int, float, str, bool] = Field(..., description="Current value of the parameter")
    description: LocalizedString = Field(..., description="Description of what this parameter affects")
    range: Optional[Dict[str, Union[int, float]]] = Field(None, description="Possible range of values for numeric parameters")

class WorldSimulation(BaseEntity):
    """
    Represents a simulation of dynamic changes in the world.

    Attributes:
        world_id (UUID): UUID of the world being simulated.
        active_scenarios (List[UUID]): UUIDs of currently active scenarios.
        simulation_parameters (List[SimulationParameter]): Customizable parameters for the simulation.
        current_state (Dict[str, Any]): Current state of various aspects of the world.
        history (List[Dict[str, Any]]): History of changes in the world state.
    """
    world_id: uuid.UUID = Field(..., description="UUID of the world being simulated")
    active_scenarios: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of currently active scenarios")
    simulation_parameters: List[SimulationParameter] = Field(default_factory=list, description="Customizable parameters for the simulation")
    current_state: Dict[str, Any] = Field(default_factory=dict, description="Current state of various aspects of the world")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="History of changes in the world state")

class SimulationSheet(BaseEntity):
    """
    Comprehensive model for simulation, encapsulating rules, scenarios, and active elements in the world.

    Attributes:
        rules (List[UUID]): UUIDs of rules governing the simulation.
        scenarios (List[UUID]): UUIDs of scenarios currently active within the simulation.
        active_characters (List[UUID]): UUIDs of characters currently engaged in the simulation.
        current_world (UUID): UUID of the world where the current simulation is taking place.
        world_simulation (WorldSimulation): Current state and parameters of the world simulation.
        game_master_notes (LocalizedString): Additional notes or observations from the game master.
    """
    rules: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of rules governing the simulation")
    scenarios: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of scenarios currently active within the simulation")
    active_characters: List[uuid.UUID] = Field(default_factory=list, description="UUIDs of characters currently engaged in the simulation")
    current_world: uuid.UUID = Field(..., description="UUID of the world where the current simulation is taking place")
    world_simulation: WorldSimulation = Field(..., description="Current state and parameters of the world simulation")
    game_master_notes: LocalizedString = Field(default_factory=LocalizedString, description="Additional notes or observations from the game master")

# ----------------------------------------------
# Dynamic Memory Models
# ----------------------------------------------

class Memories(BaseEntity):
    """
    Represents a memory or experience linked to a specific entity.

    Attributes:
        memory_string (LocalizedString): Detailed memory or experience associated with an entity.
        associated_entity_id (UUID): UUID of the entity that this memory belongs to.
        event_id (Optional[UUID]): UUID of the associated event, if applicable.
        location_id (Optional[UUID]): UUID of the associated location, if applicable.
        emotional_impact (int): Emotional impact of the memory, from -100 to 100.
        recall_difficulty (int): Difficulty of recalling this memory, from 0 to 100.
    """
    memory_string: LocalizedString = Field(..., description="Detailed memory or experience associated with an entity")
    associated_entity_id: uuid.UUID = Field(..., description="UUID of the entity that this memory belongs to")
    event_id: Optional[uuid.UUID] = Field(None, description="UUID of the associated event, if applicable")
    location_id: Optional[uuid.UUID] = Field(None, description="UUID of the associated location, if applicable")
    emotional_impact: int = Field(0, ge=-100, le=100, description="Emotional impact of the memory, from -100 to 100")
    recall_difficulty: int = Field(0, ge=0, le=100, description="Difficulty of recalling this memory, from 0 to 100")
