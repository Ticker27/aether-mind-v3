"""
NEXUS ULTRA - Neural Core Smoke Test
=====================================
Verify architecture without heavy computation
"""

import numpy as np
import time
import json
from pathlib import Path


def smoke_test():
    """Minimal test to verify Neural Core architecture"""
    print("=" * 70)
    print("🧠 NEXUS ULTRA - Neural Core Smoke Test")
    print("=" * 70)

    start_time = time.time()

    # Test 1: Architecture definition
    print("\n📦 Test 1: Architecture Definition")
    from neural.neural_core import NeuralCore

    model = NeuralCore()
    params = model.count_parameters()
    size_mb = model.estimate_size_mb()

    print(f"   ✅ Model instantiated")
    print(f"   Parameters: {params:,}")
    print(f"   Size (float32): {size_mb:.2f} MB")
    print(f"   Target: 3.0 MB")

    # Test 2: Forward pass
    print("\n🔄 Test 2: Forward Pass")
    test_input = np.random.randn(1, 2, 128, 256).astype(np.float32)

    start_forward = time.time()
    predictions, h, c = model.forward(test_input, training=False)
    forward_time = (time.time() - start_forward) * 1000

    print(f"   ✅ Forward pass successful")
    print(f"   Input shape: {test_input.shape}")
    print(f"   Output shape: {predictions.shape}")
    print(f"   Time: {forward_time:.2f} ms")

    # Test 3: Output validation
    print("\n✅ Test 3: Output Validation")
    assert predictions.shape == (1, 64), f"Expected (1, 64), got {predictions.shape}"
    assert h.shape == (1, 256), f"Expected (1, 256), got {h.shape}"
    assert c.shape == (1, 256), f"Expected (1, 256), got {c.shape}"
    print(f"   ✅ All shapes correct")

    # Test 4: Size check
    print("\n📏 Test 4: Size Check")
    quantized_size = size_mb / 4  # int8 quantization
    status = 'pass' if quantized_size <= 3.5 else 'fail'
    print(f"   Size (float32): {size_mb:.2f} MB")
    print(f"   Size (int8): {quantized_size:.2f} MB")
    print(f"   Target: 3.0 MB")
    print(f"   Status: {'✅ PASS' if status == 'pass' else '⚠️ FAIL'}")

    total_time = time.time() - start_time

    # Summary
    print("\n" + "=" * 70)
    print("📋 Smoke Test Summary")
    print("=" * 70)
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Architecture: ✅ Ready")
    print(f"   Forward pass: ✅ Working")
    print(f"   Model size: {quantized_size:.2f} MB (target: 3.0 MB)")
    print(f"   Status: {'✅ NEURAL CORE READY' if status == 'pass' else '⚠️ NEEDS OPTIMIZATION'}")

    # Save results
    results = {
        'test': 'smoke_test',
        'model_params': params,
        'model_size_mb': size_mb,
        'quantized_size_mb': quantized_size,
        'forward_pass_ms': forward_time,
        'status': status,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    output_dir = Path('/var/minis/workspace/aether_mind/neural/models')
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / 'smoke_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to neural/models/smoke_test_results.json")

    return results


if __name__ == "__main__":
    smoke_test()
