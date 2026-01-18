from django.core.management.base import BaseCommand
from django.db import transaction

from foodapi.models import FoodItem, FoodNutrition, PortionType  # change app name if needed


FOODS = [
    # name, portion_type
    ("burger", PortionType.COUNTABLE),
    ("chatamari", PortionType.PORTION),
    ("chhoila", PortionType.PORTION),
    ("chiya", PortionType.PORTION),
    ("dalbhat", PortionType.PORTION),
    ("dhindo", PortionType.PORTION),
    ("friedrice", PortionType.PORTION),
    ("gundruk", PortionType.PORTION),
    ("jeri", PortionType.COUNTABLE),
    ("kheer", PortionType.PORTION),
    ("momo", PortionType.COUNTABLE),
    ("omelette", PortionType.COUNTABLE),
    ("pakoda", PortionType.COUNTABLE),
    ("panipuri", PortionType.COUNTABLE),
    ("pizza", PortionType.PORTION),
    ("roti", PortionType.COUNTABLE),
    ("samosa", PortionType.COUNTABLE),
    ("sekuwa", PortionType.PORTION),
    ("selroti", PortionType.COUNTABLE),
    ("yomari", PortionType.COUNTABLE),
]

# Starter nutrition values.
# COUNTABLE: per piece
# PORTION: small/medium/large
NUTRITION = {
    "momo": {
        "per_piece": {"calories": 35, "protein": 1.5, "carbs": 4.5, "fat": 1.0},
    },
    "samosa": {
        "per_piece": {"calories": 260, "protein": 6, "carbs": 28, "fat": 14},
    },
    "roti": {
        "per_piece": {"calories": 120, "protein": 3.5, "carbs": 22, "fat": 2.5},
    },
    "selroti": {
        "per_piece": {"calories": 220, "protein": 3, "carbs": 35, "fat": 8},
    },
    "panipuri": {
        "per_piece": {"calories": 30, "protein": 1, "carbs": 5, "fat": 1},
    },
    "pakoda": {
        "per_piece": {"calories": 70, "protein": 2, "carbs": 8, "fat": 4},
    },
    "omelette": {
        "per_piece": {"calories": 180, "protein": 12, "carbs": 2, "fat": 14},
    },
    "jeri": {
        "per_piece": {"calories": 150, "protein": 1.5, "carbs": 22, "fat": 6},
    },
    "yomari": {
        "per_piece": {"calories": 180, "protein": 4, "carbs": 34, "fat": 3},
    },
    "burger": {
        "per_piece": {"calories": 450, "protein": 20, "carbs": 45, "fat": 20},
    },

    "dalbhat": {
        "portion": {
            "small":  {"calories": 450, "protein": 14, "carbs": 78, "fat": 10},
            "medium": {"calories": 650, "protein": 20, "carbs": 110, "fat": 14},
            "large":  {"calories": 850, "protein": 26, "carbs": 140, "fat": 18},
        }
    },
    "friedrice": {
        "portion": {
            "small":  {"calories": 380, "protein": 10, "carbs": 55, "fat": 14},
            "medium": {"calories": 550, "protein": 14, "carbs": 80, "fat": 20},
            "large":  {"calories": 750, "protein": 18, "carbs": 110, "fat": 28},
        }
    },
    "kheer": {
        "portion": {
            "small":  {"calories": 220, "protein": 6, "carbs": 35, "fat": 6},
            "medium": {"calories": 320, "protein": 8, "carbs": 50, "fat": 9},
            "large":  {"calories": 430, "protein": 11, "carbs": 65, "fat": 12},
        }
    },
    "chiya": {
        "portion": {
            "small":  {"calories": 60, "protein": 2, "carbs": 7, "fat": 3},
            "medium": {"calories": 90, "protein": 3, "carbs": 10, "fat": 4},
            "large":  {"calories": 130, "protein": 4, "carbs": 14, "fat": 6},
        }
    },
    "pizza": {
        "portion": {
            "small":  {"calories": 250, "protein": 10, "carbs": 28, "fat": 11},
            "medium": {"calories": 450, "protein": 18, "carbs": 50, "fat": 20},
            "large":  {"calories": 650, "protein": 26, "carbs": 72, "fat": 28},
        }
    },
    "chatamari": {
        "portion": {
            "small":  {"calories": 220, "protein": 10, "carbs": 20, "fat": 10},
            "medium": {"calories": 320, "protein": 14, "carbs": 28, "fat": 14},
            "large":  {"calories": 450, "protein": 18, "carbs": 38, "fat": 20},
        }
    },
    "chhoila": {
        "portion": {
            "small":  {"calories": 180, "protein": 18, "carbs": 4, "fat": 10},
            "medium": {"calories": 260, "protein": 26, "carbs": 6, "fat": 14},
            "large":  {"calories": 360, "protein": 35, "carbs": 8, "fat": 20},
        }
    },
    "dhindo": {
        "portion": {
            "small":  {"calories": 250, "protein": 6, "carbs": 52, "fat": 2},
            "medium": {"calories": 360, "protein": 9, "carbs": 75, "fat": 3},
            "large":  {"calories": 480, "protein": 12, "carbs": 100, "fat": 4},
        }
    },
    "gundruk": {
        "portion": {
            "small":  {"calories": 50, "protein": 3, "carbs": 8, "fat": 1},
            "medium": {"calories": 80, "protein": 5, "carbs": 12, "fat": 1},
            "large":  {"calories": 120, "protein": 7, "carbs": 18, "fat": 2},
        }
    },
    "sekuwa": {
        "portion": {
            "small":  {"calories": 220, "protein": 22, "carbs": 2, "fat": 14},
            "medium": {"calories": 320, "protein": 32, "carbs": 3, "fat": 20},
            "large":  {"calories": 450, "protein": 45, "carbs": 4, "fat": 28},
        }
    },
}

