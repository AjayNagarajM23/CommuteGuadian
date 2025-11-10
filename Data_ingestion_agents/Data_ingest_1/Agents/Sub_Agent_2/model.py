from pydantic import BaseModel, Field
from typing import Optional

# --- Pydantic Model for Reverse Geocoding Input ---
class ReverseGeocodeInput(BaseModel):
    """Input schema for the reverse_geocode_tool."""
    latitude: float = Field(description="The latitude coordinate for reverse geocoding.")
    longitude: float = Field(description="The longitude coordinate for reverse geocoding.")

# --- Pydantic Model for Address Details ---
class AddressDetailsOutput(BaseModel):
    """
    Represents the structured address details obtained from reverse geocoding coordinates.
    """
    latitude: float = Field(description="The latitude coordinate provided.")
    longitude: float = Field(description="The longitude coordinate provided.")
    formatted_address: str = Field(
        description="The full, human-readable address string (e.g., '1600 Amphitheatre Parkway, Mountain View, CA 94043, USA')."
    )
    house_number: Optional[str] = Field(
        default=None, description="The house or building number, if available."
    )
    street_name: Optional[str] = Field(
        default=None, description="The name of the street or road."
    )
    area_name: Optional[str] = Field(
        default=None, description="The name of the local area, neighborhood, or locality."
    )
    city: Optional[str] = Field(
        default=None, description="The name of the city or town."
    )
    district: Optional[str] = Field(
        default=None, description="The name of the district or county, if applicable."
    )
    state: Optional[str] = Field(
        default=None, description="The name of the state, province, or administrative region."
    )
    country: Optional[str] = Field(
        default=None, description="The name of the country."
    )
    country_code: Optional[str] = Field(
        default=None, description="The two-letter ISO country code (e.g., 'US', 'IN')."
    )
    postal_code: Optional[str] = Field(
        default=None, description="The postal code or ZIP code."
    )