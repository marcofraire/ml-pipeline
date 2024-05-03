import os
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from config_ml import ML_MODELS_DIRECTORY

class ModelTraining:
    def __init__(self, edition_id, base_model=None):
        self.edition_id = edition_id
        self.base_model = base_model if base_model else self._create_base_model()
        self.model = self._build_model()

    def _create_base_model(self):
        base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        base_model.trainable = False
        return base_model

    def _build_model(self):
        model = Sequential([
            self.base_model,
            GlobalAveragePooling2D(),
            Dense(1, activation='sigmoid')  # Assume binary classification
        ])
        model.compile(optimizer=Adam(learning_rate=0.0001), loss='binary_crossentropy', metrics=['accuracy'])
        return model

    @property
    def train_directory(self):
        return os.path.join(ML_MODELS_DIRECTORY, self.edition_id, 'Images', 'Train')

    @property
    def test_directory(self):
        return os.path.join(ML_MODELS_DIRECTORY, self.edition_id, 'Images', 'Test')

    def datagen(self):
        return ImageDataGenerator(
            preprocessing_function=preprocess_input,
            rotation_range=45,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            channel_shift_range=0.2,
            horizontal_flip=True,
            vertical_flip=True,
            brightness_range=[0.5, 1.5],
            fill_mode='nearest',
            validation_split=0.08
        )

    def train_model(self, batch_size, epochs=5):
        train_generator = self.datagen().flow_from_directory(
            self.train_directory,
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='binary',
            subset='training'
        )
        validation_generator = self.datagen().flow_from_directory(
            self.train_directory,
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='binary',
            subset='validation'
        )
        self.model.fit(
            train_generator,
            steps_per_epoch=max(1, train_generator.samples // batch_size),
            validation_data=validation_generator,
            validation_steps=max(1, validation_generator.samples // batch_size),
            epochs=epochs
        )

    def test_model(self):
        test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
        test_generator = test_datagen.flow_from_directory(
            self.test_directory,
            target_size=(224, 224),
            batch_size=1,
            class_mode='binary',
            shuffle=False
        )
        predictions = self.model.predict(test_generator, steps=test_generator.samples)
        return predictions, test_generator
