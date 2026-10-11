"""Vehicle profiles used in the evaluation (proposal: at least four, compact to high-roof van).

Dimensions are manufacturer figures for common Swiss-market models, rounded to the cm.
The 1.85 m / 1.90 m limits seen in the survey make the 'large SUV' profile the
discriminating case; the two van profiles bracket the 2.00-2.10 m limits that dominate
Zurich garages.
"""
PROFILES = [
    {"name": "compact car (VW Golf)", "height_m": 1.46, "width_m": 1.79, "length_m": 4.28},
    {"name": "mid-size SUV (VW Tiguan)", "height_m": 1.67, "width_m": 1.84, "length_m": 4.54},
    {"name": "large SUV (Range Rover)", "height_m": 1.87, "width_m": 2.05, "length_m": 5.05},
    {"name": "standard-roof van (VW T6.1)", "height_m": 1.99, "width_m": 1.90, "length_m": 4.90},
    {"name": "high-roof van (Sprinter H2)", "height_m": 2.62, "width_m": 2.02, "length_m": 5.93},
]
