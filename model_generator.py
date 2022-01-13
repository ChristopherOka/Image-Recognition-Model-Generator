import numpy as np
import os
import PIL
from PIL import Image
import tensorflow as tf
import tensorflow_datasets as tfds
import pathlib

dataset_path = "D:\Programming\TensorFlow\dataset"
data_dir = pathlib.Path(dataset_path)

prediction_img = "D:\Programming\TensorFlow\prediction_set\\test.jpg"
# prediction_img = tf.keras.preprocessing.image.load_image(prediction_img, target_size=(256,256))
# img_array = tf.keras.preprocessing.image.img_to_array(prediction_img)
# img_batch = np.expand_dims(img_array, axis=0)
# img_preprocessed = tf.keras.applications.resnet50.preprocess_input(img_batch)

image_count = len(list(data_dir.glob("*/*.png")))
print(image_count)

# for x in range(1, image_count):
#     # tensor = tf.image.convert_image_dtype(
#     #     image=f"D:\Programming\TensorFlow\dataset\\auston_matthews\\{x}.jpg",
#     #     dtype="uint8",
#     # )
#     print(
#         tf.io.decode_image(
#             "D:/Chris/Pictures/1000x-1.jpg",
#             channels=None,
#             dtype=tf.dtypes.uint8,
#             name=None,
#             expand_animations=True,
#         )
#     )


batch_size = 32
img_height = 180
img_width = 180

# train_ds = tf.keras.utils.image_dataset_from_directory(
#     data_dir,
#     validation_split=0.1,
#     subset="training",
#     seed=123,
#     image_size=(img_height, img_width),
#     batch_size=batch_size,
# )
# val_ds = tf.keras.utils.image_dataset_from_directory(
#     data_dir,
#     validation_split=0.1,
#     subset="validation",
#     seed=123,
#     image_size=(img_height, img_width),
#     batch_size=batch_size,
# )

train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size,
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size,
)

normalization_layer = tf.keras.layers.Rescaling(1.0 / 255)

normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
image_batch, labels_batch = next(iter(normalized_ds))
first_image = image_batch[0]
# Notice the pixel values are now in `[0,1]`.
print(np.min(first_image), np.max(first_image))

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

num_classes = 5
model = tf.keras.Sequential(
    [
        tf.keras.layers.Rescaling(1.0 / 255),
        tf.keras.layers.Conv2D(32, 3, activation="relu"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(32, 3, activation="relu"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(32, 3, activation="relu"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dense(num_classes),
    ]
)

# tf.keras.models.load_model(
#     './flower_model', custom_objects=None, compile=True, options=None
# )

model.compile(
    optimizer="adam",
    loss=tf.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"],
)

model.fit(train_ds, validation_data=val_ds, epochs=5)
# prediction = model.predict(prediction_set)

# print(prediction)

model.save("./auston_model")
