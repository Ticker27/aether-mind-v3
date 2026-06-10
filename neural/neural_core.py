"""
NEXUS ULTRA - Neural Core Architecture
=======================================
MobileNetV3-Small backbone + LSTM head สำหรับทำนายฟิสิกส์ลูกบิลเลียด

Architecture:
- Input: 2 frames (128x256 grayscale) → shape (2, 128, 256)
- MobileNetV3-Small: feature extraction → (512,)
- LSTM: temporal modeling → (256,)
- FC Head: ball prediction → (16 balls × 4 values = 64)

Output: [x, y, vx, vy] × 16 balls = 64 values
"""

import numpy as np
import math
from typing import List, Tuple


class Conv2D:
    """2D Convolution layer"""

    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding

        # Initialize weights (He initialization)
        fan_in = in_channels * kernel_size * kernel_size
        self.weights = np.random.randn(
            out_channels, in_channels, kernel_size, kernel_size
        ) * np.sqrt(2.0 / fan_in)
        self.bias = np.zeros(out_channels)

    def forward(self, x):
        """
        x: (batch, channels, height, width)
        """
        batch_size, in_c, h, w = x.shape

        # Padding
        if self.padding > 0:
            x_padded = np.pad(
                x,
                ((0, 0), (0, 0), (self.padding, self.padding), (self.padding, self.padding)),
                mode='constant', constant_values=0
            )
        else:
            x_padded = x

        h_padded, w_padded = x_padded.shape[2], x_padded.shape[3]
        h_out = (h_padded - self.kernel_size) // self.stride + 1
        w_out = (w_padded - self.kernel_size) // self.stride + 1

        output = np.zeros((batch_size, self.out_channels, h_out, w_out))

        # Convolution
        for i in range(h_out):
            for j in range(w_out):
                h_start = i * self.stride
                w_start = j * self.stride
                h_end = h_start + self.kernel_size
                w_end = w_start + self.kernel_size

                receptive_field = x_padded[:, :, h_start:h_end, w_start:w_end]

                # (batch, in_c, k, k) × (out_c, in_c, k, k)
                for oc in range(self.out_channels):
                    output[:, oc, i, j] = np.sum(
                        receptive_field * self.weights[oc],
                        axis=(1, 2, 3)
                    ) + self.bias[oc]

        return output


class DepthwiseConv2D:
    """Depthwise separable convolution (MobileNet style)"""

    def __init__(self, channels, kernel_size, stride=1, padding=0):
        self.channels = channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding

        fan_in = kernel_size * kernel_size
        self.weights = np.random.randn(
            channels, 1, kernel_size, kernel_size
        ) * np.sqrt(2.0 / fan_in)
        self.bias = np.zeros(channels)

    def forward(self, x):
        batch_size, c, h, w = x.shape

        if self.padding > 0:
            x_padded = np.pad(
                x,
                ((0, 0), (0, 0), (self.padding, self.padding), (self.padding, self.padding)),
                mode='constant', constant_values=0
            )
        else:
            x_padded = x

        h_padded, w_padded = x_padded.shape[2], x_padded.shape[3]
        h_out = (h_padded - self.kernel_size) // self.stride + 1
        w_out = (w_padded - self.kernel_size) // self.stride + 1

        output = np.zeros((batch_size, self.channels, h_out, w_out))

        for ch in range(self.channels):
            for i in range(h_out):
                for j in range(w_out):
                    h_start = i * self.stride
                    w_start = j * self.stride
                    h_end = h_start + self.kernel_size
                    w_end = w_start + self.kernel_size

                    output[:, ch, i, j] = np.sum(
                        x_padded[:, ch:ch+1, h_start:h_end, w_start:w_end] * self.weights[ch],
                        axis=(1, 2, 3)
                    ) + self.bias[ch]

        return output


class BatchNorm2D:
    """Batch Normalization"""

    def __init__(self, num_features, momentum=0.9, eps=1e-5):
        self.momentum = momentum
        self.eps = eps
        self.gamma = np.ones(num_features)
        self.beta = np.zeros(num_features)
        self.running_mean = np.zeros(num_features)
        self.running_var = np.ones(num_features)

    def forward(self, x, training=True):
        if training:
            mean = np.mean(x, axis=(0, 2, 3))
            var = np.var(x, axis=(0, 2, 3))
            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * mean
            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * var
        else:
            mean = self.running_mean
            var = self.running_var

        x_norm = (x - mean[None, :, None, None]) / np.sqrt(var[None, :, None, None] + self.eps)
        return self.gamma[None, :, None, None] * x_norm + self.beta[None, :, None, None]


class HardSwish:
    """Hard-Swish activation (MobileNetV3)"""

    def forward(self, x):
        return x * np.clip(x + 3, 0, 6) / 6


class ReLU:
    """ReLU activation"""

    def forward(self, x):
        return np.maximum(0, x)


