load_db_configurations = {
    "ml_book": {
        "url": {
            "production": "https://bbourse-f97c610fe272.herokuapp.com/ml_book",
            "development": "http://localhost:8000/ml_book",
        },
        "payload_template": {
            "edition_id": ("edition_id", "int"),
            "img_link": ("galleryURL", "str"),
            "img_id": ("img_id", "str"),
            "prediction": ("is_edition", "bool"),
            "prediction_probability": ("is_edition_probability", "float"),
            "label": ("correct", "bool"),
        },
    },
    "ebay_listings": {
        "url": {
            "production": "https://bbourse-f97c610fe272.herokuapp.com/ebay_listings",
            "development": "http://localhost:8000/ebay_listings",
        },
        "payload_template": {
            "edition_id": ("edition_id", "int"),
            "img_link": ("galleryURL", "str"),
            "img_id": ("img_id", "str"),
            "signed": ("signed", "str"),
            "condition": ("condition", "str"),
            "sub_edition": ("sub_edition", "str"),
        },
    },
    "ebay_sales": {
        "url": {
            "production": "https://bbourse-f97c610fe272.herokuapp.com/ebay_sales",
            "development": "http://localhost:8000/ebay_sales",
        },
        "payload_template": {
            "edition_id": ("edition_id", "int"),
            "img_link": ("galleryURL", "str"),
            "img_id": ("img_id", "str"),
            "title": ("title", "str"),
            "price": ("price", "float"),
            "reduced": ("reduced", "int"),
            "seller": ("seller", "str"),
            "seller_rating": ("seller_rating", "float"),
            "seller_sales": ("seller_sales", "float"),
            "sale_data": ("sale_data", "date"),
            "country": ("country", "str"),
            "signed": ("signed", "str"),
            "condition": ("condition", "str"),
            "sub_edition": ("sub_edition", "str"),
        },
    },
    "image_features": {
        "url": {
            "production": "https://bbourse-f97c610fe272.herokuapp.com/image_features",
            "development": "http://localhost:8000/image_features",
        },
        "payload_template": {
            "edition_id": ("edition_id", "int"),
            "feature_vector": ("feature_vector", "list_float"),
            "binding": ("binding", "str"),
            "edition_metadata": ("edition_metadata", "str"),
        },
    },
    "book_editions": {
        "url": {
            "production": "https://bbourse-f97c610fe272.herokuapp.com/book_editions",
            "development": "http://localhost:8000/book_editions",
        },
        "payload_template": {
            "edition_details": ("edition_details", "str"),
            "display": ("display", "bool"),
        },
    },
}
