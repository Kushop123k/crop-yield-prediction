"""
Seed & Variety Recommendation Engine
=====================================
Returns best seed varieties for given crop, soil, season & state.
"""

SEED_DATABASE = {
    "Rice": {
        "Kharif": {
            "West Bengal": [
                {"name": "MTU 7029 (Swarna)", "yield": "5–6 t/ha", "duration": "145–150 days", "trait": "High yield, flood tolerant", "certified": True},
                {"name": "IR 64",              "yield": "4–5 t/ha", "duration": "125–130 days", "trait": "Drought tolerant, widely grown", "certified": True},
                {"name": "Satabdi (IET 4786)", "yield": "4.5–5 t/ha","duration": "130–135 days", "trait": "Fine grain, popular in WB", "certified": True},
                {"name": "Lalat",              "yield": "4–5 t/ha", "duration": "140 days",     "trait": "Medium slender, good taste", "certified": True},
            ],
            "default": [
                {"name": "Pusa Basmati 1121", "yield": "4–5 t/ha", "duration": "135–140 days", "trait": "Aromatic, export quality", "certified": True},
                {"name": "IR 36",             "yield": "4.5 t/ha", "duration": "110–115 days", "trait": "Short duration, pest resistant", "certified": True},
            ]
        },
        "Rabi": {
            "default": [
                {"name": "Ranjit",  "yield": "5 t/ha",   "duration": "155 days", "trait": "Boro rice, cold tolerant", "certified": True},
                {"name": "CR 310", "yield": "4.5 t/ha", "duration": "145 days", "trait": "Good for boro season", "certified": True},
            ]
        }
    },
    "Wheat": {
        "Rabi": {
            "Punjab": [
                {"name": "HD 2967",    "yield": "5–5.5 t/ha", "duration": "145 days", "trait": "High yield, rust resistant", "certified": True},
                {"name": "PBW 343",    "yield": "4.5–5 t/ha", "duration": "148 days", "trait": "Very popular in Punjab", "certified": True},
                {"name": "DBW 187",    "yield": "5.5–6 t/ha", "duration": "143 days", "trait": "New variety, excellent yield", "certified": True},
            ],
            "default": [
                {"name": "GW 322",     "yield": "4–5 t/ha",   "duration": "110 days", "trait": "Short duration, drought tolerant", "certified": True},
                {"name": "Lok 1",      "yield": "3.5–4 t/ha", "duration": "108 days", "trait": "Early maturing", "certified": True},
            ]
        }
    },
    "Maize": {
        "Kharif": {
            "default": [
                {"name": "DHM 117",      "yield": "7–8 t/ha", "duration": "90–95 days", "trait": "Hybrid, high yield", "certified": True},
                {"name": "Ganga 5",      "yield": "5–6 t/ha", "duration": "95–100 days","trait": "Open pollinated, stable", "certified": True},
                {"name": "HQPM 1",       "yield": "6 t/ha",   "duration": "90 days",    "trait": "Quality protein maize", "certified": True},
                {"name": "Vivek QPM 9",  "yield": "5.5 t/ha", "duration": "85 days",    "trait": "Short duration, nutritious", "certified": True},
            ]
        },
        "Rabi": {
            "default": [
                {"name": "Pusa Hybrid 4", "yield": "6–7 t/ha", "duration": "100 days", "trait": "Winter maize, good yield", "certified": True},
            ]
        }
    },
    "Potato": {
        "Rabi": {
            "West Bengal": [
                {"name": "Kufri Jyoti",    "yield": "25–30 t/ha", "duration": "90–100 days", "trait": "Most popular in WB, late blight tolerant", "certified": True},
                {"name": "Kufri Sindhuri", "yield": "20–25 t/ha", "duration": "100–110 days","trait": "Red skin, good storability", "certified": True},
                {"name": "Kufri Chandramukhi","yield":"15–20 t/ha","duration":"70–80 days",  "trait": "Early maturing, white flesh", "certified": True},
            ],
            "default": [
                {"name": "Kufri Pukhraj", "yield": "25–35 t/ha", "duration": "70–80 days", "trait": "High yield, early", "certified": True},
            ]
        }
    },
    "Tomato": {
        "Kharif": {
            "default": [
                {"name": "Pusa Ruby",     "yield": "25–30 t/ha", "duration": "65–70 days", "trait": "Firm fruit, good shelf life", "certified": True},
                {"name": "Arka Vikas",    "yield": "30–35 t/ha", "duration": "70 days",    "trait": "High yield, suitable for processing", "certified": True},
                {"name": "NS 585",        "yield": "35–40 t/ha", "duration": "65 days",    "trait": "Hybrid, disease resistant", "certified": True},
            ]
        },
        "Rabi": {
            "default": [
                {"name": "Pusa Sheetal",  "yield": "25 t/ha",    "duration": "75 days", "trait": "Cool season adapted", "certified": True},
            ]
        }
    },
    "Sugarcane": {
        "Kharif": {
            "default": [
                {"name": "Co 0238",     "yield": "80–100 t/ha", "duration": "12 months", "trait": "High sucrose, widely grown", "certified": True},
                {"name": "CoJ 64",      "yield": "70–85 t/ha",  "duration": "12 months", "trait": "Early maturing, good for North India", "certified": True},
                {"name": "CoSe 98231",  "yield": "75–90 t/ha",  "duration": "12 months", "trait": "Red rot resistant", "certified": True},
            ]
        }
    },
    "Soybean": {
        "Kharif": {
            "default": [
                {"name": "JS 335",   "yield": "2–2.5 t/ha", "duration": "95–100 days", "trait": "Most popular, high protein", "certified": True},
                {"name": "MACS 450", "yield": "2.5 t/ha",   "duration": "100 days",    "trait": "Lodging resistant", "certified": True},
                {"name": "NRC 7",    "yield": "2–2.8 t/ha", "duration": "105 days",    "trait": "High yield, broad adaptability", "certified": True},
            ]
        }
    },
    "Cotton": {
        "Kharif": {
            "default": [
                {"name": "Bt Cotton MRC 7017", "yield": "20–25 q/ha", "duration": "170–180 days", "trait": "Bollworm resistant, Bt hybrid", "certified": True},
                {"name": "RCH 2",              "yield": "18–22 q/ha", "duration": "165 days",     "trait": "Widely grown Bt hybrid", "certified": True},
                {"name": "Bunny BG II",        "yield": "20–24 q/ha", "duration": "170 days",     "trait": "High yield, good fibre", "certified": True},
            ]
        }
    }
}

