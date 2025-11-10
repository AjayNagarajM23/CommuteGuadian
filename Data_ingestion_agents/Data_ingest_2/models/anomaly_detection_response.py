from pydantic import BaseModel, Field
from typing import Optional
import time

class CityAnomalyReport(BaseModel):
    """
    A comprehensive report combining anomaly detection details with location information and timestamp.
    """
    unix_timestamp: float = Field(
        description="The Unix timestamp uploaded from the user, representing the time of the anomaly detection event.",
    )

    # Anomaly Detection Fields (from SubAgent1OutPut)
    event_type: str = Field(
        description="""
        The classification of the event or anomaly detected in the image. 
        Examples include: 
        - 'Structural Damage': For issues like cracked buildings, broken bridges, deteriorating infrastructure.
        - 'Environmental Hazard': For pollution (air, water, noise), spills, illegal dumping, deforestation, natural disasters (flooding, landslides, fires).
        - 'Traffic Anomaly': For unusual traffic patterns, accidents, road blockages, illegal parking, malfunctioning traffic lights.
        - 'Unusual Activity': For suspicious gatherings, unexpected object placements, vandalism, loitering.
        - 'Infrastructure Issue': For problems with roads (potholes, sinkholes), streetlights (outages, damage), utilities (water pipe bursts, gas leaks, sewage blockages), damaged public amenities (benches, signs).
        - 'Public Safety Concern': For fires, crime scenes, hazardous situations (exposed wires, unstable structures), missing manhole covers, unsafe construction practices.
        - 'Weather-Related Damage': Specifically for issues caused by adverse weather like heavy rain (flooding, waterlogging, sewage overflow), storms (fallen trees, damaged power lines, structural impact).
        - 'Utility Disruption': For power outages, water supply interruptions, gas line issues, communication network failures.
        """
    )
    description: str = Field(
        description="""
        A concise yet comprehensive textual description of the anomaly or event observed in the image. 
        This should detail what is visible and why it is considered an anomaly. 
        For instance, "A large sinkhole has opened up in the middle of a residential street, 
        impeding traffic and posing a danger to pedestrians." or "Heavy rainfall has led to severe 
        waterlogging on Main Street, completely submerging vehicle tires and causing traffic jams, 
        with visible sewage overflow from drains."
        """
    )
    severity_level: str = Field(
        description="""
        The assessed level of severity for the detected anomaly, categorized as:
        - 'Low': Minimal impact, easily resolvable, minor inconvenience (e.g., small pothole, faded road marking).
        - 'Medium': Moderate impact, requires attention, potential for escalation if ignored, localized disruption 
                   (e.g., significant pothole, malfunctioning streetlight, minor traffic jam).
        - 'High': Significant impact, poses immediate danger, requires urgent intervention,
                  potential for widespread disruption or harm, critical infrastructure failure 
                  (e.g., major structural damage, widespread flooding, complete power outage, gas leak).
        """
    )

    # Address Details Fields (from AddressDetailsOutput)
    latitude: float = Field(description="The latitude coordinate where the anomaly was detected.")
    longitude: float = Field(description="The longitude coordinate where the anomaly was detected.")
    formatted_address: str = Field(
        description="The full, human-readable address string of the anomaly location (e.g., '1600 Amphitheatre Parkway, Mountain View, CA 94043, USA')."
    )
    house_number: Optional[str] = Field(
        default=None, description="The house or building number at the anomaly location, if available."
    )
    street_name: Optional[str] = Field(
        default=None, description="The name of the street or road at the anomaly location."
    )
    area_name: Optional[str] = Field(
        default=None, description="The name of the local area, neighborhood, or locality where the anomaly is."
    )
    city: Optional[str] = Field(
        default=None, description="The name of the city or town where the anomaly is."
    )
    district: Optional[str] = Field(
        default=None, description="The name of the district or county where the anomaly is, if applicable."
    )
    state: Optional[str] = Field(
        default=None, description="The name of the state, province, or administrative region where the anomaly is."
    )
    country: Optional[str] = Field(
        default=None, description="The name of the country where the anomaly is."
    )
    country_code: Optional[str] = Field(
        default=None, description="The two-letter ISO country code of the anomaly location (e.g., 'US', 'IN')."
    )
    postal_code: Optional[str] = Field(
        default=None, description="The postal code or ZIP code of the anomaly location."
    )