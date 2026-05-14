"""
GPU Setup Verification Script
==============================
Run this FIRST to make sure your GPU + TensorFlow is working.
    python check_gpu.py
"""

import sys
print("=" * 50)
print("  GPU & TensorFlow Verification")
print("=" * 50)

# Python version
print(f"\n🐍 Python : {sys.version.split()[0]}")

# TensorFlow
try:
    import tensorflow as tf
    print(f"✅ TensorFlow : {tf.__version__}")

    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"✅ GPU detected: {len(gpus)} device(s)")
        for i, gpu in enumerate(gpus):
            print(f"   GPU {i}: {gpu.name}")

        # Enable memory growth
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

        # Quick compute test
        import time
        a = tf.random.normal([1000, 1000])
        b = tf.random.normal([1000, 1000])
        start = time.time()
        c = tf.matmul(a, b)
        _ = c.numpy()
        elapsed = time.time() - start
        print(f"✅ GPU compute test: {elapsed*1000:.1f}ms (matrix multiply 1000x1000)")

        # Check mixed precision support
        gpu_name = gpus[0].name.lower()
        if any(x in gpu_name for x in ['rtx', '30', '40', '20']):
            print("✅ RTX GPU detected — mixed_float16 precision supported (faster training!)")
        else:
            print("ℹ️  GTX GPU — float32 precision will be used")

    else:
        print("⚠️  No GPU detected by TensorFlow!")
        print("\nPossible fixes:")
        print("1. Install CUDA 11.8 from https://developer.nvidia.com/cuda-11-8-0-download-archive")
        print("2. Install cuDNN 8.6 from https://developer.nvidia.com/cudnn")
        print("3. Reinstall TensorFlow: pip install tensorflow==2.13.0")
        print("4. Restart your PC after CUDA install")

except ImportError:
    print("❌ TensorFlow NOT installed!")
    print("   Run: pip install tensorflow==2.13.0")

# Other libraries
print("\n📦 Other Libraries:")
libs = {
    "numpy":      "numpy",
    "opencv":     "cv2",
    "matplotlib": "matplotlib",
    "sklearn":    "sklearn",
    "seaborn":    "seaborn",
    "PIL":        "PIL",
    "flask":      "flask",
}

for name, module in libs.items():
    try:
        m = __import__(module)
        ver = getattr(m, '__version__', '✓')
        print(f"   ✅ {name:<12}: {ver}")
    except ImportError:
        print(f"   ❌ {name:<12}: NOT installed  →  pip install {name}")

print("\n" + "="*50)
print("  If all ✅ — you're ready to train!")
print("  Run: python prepare_dataset.py")
print("  Then: python train_soil_model.py")
print("  Then: python train_leaf_model.py")
print("="*50)