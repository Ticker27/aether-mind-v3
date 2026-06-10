"""
NEXUS ULTRA - Architecture Parameter Calculator
=================================================
คำนวณ parameter count จาก architecture spec โดยตรง
ไม่ต้อง instantiate model (เร็วมาก)
"""

import time
import json
from pathlib import Path


def calc_conv_params(in_c, out_c, kernel_size):
    return out_c * in_c * kernel_size * kernel_size + out_c

def calc_bn_params(channels):
    return channels * 4  # gamma, beta, running_mean, running_var

def calc_dw_params(channels, kernel_size):
    return channels * 1 * kernel_size * kernel_size + channels

def calc_se_params(channels, reduction=4):
    fc1 = max(1, channels // reduction)
    return channels * fc1 + fc1 + channels * fc1 + channels

def calc_fc_params(in_f, out_f):
    return out_f * in_f + out_f


def verify_architecture():
    print("=" * 70)
    print("🧠 NEXUS ULTRA - Architecture Parameter Calculator")
    print("=" * 70)

    start = time.time()

    # === MobileNetV3-Small + LSTM Architecture ===

    total_params = 0

    # 1. Conv Stem: 2 input channels → 16
    stem = calc_conv_params(2, 16, 3) + calc_bn_params(16)
    total_params += stem
    print(f"\n📦 Conv Stem (2→16, 3×3):  {stem:,}")

    # 2. MobileNetV3 Blocks
    blocks = [
        # (in_c, exp_c, out_c, k, stride, se, act)
        (16, 16, 16, 3, 2, True, 'relu'),
        (16, 72, 24, 3, 2, False, 'relu'),
        (24, 88, 24, 3, 1, False, 'relu'),
        (24, 96, 40, 5, 2, True, 'hswish'),
        (40, 240, 40, 5, 1, True, 'hswish'),
        (40, 240, 40, 5, 1, True, 'hswish'),
        (40, 120, 48, 5, 1, True, 'hswish'),
        (48, 144, 48, 5, 1, True, 'hswish'),
        (48, 288, 96, 5, 2, True, 'hswish'),
        (96, 576, 96, 5, 1, True, 'hswish'),
        (96, 576, 96, 5, 1, True, 'hswish'),
    ]

    blocks_total = 0
    for i, (in_c, exp_c, out_c, k, stride, se, act) in enumerate(blocks):
        p = 0
        p += calc_conv_params(in_c, exp_c, 1) + calc_bn_params(exp_c)
        p += calc_dw_params(exp_c, k) + calc_bn_params(exp_c)
        if se:
            p += calc_se_params(exp_c)
        p += calc_conv_params(exp_c, out_c, 1) + calc_bn_params(out_c)
        blocks_total += p
        print(f"   Block {i+1:2d} ({in_c:3d}→{exp_c:3d}→{out_c:3d}, k={k}, s={stride}): {p:,}")

    total_params += blocks_total
    print(f"   {'─'*40}")
    print(f"   Blocks total: {blocks_total:,}")

    # 3. Final Conv: 96→512
    final_conv = calc_conv_params(96, 512, 1) + calc_bn_params(512)
    total_params += final_conv
    print(f"\n📦 Final Conv (96→512, 1×1): {final_conv:,}")

    # 4. LSTM: input=512, hidden=256
    # 4 gates × (hidden × (input + hidden) + hidden)
    lstm_hidden = 256
    lstm_input = 512
    lstm_gate = lstm_hidden * (lstm_input + lstm_hidden) + lstm_hidden
    lstm_total = lstm_gate * 4
    total_params += lstm_total
    print(f"📦 LSTM (512→256, 4 gates):  {lstm_total:,}")

    # 5. FC Head: 256→64
    fc_head = calc_fc_params(256, 64)
    total_params += fc_head
    print(f"📦 FC Head (256→64):         {fc_head:,}")

    # === Results ===
    print(f"\n{'='*70}")
    print(f"📊 TOTAL RESULTS")
    print(f"{'='*70}")

    size_f32 = total_params * 4 / (1024 * 1024)
    size_int8 = total_params * 1 / (1024 * 1024)
    target = 3.0

    print(f"   Total parameters:  {total_params:,}")
    print(f"   Size (float32):    {size_f32:.2f} MB")
    print(f"   Size (int8):       {size_int8:.2f} MB")
    print(f"   Target:            {target:.2f} MB")
    print(f"   Margin:            {target - size_int8:.2f} MB")

    status = 'pass' if size_int8 <= target else 'fail'
    print(f"   Status:            {'✅ PASS' if status == 'pass' else '⚠️ FAIL'}")

    # Architecture summary
    print(f"\n🏗️ Architecture Summary:")
    print(f"   Input:  2 frames (128×256 grayscale)")
    print(f"   Backbone: MobileNetV3-Small (11 blocks)")
    print(f"   Temporal: LSTM (256 hidden)")
    print(f"   Output: 64 values (16 balls × [x,y,vx,vy])")
    print(f"   Inference target: <2ms on NPU")

    elapsed = time.time() - start
    print(f"\n   Verification time: {elapsed*1000:.1f} ms")
    print(f"   {'✅ NEURAL CORE READY' if status == 'pass' else '⚠️ NEEDS OPTIMIZATION'}")

    # Save
    results = {
        'model': 'NEXUS_ULTRA_Neural_Core',
        'architecture': 'MobileNetV3-Small + LSTM',
        'total_params': total_params,
        'size_float32_mb': round(size_f32, 2),
        'size_int8_mb': round(size_int8, 2),
        'target_mb': target,
        'status': status,
        'blocks': len(blocks),
        'lstm_hidden': lstm_hidden,
        'output_values': 64,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    out = Path('/var/minis/workspace/aether_mind/neural/models')
    out.mkdir(parents=True, exist_ok=True)
    with open(out / 'architecture_verification.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Saved to neural/models/architecture_verification.json")
    return results


if __name__ == "__main__":
    verify_architecture()
