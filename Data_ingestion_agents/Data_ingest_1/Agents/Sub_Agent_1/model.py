from pydantic import BaseModel, Field
from typing import Optional

class SubAgent1OutPut(BaseModel):
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
        - 'Normal' : if there is no anomaly
        """
    )
    sub_event_type: Optional[str] = Field(
        default=None,
        description="""
        A more specific classification of the event or anomaly, especially when 'event_type' is 'Weather-Related Damage'.
        Examples for 'Weather-Related Damage' sub-event-types include: 'heavy rain', 'flooding', 'waterlogging',
        'sewage overflow', 'storms', 'fallen trees', 'damaged power lines', 'structural impact'.
        This field provides granular detail about the nature of the weather-related incident or other broad event types.
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
    severity_score: int = Field(
        description="""
        The 'severity_score' should be an integer between 1 and 10, based on the following detailed criteria:
        - Severity Score Criteria (1-10)
        Score 1-2 (Low Severity): Minimal Impact
        Human Safety: No immediate threat to life or limb. Minor inconvenience.
        Infrastructure: Very minor, localized cosmetic damage, easily repairable, no structural integrity issues.
        Services/Operations: No disruption to essential services. Very minor, localized traffic flow impedance, easily navigable.
        Scope/Scale: Isolated incident, affecting a very small area or single individual/object.
        Urgency: Can be addressed during routine maintenance.
        Examples: Small, shallow pothole on a low-traffic street; minor graffiti; broken, non-essential signage; a single flickering street light.
        - Score 3-4 (Moderate-Low Severity): Minor Impact
        Human Safety: Low potential for minor injury, but generally safe conditions.
        Infrastructure: Minor damage to property or non-critical public utilities, requiring repair but not immediate replacement.
        Services/Operations: Slight, temporary inconvenience to services or traffic flow. Traffic might need to slow down or navigate around, but no significant delays.
        Scope/Scale: Localized incident, affecting a small area or a few individuals/objects.
        Urgency: Should be addressed within a few days to a week.
        Examples: Medium-sized pothole on a moderately busy street; minor structural crack in a non-load-bearing wall; a few non-functional streetlights in an area that still has some lighting; overflowing small public waste bins.
        - Score 5-6 (Medium Severity): Noticeable Impact
        Human Safety: Moderate potential for minor to moderate injury; might require caution or minor detours for safety.
        Infrastructure: Noticeable damage to property or public utilities, potentially requiring significant repair or partial replacement.
        Services/Operations: Moderate disruption to services or traffic flow. Traffic delays, detours, or slow-downs. Could affect a small number of businesses.
        Scope/Scale: Affecting a street segment, a small neighborhood, or a moderate number of people.
        Urgency: Should be addressed within 24-48 hours.
        Examples: Large pothole causing vehicles to swerve significantly; broken traffic light at a less busy intersection; burst water pipe causing localized flooding on a sidewalk; significant, visible structural crack in a non-critical building element; moderate fallen tree obstructing a sidewalk.
        - Score 7-8 (Moderate-High Severity): Significant Impact
        Human Safety: High potential for serious injury; direct threat to public safety if not addressed promptly. Requires immediate caution or area closure
        Infrastructure: Severe damage to critical infrastructure (e.g., main roads, bridges, essential utility lines), requiring urgent and significant repair or complete replacement.
        Services/Operations: Major disruption to essential services (e.g., power outages for a few hours, significant water supply issues). Major traffic delays, road closures, or diversions impacting a wider area. Business operations severely affected.
        Scope/Scale: Affecting multiple streets, a significant portion of a neighborhood, or a large number of people.
        Urgency: Requires immediate attention and response (within hours).
        Examples: Complete road collapse; significant flooding submerging vehicles and disrupting major traffic routes; widespread power outage due to a damaged utility pole; large fallen tree completely blocking a main road; major structural damage to a building that poses a risk of collapse.
        - Score 9-10 (High Severity): Catastrophic/Critical Impact
        Human Safety: Imminent and severe threat to life and limb; requires immediate evacuation or complete area lockdown. Potential for mass casualties.
        Infrastructure: Catastrophic damage to critical, widespread infrastructure, requiring extensive and long-term reconstruction. Total failure of essential utilities.
        Services/Operations: Complete cessation of essential services for a prolonged period. Major, widespread, and prolonged traffic gridlock or complete closure of critical transport arteries. Entire communities or large business districts shut down.
        Scope/Scale: Affecting entire districts, multiple neighborhoods, or posing a regional threat.
        Urgency: Emergency response required immediately.
        Examples: Building collapse; large-scale flash flooding with rapid currents; widespread and prolonged power grid failure; chemical spill with immediate health risks; major bridge collapse; terrorist act aftermath.

    """
    )