class SqueezeExcite:
    """Squeeze-and-Excitation block"""

    def __init__(self, channels, reduction=4):
        self.channels = channels
        self.fc1_channels = max(1, channels // reduction)
        self.fc2_channels = channels

        self.fc1_weights = np.random.randn(self.fc1_channels, channels) * 0.01
        self.fc1_bias = np.zeros(self.fc1_channels)
        self.fc2_weights = np.random.randn(self.fc2_channels, self.fc1_channels) * 0.01
        self.fc2_bias = np.zeros(self.fc2_channels)

    def forward(self, x):
        batch_size, c, h, w = x.shape

        # Squeeze: global average pooling
        se = np.mean(x, axis=(2, 3))  # (batch, channels)

        # Excitation: FC layers
        se = np.dot(se, self.fc1_weights.T) + self.fc1_bias
        se = np.maximum(0, se)  # ReLU
        se = np.dot(se, self.fc2_weights.T) + self.fc2_bias

        # Hard-Sigmoid
        se = np.clip(se + 3, 0, 6) / 6

        # Scale
        return x * se[:, :, None, None]


class MobileNetV3Block:
    """MobileNetV3 Inverted Residual Block"""

    def __init__(self, in_channels, exp_channels, out_channels, kernel_size,
                 stride=1, use_se=True, activation='hard_swish'):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.stride = stride
        self.use_se = use_se

        # Expansion
        self.exp_conv = Conv2D(in_channels, exp_channels, 1)
        self.exp_bn = BatchNorm2D(exp_channels)
        self.exp_act = HardSwish() if activation == 'hard_swish' else ReLU()

        # Depthwise
        padding = (kernel_size - 1) // 2
        self.dw_conv = DepthwiseConv2D(exp_channels, kernel_size, stride, padding)
        self.dw_bn = BatchNorm2D(exp_channels)
        self.dw_act = HardSwish() if activation == 'hard_swish' else ReLU()

        # Squeeze-Excite
        if use_se:
            self.se = SqueezeExcite(exp_channels)

        # Projection
        self.proj_conv = Conv2D(exp_channels, out_channels, 1)
        self.proj_bn = BatchNorm2D(out_channels)

    def forward(self, x, training=True):
        identity = x

        # Expansion
        x = self.exp_conv.forward(x)
        x = self.exp_bn.forward(x, training)
        x = self.exp_act.forward(x)

        # Depthwise
        x = self.dw_conv.forward(x)
        x = self.dw_bn.forward(x, training)
        x = self.dw_act.forward(x)

        # Squeeze-Excite
        if self.use_se:
            x = self.se.forward(x)

        # Projection
        x = self.proj_conv.forward(x)
        x = self.proj_bn.forward(x, training)

        # Residual connection
        if self.stride == 1 and self.in_channels == self.out_channels:
            x = x + identity

        return x


class LSTMCell:
    """LSTM Cell"""

    def __init__(self, input_size, hidden_size):
        self.input_size = input_size
        self.hidden_size = hidden_size

        # Initialize weights
        self.Wf = np.random.randn(hidden_size, input_size + hidden_size) * 0.01
        self.Wi = np.random.randn(hidden_size, input_size + hidden_size) * 0.01
        self.Wc = np.random.randn(hidden_size, input_size + hidden_size) * 0.01
        self.Wo = np.random.randn(hidden_size, input_size + hidden_size) * 0.01

        self.bf = np.zeros(hidden_size) + 1.0  # Forget gate bias init
        self.bi = np.zeros(hidden_size)
        self.bc = np.zeros(hidden_size)
        self.bo = np.zeros(hidden_size)

    def forward(self, x, h, c):
        """
        x: (batch, input_size)
        h: (batch, hidden_size)
        c: (batch, hidden_size)
        """
        # Concatenate input and hidden state
        combined = np.concatenate([x, h], axis=1)

        # Gates
        f = self._sigmoid(np.dot(combined, self.Wf.T) + self.bf)
        i = self._sigmoid(np.dot(combined, self.Wi.T) + self.bi)
        c_candidate = np.tanh(np.dot(combined, self.Wc.T) + self.bc)
        o = self._sigmoid(np.dot(combined, self.Wo.T) + self.bo)

        # Cell state
        c_new = f * c + i * c_candidate

        # Hidden state
        h_new = o * np.tanh(c_new)

        return h_new, c_new

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


class FullyConnected:
    """Fully connected layer"""

    def __init__(self, in_features, out_features):
        self.weights = np.random.randn(out_features, in_features) * np.sqrt(2.0 / in_features)
        self.bias = np.zeros(out_features)

    def forward(self, x):
        return np.dot(x, self.weights.T) + self.bias


class NeuralCore:
    """
    NEXUS ULTRA Neural Core
    ========================
    MobileNetV3-Small + LSTM for ball trajectory prediction
    """

    def __init__(self):
        # MobileNetV3-Small architecture (simplified)
        self.conv_stem = Conv2D(2, 16, 3, stride=2, padding=1)  # 2 frames input
        self.bn_stem = BatchNorm2D(16)
        self.act_stem = HardSwish()

        # MobileNetV3 blocks
        self.blocks = [
            MobileNetV3Block(16, 16, 16, 3, stride=2, use_se=True, activation='relu'),
            MobileNetV3Block(16, 72, 24, 3, stride=2, use_se=False, activation='relu'),
            MobileNetV3Block(24, 88, 24, 3, stride=1, use_se=False, activation='relu'),
            MobileNetV3Block(24, 96, 40, 5, stride=2, use_se=True, activation='hard_swish'),
            MobileNetV3Block(40, 240, 40, 5, stride=1, use_se=True, activation='hard_swish'),
            MobileNetV3Block(40, 240, 40, 5, stride=1, use_se=True, activation='hard_swish'),
            MobileNetV3Block(40, 120, 48, 5, stride=1, use_se=True, activation='hard_swish'),
            MobileNetV3Block(48, 144, 48, 5, stride=1, use_se=True, activation='hard_swish'),
            MobileNetV3Block(48, 288, 96, 5, stride=2, use_se=True, activation='hard_swish'),
            MobileNetV3Block(96, 576, 96, 5, stride=1, use_se=True, activation='hard_swish'),
            MobileNetV3Block(96, 576, 96, 5, stride=1, use_se=True, activation='hard_swish'),
        ]

        # Final conv
        self.conv_final = Conv2D(96, 512, 1)
        self.bn_final = BatchNorm2D(512)
        self.act_final = HardSwish()

        # LSTM
        self.lstm = LSTMCell(512, 256)

        # Output head: 16 balls × 4 values (x, y, vx, vy)
        self.fc_head = FullyConnected(256, 64)

    def forward(self, frames, h=None, c=None, training=True):
        """
        Forward pass

        Args:
            frames: (batch, 2, 128, 256) - 2 consecutive grayscale frames
            h: (batch, 256) - LSTM hidden state (optional)
            c: (batch, 256) - LSTM cell state (optional)
            training: bool

        Returns:
            predictions: (batch, 64) - ball states
            h: (batch, 256) - updated hidden state
            c: (batch, 256) - updated cell state
        """
        batch_size = frames.shape[0]

        # MobileNetV3-Small backbone
        x = self.conv_stem.forward(frames)
        x = self.bn_stem.forward(x, training)
        x = self.act_stem.forward(x)

        for block in self.blocks:
            x = block.forward(x, training)

        x = self.conv_final.forward(x)
        x = self.bn_final.forward(x, training)
        x = self.act_final.forward(x)

        # Global average pooling
        x = np.mean(x, axis=(2, 3))  # (batch, 512)

        # LSTM
        if h is None:
            h = np.zeros((batch_size, 256))
        if c is None:
            c = np.zeros((batch_size, 256))

        h, c = self.lstm.forward(x, h, c)

        # Output head
        predictions = self.fc_head.forward(h)

        return predictions, h, c

    def count_parameters(self):
        """นับจำนวน parameters ทั้งหมด"""
        count = 0

        # Stem
        count += self.conv_stem.weights.size + self.conv_stem.bias.size
        count += self.bn_stem.gamma.size * 2

        # Blocks
        for block in self.blocks:
            count += block.exp_conv.weights.size + block.exp_conv.bias.size
            count += block.exp_bn.gamma.size * 2
            count += block.dw_conv.weights.size + block.dw_conv.bias.size
            count += block.dw_bn.gamma.size * 2
            if block.use_se:
                count += block.se.fc1_weights.size + block.se.fc1_bias.size
                count += block.se.fc2_weights.size + block.se.fc2_bias.size
            count += block.proj_conv.weights.size + block.proj_conv.bias.size
            count += block.proj_bn.gamma.size * 2

        # Final conv
        count += self.conv_final.weights.size + self.conv_final.bias.size
        count += self.bn_final.gamma.size * 2

        # LSTM
        count += self.lstm.Wf.size + self.lstm.bf.size
        count += self.lstm.Wi.size + self.lstm.bi.size
        count += self.lstm.Wc.size + self.lstm.bc.size
        count += self.lstm.Wo.size + self.lstm.bo.size

        # Head
        count += self.fc_head.weights.size + self.fc_head.bias.size

        return count

    def estimate_size_mb(self):
        """ประเมินขนาดโมเดล (MB)"""
        params = self.count_parameters()
        # Assume float32 (4 bytes per param)
        size_bytes = params * 4
        size_mb = size_bytes / (1024 * 1024)
        return size_mb


if __name__ == "__main__":
    print("🧠 NEXUS ULTRA Neural Core")
    print("=" * 50)

    model = NeuralCore()
    params = model.count_parameters()
    size_mb = model.estimate_size_mb()

    print(f"Total parameters: {params:,}")
    print(f"Estimated size: {size_mb:.2f} MB")
    print(f"Target size: 3.0 MB")
    print(f"Status: {'✅' if size_mb <= 3.5 else '⚠️'}")

    # Test forward pass
    print("\n📊 Testing forward pass...")
    frames = np.random.randn(1, 2, 128, 256).astype(np.float32)
    predictions, h, c = model.forward(frames, training=False)

    print(f"Input shape: {frames.shape}")
    print(f"Output shape: {predictions.shape}")
    print(f"Hidden state shape: {h.shape}")
    print(f"Cell state shape: {c.shape}")
    print("\n✅ Neural Core architecture ready!")
