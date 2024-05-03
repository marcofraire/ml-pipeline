ML_MODELS_DIRECTORY_PRODUCTION = '/content/drive/My Drive/Tech/Production/ML_Models/'
PREDICTION_FILES_DIRECTORY = '/content/drive/My Drive/Tech/Production/Edition_Prediction_Files/New/'
ARCHIVE_FILES_DIRECTORY = '/content/drive/My Drive/Tech/Production/Edition_Prediction_Files/Archive/'

ML_MODELS_DIRECTORY = '/content/drive/My Drive/Tech/Model Training/Edition Recognition/'

config_edition_ml = {
    '1': {
        'ebay_api_keywords': 'A game of thrones first edition',
        'ml_model': '2_AGOT_Model_2024-02-27.h5',
        'file_name': 'AGOT_1_US'
    },
    '2': {
        'ebay_api_keywords': 'A game of thrones first edition uk',
        'ml_model': '2_model_2024-05-03 09:43:07.h5',
        'file_name': 'AGOT_1_UK'
    }
}