from .enums import PortionType

def compute_nutrition(food_item, pieces=None, size=None):
    nutrition = food_item.nutrition

    if food_item.portion_type == PortionType.COUNTABLE:
        if pieces is None:
            raise ValueError("pieces is required for COUNTABLE foods")

        return {
            "unit": "piece",
            "quantity": float(pieces),
            "calories": (nutrition.calories_per_piece or 0) * pieces,
            "protein": (nutrition.protein_per_piece or 0) * pieces,
            "carbs": (nutrition.carbs_per_piece or 0) * pieces,
            "fat": (nutrition.fat_per_piece or 0) * pieces,
        }

    if food_item.portion_type == PortionType.PORTION:
        if not size:
            raise ValueError("size is required for PORTION foods")

        return {
            "unit": "portion",
            "size": size,
            "calories": getattr(nutrition, f"calories_{size}") or 0,
            "protein": getattr(nutrition, f"protein_{size}") or 0,
            "carbs": getattr(nutrition, f"carbs_{size}") or 0,
            "fat": getattr(nutrition, f"fat_{size}") or 0,
        }

    raise ValueError("Invalid portion type")
