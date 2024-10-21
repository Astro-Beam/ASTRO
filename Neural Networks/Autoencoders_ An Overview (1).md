# Autoencoders: An Overview

Autoencoders are a type of artificial neural network that aims to copy their inputs to their outputs. They work by compressing the input into a latent-space representation (also known as a **bottleneck**) and then reconstructing the output from this representation. Autoencoders are an unsupervised machine learning algorithm and can be used for **feature extraction** through dimensionality reduction.

## 1. Feature Extraction
Feature projection, also called **feature extraction**, transforms the data from a high-dimensional space to a space of fewer dimensions. The transformation may be linear, as in **Principal Component Analysis (PCA)**, but many non-linear dimensionality reduction techniques exist, such as the ones used by autoencoders. For multidimensional data, **tensor representation** can be used for dimensionality reduction through multilinear subspace learning.

### 2. PCA
PCA is the main linear technique for dimensionality reduction. It performs a linear mapping of data to a lower-dimensional space, maximizing the variance of the data in the reduced space.

### 3. ICA
(*Add details if needed*)

## 4. Dimensionality Reduction
Dimensionality reduction transforms data from a high-dimensional space to a lower-dimensional space, while retaining meaningful properties of the original data. Ideally, the low-dimensional representation approximates the **intrinsic dimension** of the dataset (i.e., the number of variables required for a minimal representation).

---

## Components of an Autoencoder

### Encoder
The encoder compresses the input data into a latent-space representation. The compressed data often looks garbled and dissimilar to the original.

### Decoder
The decoder reconstructs the encoded data back to the original dimensionality. The reconstructed data is often a lossy version of the input.

### Bottleneck
The **bottleneck** (or “code”) contains the most compressed representation of the input. It is the output layer of the encoder and the input layer of the decoder. A fundamental goal in designing autoencoders is to discover the minimal number of features necessary for effective reconstruction.

### Purpose
Autoencoders aim to copy inputs to outputs in such a way that the **bottleneck** learns useful features or properties, not just identity mapping.

---

## Undercomplete Autoencoders
An **undercomplete autoencoder** is primarily used for dimensionality reduction. The hidden layers have fewer nodes than the input/output layers, which helps the bottleneck focus on the essential features needed for reconstruction. The goal is to prevent overfitting by limiting the bottleneck's capacity, forcing the network to retain only the most important information.

---

## Hyperparameters of Autoencoders
Designing an autoencoder involves several key hyperparameters:
- **Code size**: Controls how much the data is compressed. Adjusting the code size helps prevent overfitting or underfitting.
- **Number of layers**: Deeper networks add complexity but may slow processing speed.
- **Number of nodes per layer**: Typically, the number of nodes decreases with each encoder layer, reaching a minimum at the bottleneck, and increases with each decoder layer. However, this may vary depending on the input data.
- **Loss function**: The loss function, measuring reconstruction loss, is essential for optimizing the model during training. Common choices depend on the task (e.g., MSE for continuous data).

---

## Long Short-Term Memory (LSTM)
LSTM is a type of **recurrent neural network (RNN)** designed to address the **vanishing gradient** problem of traditional RNNs. It excels in sequence prediction tasks, especially those involving long-term dependencies (e.g., time series).

### LSTM Architecture
LSTMs introduce a **memory cell** controlled by three gates:
- **Input gate**: Adds information to the memory cell.
- **Forget gate**: Removes information from the memory cell.
- **Output gate**: Outputs information from the memory cell.

---

## Denoising Autoencoders (DAE)
**DAE** aims to minimize the difference between the original (clean) input and the reconstructed output, rather than comparing against corrupted input. The reconstruction loss (e.g., **MSE** for continuous data) quantifies the discrepancy between the input and output. The goal is to learn to capture and replicate the essential features of the input data.

---

## Error Metrics
Common error metrics for autoencoders include:
- **RMSE**
- **MSE**
- **MAE**
- **PSNR (Peak Signal-to-Noise Ratio)**: Used to assess the quality of reconstruction in signal processing, particularly for images. It measures the amount of noise introduced during reconstruction.

PSNR formula:
$$PSNR = 10 \cdot \log_{10} \left( \frac{MAX_f^2}{MSE} \right)$$

Where **MAXf** is the maximum possible value of the original signal and **MSE** is the mean squared error. Higher PSNR values indicate better reconstruction quality.

---

## Activation Functions
- **Sigmoid**: Outputs values between 0 and 1. It’s useful for constraining outputs to a specific range.
- **Tanh**: Outputs values between -1 and 1, providing a symmetric range.
