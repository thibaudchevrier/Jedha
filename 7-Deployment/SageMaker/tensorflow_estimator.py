import argparse
import os
import pathlib
import tensorflow as tf

parser = argparse.ArgumentParser()
# Hyperparameters sent by the client are passed as command-line arguments
# to the script
parser.add_argument("--epochs", type=int, default=10)
parser.add_argument("--batch_size", type=int, default=100)
parser.add_argument("--learning_rate", type=float, default=0.1)

parser.add_argument("--model_dir", type=str)
parser.add_argument("--sm-model-dir",
                    type=str,
                    default=os.environ.get("SM_MODEL_DIR"))
parser.add_argument("--train",
                    type=str,
                    default=os.environ.get("SM_CHANNEL_TRAIN"))
parser.add_argument("--test",
                    type=str,
                    default=os.environ.get("SM_CHANNEL_TEST"))

if __name__ == "__main__":
    args = parser.parse_args()

    # Get files
    path = pathlib.Path(args.train)

    # Get all images
    all_images = list(path.glob("*/*"))
    all_image_paths = [str(path) for path in list(path.glob("*/*"))]

    # Transform images into tensors
    def preprocess_and_load_images(path):
        image = tf.io.read_file(path)
        image = tf.image.decode_jpeg(image, channels=3)
        image = tf.image.resize(image, [192, 192])
        return image

    # Apply preprocessing function
    ds_paths = tf.data.Dataset.from_tensor_slices(all_image_paths)
    ds_images = ds_paths.map(preprocess_and_load_images)

    # Map Labels
    labels = []
    for data in path.iterdir():
        if data.is_dir():
            labels += [data.name]

    labels_index = {}
    for i, label in enumerate(labels):
        labels_index[label] = i

    all_image_labels = [
        labels_index[path.parent.name] for path in list(path.glob("*/*"))
    ]

    # Create a tf Dataset
    labels_ds = tf.data.Dataset.from_tensor_slices(all_image_labels)

    # Zip train and labeled dataset
    full_ds = tf.data.Dataset.zip((ds_images, labels_ds))

    # Shuffle Dataset and batch it
    full_ds = full_ds.shuffle(len(all_images)).batch(args.batch_size)

    # Create a pre-trained model
    base_model = tf.keras.applications.InceptionV3(input_shape=(192, 192, 3),
                                                   include_top=False,
                                                   weights="imagenet")

    base_model.trainable = False
    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(len(labels), activation="softmax"),
    ])

    initial_learning_rate = args.learning_rate

    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
        initial_learning_rate,
        decay_steps=1000,
        decay_rate=0.96,
        staircase=True)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr_schedule),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
    )

    # Train the model
    model.fit(full_ds, epochs=args.epochs)

    # Save the model
    # If you want to deploy your model after training,
    # Sagemaker requires you to register it inside a numerical
    # folder. That is why we put "1".
    model.save(os.path.join(args.sm_model_dir, "1"))