def get_default_nutrition(portion_type: str):
    """
    Fallback values if a food has no entry in NUTRITION.
    """
    if portion_type == PortionType.COUNTABLE:
        return {"per_piece": {"calories": 100, "protein": 3, "carbs": 12, "fat": 4}}
    return {
        "portion": {
            "small": {"calories": 200, "protein": 6, "carbs": 30, "fat": 6},
            "medium": {"calories": 350, "protein": 10, "carbs": 50, "fat": 10},
            "large": {"calories": 500, "protein": 14, "carbs": 70, "fat": 14},
        }
    }


class Command(BaseCommand):
    help = "Seed FoodItem and FoodNutrition with starter data"

    @transaction.atomic
    def handle(self, *args, **options):
        created_items = 0
        created_nutrition = 0
        updated_nutrition = 0

        for name, ptype in FOODS:
            name = name.strip().lower()

            food, created = FoodItem.objects.get_or_create(
                name=name,
                defaults={"portion_type": ptype, "is_active": True},
            )
            if created:
                created_items += 1
            else:
                # keep portion_type synced (optional)
                if food.portion_type != ptype:
                    food.portion_type = ptype
                    food.save(update_fields=["portion_type"])

            payload = NUTRITION.get(name) or get_default_nutrition(ptype)

            nutrition, n_created = FoodNutrition.objects.get_or_create(food=food)
            if n_created:
                created_nutrition += 1

            if food.portion_type == PortionType.COUNTABLE:
                per = payload.get("per_piece") or get_default_nutrition(PortionType.COUNTABLE)["per_piece"]
                nutrition.calories_per_piece = per["calories"]
                nutrition.protein_per_piece = per["protein"]
                nutrition.carbs_per_piece = per["carbs"]
                nutrition.fat_per_piece = per["fat"]

            else:
                por = payload.get("portion") or get_default_nutrition(PortionType.PORTION)["portion"]
                for size in ("small", "medium", "large"):
                    nutrition.__dict__[f"calories_{size}"] = por[size]["calories"]
                    nutrition.__dict__[f"protein_{size}"] = por[size]["protein"]
                    nutrition.__dict__[f"carbs_{size}"] = por[size]["carbs"]
                    nutrition.__dict__[f"fat_{size}"] = por[size]["fat"]

            nutrition.save()
            updated_nutrition += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. FoodItem created: {created_items}, FoodNutrition created: {created_nutrition}, updated: {updated_nutrition}"
        ))
