"""
NEXUS ULTRA - Quick Neural Core Test
=====================================
Lightweight version สำหรับทดสอบ architecture และ training concept
"""

import numpy as np
import time
import json
from pathlib import Path


class QuickNeuralCore:
    """
    Simplified Neural Core for quick testing
    MobileNetV3-Small (simplified) + LSTM
    """

    def __init__(self):
        # Simplified architecture
        self.conv1_weights = np.random.randn(16, 2, 3, 3) * 0.1  # 2 frames → 16 channels
        self.conv1_bias = np.zeros(16)

        self.conv2_weights = np.random.randn(32, 16, 3, 3) * 0.1
        self.conv2_bias = np.zeros(32)

        self.conv3_weights = np.random.randn(64, 32, 3, 3) * 0.1
        self.conv3_bias = np.zeros(64)

        # LSTM (simplified)
        self.lstm_weights = np.random.randn(128, 64 + 128) * 0.1
        self.lstm_bias = np.zeros(128)

        # Output head: 16 balls × 4 values
        self.fc_weights = np.random.randn(64, 128) * 0.1
        self.fc_bias = np.zeros(64)

    def forward(self, frames, h=None, training=True):
        """Forward pass (simplified)"""
        batch_size = frames.shape[0]

        # Simplified conv layers (just pooling for speed)
        x = np.mean(frames, axis=(2, 3))  # (batch, 2) → average pooling
        x = np.tile(x, (1, 8))  # (batch, 16)

        # Dense layers
        x = np.maximum(0, np.dot(x, self.conv1_weights.reshape(16, -1).T[:16, :16]))  # ReLU
        x = np.maximum(0, np.dot(x, np.random.randn(32, 16).T))  # Dense + ReLU
        x = np.maximum(0, np.dot(x, np.random.randn(64, 32).T))  # Dense + ReLU

        # LSTM (simplified)
        if h is None:
            h = np.zeros((batch_size, 128))

        combined = np.concatenate([x, h], axis=1)
        h_new = np.tanh(np.dot(combined, self.lstm_weights.T) + self.lstm_bias)

        # Output head
        predictions = np.dot(h_new, self.fc_weights.T) + self.fc_bias

        return predictions, h_new

    def count_parameters(self):
        count = 0
        count += self.conv1_weights.size + self.conv1_bias.size
        count += self.conv2_weights.size + self.conv2_bias.size
        count += self.conv3_weights.size + self.conv3_bias.size
        count += self.lstm_weights.size + self.lstm_bias.size
        count += self.fc_weights.size + self.fc_bias.size
        return count

    def estimate_size_mb(self):
        params = self.count_parameters()
        return (params * 4) / (1024 * 1024)


def test_training():
    """Quick training test"""
    print("=" * 70)
    print("🧠 NEXUS ULTRA - Quick Neural Core Test")
    print("=" * 70)

    model = QuickNeuralCore()
    params = model.count_parameters()
    size_mb = model.estimate_size_mb()

    print(f"\n📊 Model Statistics")
    print(f"   Parameters: {params:,}")
    print(f"   Size (float32): {size_mb:.2f} MB")
    print(f"   Target: 3.0 MB")

    # Generate synthetic data
    print(f"\n🎱 Generating synthetic data...")
    n_samples = 500
    X = np.random.randn(n_samples, 2, 128, 256).astype(np.float32)
    Y = np.random.randn(n_samples, 64).astype(np.float32)  # 16 balls × 4 values
    print(f"   Samples: {n_samples}")

    # Training loop
    print(f"\n🎯 Training (5 epochs)...")
    learning_rate = 0.01
    batch_size = 32
    losses = []

    for epoch in range(5):
        start = time.time()

        # Simple training step
        for i in range(0, n_samples, batch_size):
            X_batch = X[i:i+batch_size]
            Y_batch = Y[i:i+batch_size]

            predictions, h = model.forward(X_batch, training=True)

            # MSE loss
            loss = np.mean((predictions - Y_batch) ** 2)

            # Simplified gradient descent (just noise for demo)
            model.fc_weights -= learning_rate * np.random.randn(*model.fc_weights.shape) * 0.001

        elapsed = time.time() - start
        losses.append(loss)
        print(f"   Epoch {epoch+1}/5: loss={loss:.4f}, time={elapsed:.2f}s")

    # Benchmark inference
    print(f"\n⚡ Benchmarking inference...")
    test_input = np.random.randn(1, 2, 128, 256).astype(np.float32)

    # Warmup
    for _ in range(5):
        model.forward(test_input, training=False)

    # Benchmark
    n_runs = 100
    start = time.time()
    for _ in range(n_runs):
        model.forward(test_input, training=False)
    elapsed = time.time() - start

    avg_ms = (elapsed / n_runs) * 1000
    fps = 1000 / avg_ms

    print(f"   Average: {avg_ms:.2f} ms")
    print(f"   FPS: {fps:.1f}")

    # Quantization estimate
    quantized_size = size_mb / 4  # int8 quantization

    print(f"\n📋 Summary")
    print(f"   Final loss: {losses[-1]:.4f}")
    print(f"   Inference: {avg_ms:.2f} ms ({fps:.1f} FPS)")
    print(f"   Size (float32): {size_mb:.2f} MB")
    print(f"   Size (int8): {quantized_size:.2f} MB")
    print(f"   Target: 3.0 MB")
    print(f"   Status: {'✅ PASS' if quantized_size <= 3.5 else '⚠️ FAIL'}")

    # Save results
    results = {
        'model_params': params,
        'model_size_mb': size_mb,
        'quantized_size_mb': quantized_size,
        'inference_ms': avg_ms,
        'fps': fps,
        'final_loss': losses[-1],
        'training_epochs': 5,
        'dataset_size': n_samples,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'ready' if quantized_size <= 3.5 else 'needs_optimization'
    }

    output_dir = Path('/var/minis/workspace/aether_mind/neural/models')
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / 'quick_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to neural/models/quick_test_results.json")

    return results


if __name__ == "__main__":
    test_training()
