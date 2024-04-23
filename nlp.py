# -*- coding: utf-8 -*-
"""NLP.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mbCZYy8DccKLOP8CgNMuUavaetXOytmm
"""

import pandas as pd
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import Sequential
from keras.utils import to_categorical
from keras.preprocessing.text import Tokenizer
import tensorflow_hub as hub
from keras.layers import Dense, Activation
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, Flatten, Dense, Dropout

df = data
# Cleaning
df.dropna(subset=['text'], inplace=True)
df['text'] = df['text'].apply(lambda x: x.lower())
df['text'] = df['text'].astype(str)
df = df.drop_duplicates()

tokenizer = Tokenizer()
tokenizer.fit_on_texts(df['text'])
X = tokenizer.texts_to_sequences(df['text'])
X = pad_sequences(X, padding='post')
y = LabelEncoder().fit_transform(df['author'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

X_train_texts = [' '.join([tokenizer.index_word[i] for i in seq if i != 0]) for seq in X_train]
X_test_texts = [' '.join([tokenizer.index_word[i] for i in seq if i != 0]) for seq in X_test]

# TensorFlow Hub Pre-trained Model
embedding_model = "https://tfhub.dev/google/nnlm-en-dim128/2"
hub_layer = hub.KerasLayer(embedding_model, input_shape=[], dtype=tf.string, trainable=True)

# model architecture
model = tf.keras.Sequential([
    hub_layer,
    tf.keras.layers.Reshape((128, 1)),
    tf.keras.layers.Conv1D(filters=128, kernel_size=5, activation='relu'),
    tf.keras.layers.MaxPooling1D(pool_size=2),
    tf.keras.layers.Conv1D(filters=128, kernel_size=5, activation='relu'),
    tf.keras.layers.MaxPooling1D(pool_size=2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(len(np.unique(y)), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
history = model.fit(np.array(X_train_texts), y_train, epochs=20, batch_size=32, validation_split=0.2)

# Evaluating
test_loss, test_accuracy = model.evaluate(np.array(X_test_texts), y_test)
print(f"Test Accuracy: {test_accuracy * 100:.2f}%")

# Plotting training and validation accuracy
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy During Training')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='upper left')
plt.grid(True)
plt.show()