FERTILIZER_DATABASE = {
    "Rice":      {"N": 120, "P": 60,  "K": 60,  "note": "Apply in 3 splits. Top dress urea at tillering & panicle initiation."},
    "Wheat":     {"N": 120, "P": 60,  "K": 40,  "note": "Apply full P & K at sowing. N in 2 splits (sowing + first irrigation)."},
    "Maize":     {"N": 150, "P": 75,  "K": 50,  "note": "Side dress N at knee-high stage. Zinc deficiency common — apply ZnSO4."},
    "Potato":    {"N": 180, "P": 100, "K": 150, "note": "High K requirement. Apply FYM 25 t/ha. Split N into 2 doses."},
    "Tomato":    {"N": 120, "P": 80,  "K": 80,  "note": "Weekly fertigation ideal. Use calcium nitrate to prevent blossom end rot."},
    "Sugarcane": {"N": 250, "P": 100, "K": 120, "note": "Apply in 3–4 splits. Trash mulching conserves moisture and nutrients."},
    "Soybean":   {"N": 30,  "P": 80,  "K": 40,  "note": "Seed inoculation with Rhizobium reduces N need. P is critical."},
    "Cotton":    {"N": 150, "P": 75,  "K": 75,  "note": "Foliar spray of K at boll development. Avoid excess N (vegetative growth)."},
}

PESTICIDE_DATABASE = {
    "Rice":      [{"pest": "Brown Plant Hopper", "chemical": "Imidacloprid 17.8% SL", "dose": "125 ml/ha"}, {"pest": "Blast disease", "chemical": "Tricyclazole 75% WP", "dose": "300 g/ha"}],
    "Wheat":     [{"pest": "Aphids", "chemical": "Dimethoate 30% EC", "dose": "1 L/ha"}, {"pest": "Yellow rust", "chemical": "Propiconazole 25% EC", "dose": "500 ml/ha"}],
    "Potato":    [{"pest": "Late Blight", "chemical": "Mancozeb 75% WP", "dose": "2 kg/ha"}, {"pest": "Aphids (virus vector)", "chemical": "Thiamethoxam 25% WG", "dose": "100 g/ha"}],
    "Tomato":    [{"pest": "Fruit borer", "chemical": "Spinosad 45% SC", "dose": "150 ml/ha"}, {"pest": "Early blight", "chemical": "Chlorothalonil 75% WP", "dose": "2 kg/ha"}],
    "Maize":     [{"pest": "Fall Army Worm", "chemical": "Emamectin Benzoate 5% SG", "dose": "200 g/ha"}, {"pest": "Stem borer", "chemical": "Chlorpyrifos 20% EC", "dose": "2.5 L/ha"}],
    "Cotton":    [{"pest": "Whitefly", "chemical": "Spiromesifen 22.9% SC", "dose": "750 ml/ha"}, {"pest": "Thrips", "chemical": "Fipronil 5% SC", "dose": "1.5 L/ha"}],
    "Soybean":   [{"pest": "Girdle beetle", "chemical": "Quinalphos 25% EC", "dose": "1.5 L/ha"}, {"pest": "Yellow mosaic (virus)", "chemical": "Control whitefly vector", "dose": "—"}],
    "Sugarcane": [{"pest": "Early shoot borer", "chemical": "Chlorantraniliprole 18.5% SC", "dose": "150 ml/ha"}, {"pest": "Red rot", "chemical": "Carbendazim 50% WP", "dose": "1 kg/ha"}],
}


def get_seed_recommendations(crop: str, season: str, state: str) -> dict:
    crop_data   = SEED_DATABASE.get(crop, {})
    season_data = crop_data.get(season, crop_data.get(list(crop_data.keys())[0], {})) if crop_data else {}
    varieties   = season_data.get(state, season_data.get("default", []))

    if not varieties:
        varieties = [{"name": "Consult local KVK", "yield": "Varies", "duration": "Varies",
                      "trait": "Contact your district Krishi Vigyan Kendra for certified seeds", "certified": False}]

    fertilizer = FERTILIZER_DATABASE.get(crop, {"N": 100, "P": 60, "K": 40, "note": "Follow soil test recommendations."})
    pesticides = PESTICIDE_DATABASE.get(crop, [])

    return {
        "crop":       crop,
        "season":     season,
        "state":      state,
        "varieties":  varieties,
        "fertilizer": fertilizer,
        "pesticides": pesticides,
        "source_note": "Recommendations based on ICAR & state agriculture department guidelines."
    }