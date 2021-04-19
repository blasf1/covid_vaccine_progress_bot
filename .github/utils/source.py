"""Get the source file to update the information of a country."""


# =============================================================================
# Imports
# =============================================================================

# Standard
import sys


# =============================================================================
# Constants
# =============================================================================

# Map the country name to the country source file
COUNTRIES = { 
    "Austria": "austria",
    "Belgium": "belgium",
    "Bulgaria": "bulgaria",
    "Croatia": "croatia",
    "Cyprus": "cyprus",
    "Czechia": "czechia",
    "Denmark": "denmark",
    "Estonia": "estonia",
    "Finland": "finland",
    "France": "france",
    "Germany": "germany",
    "Greece": "greece",
    "Ireland": "ireland",
    "Hungary": "hungary",
    "Italy": "italy",
    "Latvia": "latvia",
    "Lithuania": "lithuania",
    "Luxembourg": "luxembourg",
    "Malta": "malta",
    "Netherlands": "netherlands",
    "Poland": "poland",
    "Portugal": "portugal",
    "Romania": "romania",
    "Slovakia": "slovakia",
    "Slovenia": "slovenia",
    "Spain": "spain",
    "Sweden": "sweden"
}


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    # Parse the command line arguments
    _, country = sys.argv

    source_file = COUNTRIES[country]

    print(source_file)
