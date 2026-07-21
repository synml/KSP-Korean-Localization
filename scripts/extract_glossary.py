"""현행 번역(GameData의 ko 사전)에서 용어별 대응 한국어를 추출해 용어집 재료를 만든다.

reference_english/ 사전에서 값이 용어와 정확히 일치(대소문자 무시, 끝의 ':' 무시)하는 키를
찾고, 같은 키의 한국어 값을 모아 빈도순으로 보여준다. docs/glossary.md 편집의
근거 자료용 (출력은 stdout).

사용법: python scripts/extract_glossary.py
"""

from __future__ import annotations

import sys
from collections import Counter

from ksploc import FILE_PAIRS, parse_dictionary

TERMS: dict[str, list[str]] = {
    "조종/비행": [
        "Stability Assist",
        "Prograde",
        "Retrograde",
        "Normal",
        "Antinormal",
        "Radial",
        "Radial In",
        "Radial Out",
        "Maneuver",
        "Maneuver Node",
        "Target",
        "Throttle",
        "Thrust",
        "Pitch",
        "Yaw",
        "Roll",
        "SAS",
        "RCS",
        "Brakes",
        "Gear",
        "Lights",
        "Abort",
        "Stage",
        "Trim",
        "Attitude",
    ],
    "궤도": [
        "Orbit",
        "Apoapsis",
        "Periapsis",
        "Inclination",
        "Eccentricity",
        "Ascending Node",
        "Descending Node",
        "Altitude",
        "Trajectory",
        "Escape",
        "Encounter",
        "Rendezvous",
        "Docking",
        "Undock",
        "Transfer",
        "Atmosphere",
        "Delta-V",
        "Delta-v",
        "Burn Time",
        "Time Warp",
        "Physics Warp",
        "Sub-Orbital",
        "Reentry",
    ],
    "기체/파트": [
        "Vessel",
        "Ship",
        "Craft",
        "Rocket",
        "Plane",
        "Probe",
        "Lander",
        "Rover",
        "Station",
        "Base",
        "Debris",
        "Part",
        "Parts",
        "Decoupler",
        "Separator",
        "Fairing",
        "Heat Shield",
        "Parachute",
        "Engine",
        "Fuel Tank",
        "Command Pod",
        "Docking Port",
        "Solar Panel",
        "Battery",
        "Antenna",
        "Reaction Wheel",
        "Landing Legs",
        "Wheels",
        "Intake",
        "Control Surface",
        "Ladder",
        "Strut",
        "Fuel Line",
        "Winglet",
    ],
    "자원": [
        "Liquid Fuel",
        "Oxidizer",
        "Monopropellant",
        "Solid Fuel",
        "Electric Charge",
        "Ore",
        "Xenon Gas",
        "Ablator",
        "Intake Air",
        "EVA Propellant",
    ],
    "과학/커리어": [
        "Science",
        "Funds",
        "Reputation",
        "Contract",
        "Contracts",
        "Experiment",
        "Crew Report",
        "EVA Report",
        "Surface Sample",
        "Biome",
        "Situation",
        "Recover",
        "Transmit",
        "Strategy",
        "Milestone",
        "Upgrade",
        "Research",
        "Technology",
    ],
    "시설": [
        "Vehicle Assembly Building",
        "Spaceplane Hangar",
        "Runway",
        "Launch Pad",
        "Launchpad",
        "Tracking Station",
        "Mission Control",
        "Astronaut Complex",
        "Research and Development",
        "Administration",
        "Administration Building",
    ],
    "인물/직업": [
        "Kerbal",
        "Kerbals",
        "Pilot",
        "Engineer",
        "Scientist",
        "Tourist",
        "Crew",
        "Astronaut",
    ],
    "천체": [
        "Sun",
        "Moho",
        "Eve",
        "Gilly",
        "Kerbin",
        "Mun",
        "Minmus",
        "Duna",
        "Ike",
        "Dres",
        "Jool",
        "Laythe",
        "Vall",
        "Tylo",
        "Bop",
        "Pol",
        "Eeloo",
        "The Sun",
        "The Mun",
    ],
    "상태": [
        "LANDED",
        "SPLASHED",
        "FLYING",
        "SUB-ORBITAL",
        "ORBITING",
        "ESCAPING",
        "DOCKED",
        "PRELAUNCH",
        "Landed",
        "Splashed Down",
        "Flying",
        "Orbiting",
    ],
    "UI 공통": [
        "Settings",
        "Difficulty",
        "Save",
        "Load",
        "Quicksave",
        "Quickload",
        "Revert",
        "Revert Flight",
        "Recover Vessel",
        "Terminate",
        "Launch",
        "Cancel",
        "Accept",
        "Decline",
        "Delete",
        "Rename",
        "Map",
        "Map View",
        "Docking Mode",
        "Resume Saved",
        "Start New",
        "Exit",
        "Apply",
        "OK",
    ],
    "DLC (Breaking Ground)": [
        "Hinge",
        "Piston",
        "Rotor",
        "Rotation Servo",
        "Robotics",
        "Deployed Science",
        "Surface Features",
        "Grip Pad",
        "Propeller",
        "Blade",
        "Deploy",
        "Retract",
    ],
}


def normalize(value: str) -> str:
    return value.strip().rstrip(":").strip().lower()


def main() -> int:
    dictionaries = [
        (parse_dictionary(english_path), parse_dictionary(ko_path))
        for english_path, ko_path in FILE_PAIRS
    ]

    for category, terms in TERMS.items():
        print(f"\n## {category}")
        for term in terms:
            found: Counter = Counter()
            example_key = None
            for english, korean in dictionaries:
                ko_map = korean.mapping()
                for e in english.entries:
                    if normalize(e.value) == normalize(term):
                        ko_value = ko_map.get(e.key)
                        if ko_value:
                            found[ko_value.strip()] += 1
                            example_key = example_key or e.key
            if found:
                values = ", ".join(f"{v} (x{n})" for v, n in found.most_common(5))
                print(f"- {term}: {values}  [예: {example_key}]")
            else:
                print(f"- {term}: (정확 일치 없음)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
