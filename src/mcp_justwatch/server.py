"""MCP server for JustWatch streaming availability data using FastMCP."""

import logging
import os
from typing import Optional

from fastmcp import FastMCP
from fastmcp.server.auth import OAuthProvider
from simplejustwatchapi import justwatch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configure OAuth if running in HTTP mode (remote deployment)
base_url = os.environ.get("MCP_BASE_URL")
auth_provider = None
if base_url:
    auth_provider = OAuthProvider(base_url=base_url)
    logger.info(f"OAuth enabled with base URL: {base_url}")

# Initialize FastMCP server
mcp = FastMCP("mcp-justwatch", auth=auth_provider)


def format_media_entry(entry, index: Optional[int] = None) -> str:
    """Format a MediaEntry object as a readable string."""
    lines = []

    # Add index if provided
    if index is not None:
        lines.append(f"\n{index}. ")
    else:
        lines.append("\n")

    # Basic information
    lines.append(f"Title: {entry.title}")
    lines.append(f"  Entry ID: {entry.entry_id}")
    lines.append(f"  Type: {entry.object_type}")

    if entry.release_year:
        lines.append(f"  Release Year: {entry.release_year}")

    if entry.release_date:
        lines.append(f"  Release Date: {entry.release_date}")

    # Runtime
    if entry.runtime_minutes:
        hours = entry.runtime_minutes // 60
        minutes = entry.runtime_minutes % 60
        if hours > 0:
            lines.append(f"  Runtime: {hours}h {minutes}m")
        else:
            lines.append(f"  Runtime: {minutes}m")

    # Genres
    if entry.genres:
        genres_str = ", ".join(entry.genres)
        lines.append(f"  Genres: {genres_str}")

    # Scores
    if hasattr(entry, "scoring") and entry.scoring:
        if entry.scoring.imdb_score:
            lines.append(f"  IMDb Score: {entry.scoring.imdb_score}/10")
        if entry.scoring.tmdb_score:
            lines.append(f"  TMDb Score: {entry.scoring.tmdb_score}/10")

    # Streaming offers
    if entry.offers:
        lines.append(f"  Available on {len(entry.offers)} platform(s):")
        for offer in entry.offers:
            offer_line = f"    - {offer.package.name}"
            details_parts = []
            if offer.monetization_type:
                details_parts.append(offer.monetization_type)
            if offer.presentation_type:
                details_parts.append(offer.presentation_type)
            if offer.price_string:
                details_parts.append(f"Price: {offer.price_string}")
            if details_parts:
                offer_line += f" ({', '.join(details_parts)})"
            if offer.url:
                offer_line += f"\n      URL: {offer.url}"
            lines.append(offer_line)
    else:
        lines.append("  No streaming offers available")

    return "\n".join(lines)


@mcp.tool()
def search_content(
    query: str,
    country: str = "US",
    language: str = "en",
    count: int = 5,
    best_only: bool = True,
) -> str:
    """Search for movies and TV shows on JustWatch with streaming availability.

    Args:
        query: The title to search for (movie or TV show)
        country: Two-letter ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'DE')
        language: ISO 639-1 language code (e.g., 'en', 'es', 'fr')
        count: Maximum number of results to return (1-20)
        best_only: Return only best quality offers per platform

    Returns:
        Formatted search results with streaming availability
    """
    try:
        # Normalize country to uppercase and language to lowercase
        country = country.upper()
        language = language.lower()

        # Clamp count to reasonable range
        count = max(1, min(count, 20))

        logger.info(f"Searching for '{query}' in {country} (language: {language})")

        results = justwatch.search(
            title=query, country=country, language=language, count=count, best_only=best_only
        )

        if not results:
            return f"No results found for '{query}' in {country}."

        # Format the results
        output_lines = [f"Search results for '{query}' in {country} ({len(results)} result(s)):\n"]

        for idx, entry in enumerate(results, 1):
            output_lines.append(format_media_entry(entry, idx))

        return "\n".join(output_lines)

    except Exception as e:
        logger.error(f"Error searching for content: {e}", exc_info=True)
        return f"Error searching for content: {str(e)}"


@mcp.tool()
def get_details(
    node_id: str,
    country: str = "US",
    language: str = "en",
    best_only: bool = True,
) -> str:
    """Get detailed information about a specific movie or TV show using its JustWatch node ID.

    Args:
        node_id: The JustWatch node ID (obtained from search results, e.g., 'tm12345')
        country: Two-letter ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'DE')
        language: ISO 639-1 language code (e.g., 'en', 'es', 'fr')
        best_only: Return only best quality offers per platform

    Returns:
        Detailed information about the content with streaming offers
    """
    try:
        # Normalize country to uppercase and language to lowercase
        country = country.upper()
        language = language.lower()

        logger.info(f"Getting details for node ID '{node_id}' in {country}")

        entry = justwatch.details(
            node_id=node_id, country=country, language=language, best_only=best_only
        )

        if not entry:
            return f"No details found for node ID '{node_id}' in {country}."

        output_lines = [f"Details for content in {country}:\n"]
        output_lines.append(format_media_entry(entry))

        return "\n".join(output_lines)

    except Exception as e:
        logger.error(f"Error getting details: {e}", exc_info=True)
        return f"Error getting details: {str(e)}"


@mcp.tool()
def get_offers_for_countries(
    node_id: str,
    countries: list[str],
    language: str = "en",
    best_only: bool = True,
) -> str:
    """Get streaming offers for specific content across multiple countries.

    Args:
        node_id: The JustWatch node ID (from search results)
        countries: List of two-letter country codes (e.g., ['US', 'GB', 'CA', 'AU'])
        language: ISO 639-1 language code (e.g., 'en', 'es', 'fr')
        best_only: Return only best quality offers per platform

    Returns:
        Streaming offers organized by country
    """
    try:
        # Convert list to set and ensure uppercase
        countries_set = {c.upper() for c in countries}
        language = language.lower()

        logger.info(f"Getting offers for node ID '{node_id}' in countries: {countries_set}")

        offers_dict = justwatch.offers_for_countries(
            node_id=node_id, countries=countries_set, language=language, best_only=best_only
        )

        if not offers_dict:
            return f"No offers found for node ID '{node_id}'."

        output_lines = ["Streaming offers across countries:\n"]

        for country in sorted(countries_set):
            offers_list = offers_dict.get(country, [])
            output_lines.append(f"\n{country}:")
            if offers_list:
                for offer in offers_list:
                    offer_line = f"  - {offer.package.name}"
                    details_parts = []
                    if offer.monetization_type:
                        details_parts.append(offer.monetization_type)
                    if offer.presentation_type:
                        details_parts.append(offer.presentation_type)
                    if offer.price_string:
                        details_parts.append(f"Price: {offer.price_string}")
                    if details_parts:
                        offer_line += f" ({', '.join(details_parts)})"
                    if offer.url:
                        offer_line += f"\n    URL: {offer.url}"
                    output_lines.append(offer_line)
            else:
                output_lines.append("  No offers available")

        return "\n".join(output_lines)

    except Exception as e:
        logger.error(f"Error getting offers: {e}", exc_info=True)
        return f"Error getting offers: {str(e)}"


def main():
    """Entry point for the MCP server."""
    if base_url:
        port = int(os.environ.get("PORT", "10000"))
        logger.info(f"Starting HTTP server on port {port}")
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
