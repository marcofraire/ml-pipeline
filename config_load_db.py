load_db_configurations = {
    "ml_book": {
        "url": {
            "production": "https://bbourse-f97c610fe272.herokuapp.com/ml_book",
            "development": "http://localhost:8000/ml_book"
        },
        "payload_template": {
            "edition_id": ("edition_id", "int"),
            "img_link": ("galleryURL", "str"),
            "label": ("correct", "bool")
        }
    },
}
